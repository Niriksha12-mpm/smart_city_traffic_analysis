"""
Traffic Volume Forecasting Pipeline.

Implements chronological time-series feature engineering, baseline comparisons,
scikit-learn regression models, and leakage-free evaluation.
"""

from typing import Dict, Any, Tuple, Optional, List
import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from src.config import FORECAST_TRAIN_RATIO

def create_forecasting_features(df: pd.DataFrame, location_name: Optional[str] = None) -> pd.DataFrame:
    """
    Generate chronological lag and temporal features for a single location or network slice.
    Strictly orders by timestamp to avoid lookahead data leakage.
    """
    if location_name and "location_name" in df.columns:
        sub_df = df[df["location_name"] == location_name].copy()
    else:
        sub_df = df.copy()

    # Ensure strictly sorted by timestamp
    sub_df = sub_df.sort_values("timestamp").reset_index(drop=True)

    # 1. Target variable
    target = "vehicle_count"

    # 2. Lag features
    sub_df["lag_1h"] = sub_df[target].shift(1)
    sub_df["lag_2h"] = sub_df[target].shift(2)
    sub_df["lag_3h"] = sub_df[target].shift(3)
    sub_df["lag_24h"] = sub_df[target].shift(24)
    # 168 hours = 1 week
    if len(sub_df) >= 300:
        sub_df["lag_168h"] = sub_df[target].shift(168)
    else:
        sub_df["lag_168h"] = sub_df["lag_24h"]

    # 3. Rolling window features (computed on historical lag 1 to prevent leakage)
    sub_df["rolling_mean_3h"] = sub_df["lag_1h"].rolling(window=3, min_periods=1).mean()
    sub_df["rolling_mean_6h"] = sub_df["lag_1h"].rolling(window=6, min_periods=1).mean()

    # 4. Cyclical temporal transforms (hour)
    sub_df["hour_sin"] = np.sin(2 * np.pi * sub_df["hour"] / 24.0)
    sub_df["hour_cos"] = np.cos(2 * np.pi * sub_df["hour"] / 24.0)

    # 5. Drop initial warm-up rows containing NaNs from lagging
    feature_df = sub_df.dropna().reset_index(drop=True)
    return feature_df

def train_and_evaluate_forecaster(
    feature_df: pd.DataFrame,
    model_type: str = "RandomForest",
    train_ratio: float = FORECAST_TRAIN_RATIO
) -> Dict[str, Any]:
    """
    Train traffic volume forecasting model and evaluate against a baseline
    using a strictly chronological train/test split.
    """
    if len(feature_df) < 25:
        raise ValueError("Insufficient observations for reliable forecasting (< 25 rows).")

    # Chronological split point
    split_idx = int(len(feature_df) * train_ratio)
    train_df = feature_df.iloc[:split_idx].copy()
    test_df = feature_df.iloc[split_idx:].copy()

    feature_cols = [
        "lag_1h", "lag_2h", "lag_3h", "lag_24h", "lag_168h",
        "rolling_mean_3h", "rolling_mean_6h",
        "hour_sin", "hour_cos", "day_of_week_num", "is_weekend"
    ]
    if "road_capacity" in feature_df.columns:
        feature_cols.append("road_capacity")

    X_train = train_df[feature_cols]
    y_train = train_df["vehicle_count"]

    X_test = test_df[feature_cols]
    y_test = test_df["vehicle_count"]

    # --- 1. Baseline Model (Same Hour Previous Day: lag_24h) ---
    baseline_preds = test_df["lag_24h"].values
    baseline_mae = mean_absolute_error(y_test, baseline_preds)
    baseline_rmse = np.sqrt(mean_squared_error(y_test, baseline_preds))
    baseline_mape = np.mean(np.abs((y_test.values - baseline_preds) / (y_test.values + 1e-6))) * 100
    baseline_r2 = r2_score(y_test, baseline_preds)

    # --- 2. Machine Learning Model ---
    if model_type == "Ridge":
        model = Ridge(alpha=1.0)
    else:
        # RandomForest with conservative trees for fast, stable training
        model = RandomForestRegressor(
            n_estimators=60,
            max_depth=12,
            min_samples_split=4,
            random_state=42,
            n_jobs=-1
        )

    model.fit(X_train, y_train)
    ml_preds = model.predict(X_test)
    ml_preds = np.clip(ml_preds, 0, None)  # Traffic count cannot be negative

    ml_mae = mean_absolute_error(y_test, ml_preds)
    ml_rmse = np.sqrt(mean_squared_error(y_test, ml_preds))
    ml_mape = np.mean(np.abs((y_test.values - ml_preds) / (y_test.values + 1e-6))) * 100
    ml_r2 = r2_score(y_test, ml_preds)

    mae_improvement_pct = round(((baseline_mae - ml_mae) / (baseline_mae + 1e-6)) * 100, 1)

    # Compile Evaluation Comparison Table
    metrics_comparison = pd.DataFrame([
        {
            "Model": "Baseline (Lag-24h Persist)",
            "MAE (veh/hr)": round(baseline_mae, 1),
            "RMSE (veh/hr)": round(baseline_rmse, 1),
            "MAPE (%)": round(baseline_mape, 1),
            "R² Score": round(baseline_r2, 3)
        },
        {
            "Model": f"ML ({model_type})",
            "MAE (veh/hr)": round(ml_mae, 1),
            "RMSE (veh/hr)": round(ml_rmse, 1),
            "MAPE (%)": round(ml_mape, 1),
            "R² Score": round(ml_r2, 3)
        }
    ])

    # Result dataframe for visual comparison
    comparison_df = test_df[["timestamp", "hour", "vehicle_count"]].copy()
    comparison_df["actual"] = y_test.values
    comparison_df["baseline_pred"] = np.round(baseline_preds, 0)
    comparison_df["ml_pred"] = np.round(ml_preds, 0)
    comparison_df["residual_error"] = np.round(comparison_df["actual"] - comparison_df["ml_pred"], 1)

    # Feature Importance if available
    feature_importance = None
    if hasattr(model, "feature_importances_"):
        feature_importance = pd.DataFrame({
            "feature": feature_cols,
            "importance": model.feature_importances_
        }).sort_values(by="importance", ascending=False).reset_index(drop=True)

    return {
        "model_type": model_type,
        "train_samples": len(train_df),
        "test_samples": len(test_df),
        "metrics_table": metrics_comparison,
        "mae_improvement_pct": mae_improvement_pct,
        "ml_mae": round(ml_mae, 1),
        "ml_rmse": round(ml_rmse, 1),
        "ml_r2": round(ml_r2, 3),
        "comparison_df": comparison_df,
        "feature_importance": feature_importance,
        "train_date_range": f"{train_df['timestamp'].min()} to {train_df['timestamp'].max()}",
        "test_date_range": f"{test_df['timestamp'].min()} to {test_df['timestamp'].max()}",
    }
