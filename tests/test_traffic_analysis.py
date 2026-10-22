"""
Tests for Traffic Pattern & Peak-Hour Analytics Module.
"""

import pytest
import pandas as pd
import numpy as np

from src.traffic_analysis import (
    compute_network_kpis,
    analyze_peak_hours,
    compare_weekday_weekend,
    generate_traffic_insights,
)

@pytest.fixture
def sample_cleaned_data():
    """Create a sample cleaned dataframe spanning 48 hours for testing."""
    records = []
    # 2 days: 1 weekday, 1 weekend
    dates = [
        pd.date_range("2026-08-03 00:00:00", "2026-08-03 23:00:00", freq="h"),  # Monday (Weekday)
        pd.date_range("2026-08-08 00:00:00", "2026-08-08 23:00:00", freq="h")   # Saturday (Weekend)
    ]
    for date_series in dates:
        for ts in date_series:
            hr = ts.hour
            is_wknd = 1 if ts.dayofweek >= 5 else 0
            # Rush hour surges at 9 AM and 18 PM
            vol = 2200 if hr in [8, 9, 17, 18] else 800
            speed = 25.0 if hr in [8, 9, 17, 18] else 55.0
            cap = 2000
            records.append({
                "timestamp": ts,
                "location_id": "LOC_01",
                "location_name": "Test Corridor",
                "latitude": 12.97,
                "longitude": 77.59,
                "vehicle_count": vol,
                "average_speed": speed,
                "road_capacity": cap,
                "speed_limit": 60,
                "hour": hr,
                "date": ts.date(),
                "day_of_week": ts.day_name(),
                "day_of_week_num": ts.dayofweek,
                "is_weekend": is_wknd,
                "month": ts.month,
                "time_period": "Evening Peak" if 16 <= hr <= 20 else "Midday Off-Peak",
                "volume_capacity_ratio": vol / cap,
                "speed_performance_index": speed / 60,
                "congestion_level": "Severe" if (vol / cap) >= 1.0 else "Low"
            })
    return pd.DataFrame(records)

def test_compute_network_kpis(sample_cleaned_data):
    kpis = compute_network_kpis(sample_cleaned_data)
    assert kpis["total_records"] == 48
    assert kpis["total_volume"] > 0
    assert 20.0 < kpis["avg_speed"] < 60.0
    assert kpis["active_corridors"] == 1
    assert kpis["peak_congestion_rate"] > 0

def test_analyze_peak_hours(sample_cleaned_data):
    peaks = analyze_peak_hours(sample_cleaned_data)
    assert "hourly_summary" in peaks
    assert len(peaks["hourly_summary"]) == 24
    assert peaks["busiest_hour"] in [8, 9, 17, 18]
    assert peaks["slowest_hour"] in [8, 9, 17, 18]

def test_compare_weekday_weekend(sample_cleaned_data):
    ww = compare_weekday_weekend(sample_cleaned_data)
    assert "weekday_avg_volume" in ww
    assert "weekend_avg_volume" in ww
    assert "daily_breakdown" in ww
    assert len(ww["daily_breakdown"]) == 2

def test_generate_traffic_insights(sample_cleaned_data):
    insights = generate_traffic_insights(sample_cleaned_data)
    assert len(insights) >= 3
    assert any("Network-Wide Flow" in ins for ins in insights)

def test_empty_dataframe_handling():
    empty_df = pd.DataFrame()
    kpis = compute_network_kpis(empty_df)
    assert kpis["total_volume"] == 0
    insights = generate_traffic_insights(empty_df)
    assert "No data available" in insights[0]
