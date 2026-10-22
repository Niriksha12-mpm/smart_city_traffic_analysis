"""
Data Cleaning, Validation, and Feature Engineering Pipeline.
"""

from typing import Tuple, Dict, Any
import numpy as np
import pandas as pd

from src.config import (
    MANDATORY_COLUMNS,
    NUMERIC_COLUMNS,
    MIN_SPEED_KMH,
    MAX_SPEED_KMH,
    MIN_VEHICLE_COUNT,
    MAX_CAPACITY_FACTOR,
    TIME_PERIODS,
    VC_THRESHOLDS,
)

def assign_time_period(hour: int) -> str:
    """Categorize an hour (0-23) into standard smart city diurnal periods."""
    if 7 <= hour <= 10:
        return "Morning Peak"
    elif 11 <= hour <= 15:
        return "Midday Off-Peak"
    elif 16 <= hour <= 20:
        return "Evening Peak"
    else:
        return "Night Off-Peak"

def categorize_congestion(vc_ratio: float) -> str:
    """Classify volume-to-capacity ratio into congestion severity levels."""
    if pd.isna(vc_ratio):
        return "Unknown"
    if vc_ratio < 0.60:
        return "Low"
    elif vc_ratio < 0.85:
        return "Moderate"
    elif vc_ratio < 1.00:
        return "Heavy"
    else:
        return "Severe"

def clean_traffic_data(raw_df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Perform comprehensive data cleaning, anomaly remediation, and feature engineering.
    
    Args:
        raw_df: Raw ingested pandas DataFrame.
        
    Returns:
        (cleaned_df, audit_report)
    """
    report = {
        "raw_record_count": len(raw_df),
        "duplicates_removed": 0,
        "invalid_timestamps": 0,
        "missing_speed_imputed": 0,
        "missing_count_imputed": 0,
        "anomalous_speeds_clipped": 0,
        "anomalous_counts_clipped": 0,
        "cleaned_record_count": 0,
    }
    
    df = raw_df.copy()

    # 1. Deduplication based on primary temporal-spatial key
    dedup_cols = ["timestamp", "location_id"] if "location_id" in df.columns else ["timestamp", "location_name"]
    initial_len = len(df)
    df = df.drop_duplicates(subset=dedup_cols, keep="first")
    report["duplicates_removed"] = initial_len - len(df)

    # 2. Timestamp standardization & validation
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    invalid_ts_count = int(df["timestamp"].isna().sum())
    report["invalid_timestamps"] = invalid_ts_count
    if invalid_ts_count > 0:
        df = df.dropna(subset=["timestamp"])

    # 3. Sort chronologically per location
    sort_key = ["location_id", "timestamp"] if "location_id" in df.columns else ["location_name", "timestamp"]
    df = df.sort_values(by=sort_key).reset_index(drop=True)

    # 4. Handle numeric anomalies (negative values, physically impossible speeds)
    # Average Speed: Check negative or excessive values
    speed_anomalies = (df["average_speed"] < MIN_SPEED_KMH) | (df["average_speed"] > MAX_SPEED_KMH)
    report["anomalous_speeds_clipped"] = int(speed_anomalies.sum())
    df.loc[speed_anomalies, "average_speed"] = np.nan

    # Vehicle Count: Check negative counts or counts > MAX_CAPACITY_FACTOR * capacity
    if "road_capacity" in df.columns:
        max_allowed_count = df["road_capacity"] * MAX_CAPACITY_FACTOR
        count_anomalies = (df["vehicle_count"] < MIN_VEHICLE_COUNT) | (df["vehicle_count"] > max_allowed_count)
    else:
        count_anomalies = df["vehicle_count"] < MIN_VEHICLE_COUNT
    report["anomalous_counts_clipped"] = int(count_anomalies.sum())
    df.loc[count_anomalies, "vehicle_count"] = np.nan

    # 5. Missing value imputation
    # Impute missing speed using location-specific median by hour of day
    report["missing_speed_imputed"] = int(df["average_speed"].isna().sum())
    report["missing_count_imputed"] = int(df["vehicle_count"].isna().sum())

    df["hour_temp"] = df["timestamp"].dt.hour
    
    # Impute vehicle_count per location and hour
    df["vehicle_count"] = df.groupby(["location_name", "hour_temp"])["vehicle_count"].transform(
        lambda s: s.ffill().bfill()
    )
    # Global fallback if any remain
    df["vehicle_count"] = df["vehicle_count"].fillna(df["vehicle_count"].median()).round().astype(int)

    # Impute average_speed per location and hour
    df["average_speed"] = df.groupby(["location_name", "hour_temp"])["average_speed"].transform(
        lambda s: s.ffill().bfill()
    )
    # Global fallback if any remain
    df["average_speed"] = df["average_speed"].fillna(df["average_speed"].median()).round(1)

    df = df.drop(columns=["hour_temp"])

    # 6. Feature Engineering
    df["hour"] = df["timestamp"].dt.hour
    df["date"] = df["timestamp"].dt.date
    df["date_str"] = df["timestamp"].dt.strftime("%Y-%m-%d")
    df["day_of_week"] = df["timestamp"].dt.day_name()
    df["day_of_week_num"] = df["timestamp"].dt.dayofweek  # 0=Monday, 6=Sunday
    df["is_weekend"] = df["day_of_week_num"].apply(lambda d: 1 if d >= 5 else 0)
    df["month"] = df["timestamp"].dt.month
    df["month_name"] = df["timestamp"].dt.month_name()
    
    # Diurnal time period
    df["time_period"] = df["hour"].apply(assign_time_period)

    # Traffic ratios
    if "road_capacity" in df.columns:
        df["volume_capacity_ratio"] = (df["vehicle_count"] / df["road_capacity"]).round(3)
    else:
        df["volume_capacity_ratio"] = 0.5

    if "speed_limit" in df.columns:
        df["speed_performance_index"] = (df["average_speed"] / df["speed_limit"]).round(3)
    else:
        df["speed_performance_index"] = 0.8

    # Congestion classification
    df["congestion_level"] = df["volume_capacity_ratio"].apply(categorize_congestion)

    # Final cleanup & report
    report["cleaned_record_count"] = len(df)
    
    return df, report
