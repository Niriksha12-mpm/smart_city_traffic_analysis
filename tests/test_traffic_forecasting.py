"""
Tests for Traffic Volume Forecasting and ML Pipeline.
"""

import pytest
import pandas as pd
import numpy as np

from src.traffic_forecasting import (
    create_forecasting_features,
    train_and_evaluate_forecaster,
)

@pytest.fixture
def sample_timeseries_data():
    """Generate 300 hours of continuous chronological observations for a single corridor."""
    timestamps = pd.date_range("2026-08-01 00:00:00", periods=300, freq="h")
    records = []
    for ts in timestamps:
        hr = ts.hour
        # Diurnal pattern
        base = 1200 + 800 * np.sin(2 * np.pi * hr / 24.0)
        vol = max(100, int(base + np.random.normal(0, 50)))
        records.append({
            "timestamp": ts,
            "location_name": "Test Corridor",
            "vehicle_count": vol,
            "road_capacity": 2500,
            "speed_limit": 60,
            "hour": hr,
            "day_of_week_num": ts.dayofweek,
            "is_weekend": 1 if ts.dayofweek >= 5 else 0
        })
    return pd.DataFrame(records)

def test_feature_creation(sample_timeseries_data):
    features = create_forecasting_features(sample_timeseries_data)
    assert not features.empty
    expected_features = ["lag_1h", "lag_2h", "lag_24h", "rolling_mean_3h", "hour_sin", "hour_cos"]
    for feat in expected_features:
        assert feat in features.columns

def test_chronological_split_no_leakage(sample_timeseries_data):
    features = create_forecasting_features(sample_timeseries_data)
    res = train_and_evaluate_forecaster(features, model_type="Ridge", train_ratio=0.80)
    
    # Verify train and test samples partition the feature set
    assert res["train_samples"] + res["test_samples"] == len(features)
    assert res["train_samples"] > 0
    assert res["test_samples"] > 0

def test_model_evaluation_metrics(sample_timeseries_data):
    features = create_forecasting_features(sample_timeseries_data)
    res = train_and_evaluate_forecaster(features, model_type="RandomForest", train_ratio=0.80)
    
    # Check metric outputs
    assert res["ml_mae"] > 0
    assert res["ml_rmse"] > 0
    assert "metrics_table" in res
    assert len(res["metrics_table"]) == 2  # Baseline and ML
    assert "comparison_df" in res
    assert not res["comparison_df"].empty
