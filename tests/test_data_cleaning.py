"""
Tests for Data Cleaning and Feature Engineering Module.
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from src.data_cleaning import clean_traffic_data, assign_time_period, categorize_congestion

@pytest.fixture
def sample_raw_data():
    """Create a controlled raw dataframe with duplicates, missing values, and outliers."""
    base_time = datetime(2026, 8, 1, 8, 0, 0)
    data = [
        # Normal row
        {"timestamp": (base_time).strftime("%Y-%m-%d %H:%M:%S"), "location_id": "LOC_01", "location_name": "Corridor A", "vehicle_count": 1000, "average_speed": 50.0, "road_capacity": 2000, "speed_limit": 60},
        # Duplicate row
        {"timestamp": (base_time).strftime("%Y-%m-%d %H:%M:%S"), "location_id": "LOC_01", "location_name": "Corridor A", "vehicle_count": 1000, "average_speed": 50.0, "road_capacity": 2000, "speed_limit": 60},
        # Missing speed & negative count
        {"timestamp": (base_time + timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S"), "location_id": "LOC_01", "location_name": "Corridor A", "vehicle_count": -50, "average_speed": np.nan, "road_capacity": 2000, "speed_limit": 60},
        # Outlier speed (negative and extreme)
        {"timestamp": (base_time + timedelta(hours=2)).strftime("%Y-%m-%d %H:%M:%S"), "location_id": "LOC_01", "location_name": "Corridor A", "vehicle_count": 1200, "average_speed": -10.0, "road_capacity": 2000, "speed_limit": 60},
        {"timestamp": (base_time + timedelta(hours=3)).strftime("%Y-%m-%d %H:%M:%S"), "location_id": "LOC_01", "location_name": "Corridor A", "vehicle_count": 1300, "average_speed": 350.0, "road_capacity": 2000, "speed_limit": 60},
        # Weekend row
        {"timestamp": "2026-08-02 14:00:00", "location_id": "LOC_01", "location_name": "Corridor A", "vehicle_count": 800, "average_speed": 55.0, "road_capacity": 2000, "speed_limit": 60},
    ]
    return pd.DataFrame(data)

def test_deduplication(sample_raw_data):
    cleaned, report = clean_traffic_data(sample_raw_data)
    assert report["duplicates_removed"] == 1
    assert len(cleaned) == 5

def test_anomaly_remediation(sample_raw_data):
    cleaned, report = clean_traffic_data(sample_raw_data)
    # Impossible speeds should be clipped and imputed within legal range (1 - 160 km/h)
    assert (cleaned["average_speed"] >= 1.0).all()
    assert (cleaned["average_speed"] <= 160.0).all()
    # Vehicle count should be >= 0
    assert (cleaned["vehicle_count"] >= 0).all()
    assert report["anomalous_speeds_clipped"] >= 2
    assert report["anomalous_counts_clipped"] >= 1

def test_derived_features(sample_raw_data):
    cleaned, _ = clean_traffic_data(sample_raw_data)
    expected_cols = [
        "hour", "date", "day_of_week", "day_of_week_num", "is_weekend",
        "month", "time_period", "volume_capacity_ratio", "speed_performance_index", "congestion_level"
    ]
    for col in expected_cols:
        assert col in cleaned.columns, f"Missing derived column: {col}"

    # Saturday/Sunday check
    weekend_rows = cleaned[cleaned["timestamp"].dt.strftime("%Y-%m-%d") == "2026-08-02"]
    assert (weekend_rows["is_weekend"] == 1).all()

def test_time_period_assignment():
    assert assign_time_period(8) == "Morning Peak"
    assert assign_time_period(13) == "Midday Off-Peak"
    assert assign_time_period(18) == "Evening Peak"
    assert assign_time_period(23) == "Night Off-Peak"
    assert assign_time_period(3) == "Night Off-Peak"

def test_congestion_categorization():
    assert categorize_congestion(0.40) == "Low"
    assert categorize_congestion(0.70) == "Moderate"
    assert categorize_congestion(0.90) == "Heavy"
    assert categorize_congestion(1.15) == "Severe"
