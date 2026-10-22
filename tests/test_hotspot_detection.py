"""
Tests for Congestion Hotspot Detection and Ranking Module.
"""

import pytest
import pandas as pd
import numpy as np

from src.hotspot_detection import calculate_hotspot_scores, get_top_hotspots

@pytest.fixture
def sample_multi_corridor_data():
    """Create sample data with two distinct corridors: one congested chokepoint and one free-flow highway."""
    records = []
    for hr in range(24):
        # Chokepoint: High volume, low speed, severe congestion
        records.append({
            "location_id": "LOC_CHOKE",
            "location_name": "Chokepoint Junction",
            "latitude": 12.91,
            "longitude": 77.61,
            "vehicle_count": 2800,
            "average_speed": 18.0,
            "road_capacity": 2500,
            "speed_limit": 60,
            "hour": hr,
            "time_period": "Evening Peak" if 16 <= hr <= 20 else "Midday",
            "volume_capacity_ratio": 2800 / 2500,  # 1.12
            "speed_performance_index": 18.0 / 60,
            "congestion_level": "Severe"
        })
        # Highway: Low volume, high speed, smooth flow
        records.append({
            "location_id": "LOC_HWY",
            "location_name": "Freeflow Highway",
            "latitude": 13.04,
            "longitude": 77.58,
            "vehicle_count": 1000,
            "average_speed": 75.0,
            "road_capacity": 4000,
            "speed_limit": 80,
            "hour": hr,
            "time_period": "Evening Peak" if 16 <= hr <= 20 else "Midday",
            "volume_capacity_ratio": 1000 / 4000,  # 0.25
            "speed_performance_index": 75.0 / 80,
            "congestion_level": "Low"
        })
    return pd.DataFrame(records)

def test_hotspot_scoring_logic(sample_multi_corridor_data):
    scores = calculate_hotspot_scores(sample_multi_corridor_data)
    assert len(scores) == 2
    
    # Chokepoint must have higher CHI score than highway
    choke_score = scores[scores["location_id"] == "LOC_CHOKE"]["chi_score"].iloc[0]
    hwy_score = scores[scores["location_id"] == "LOC_HWY"]["chi_score"].iloc[0]
    
    assert choke_score > hwy_score
    # CHI scores must be bounded within [0, 100]
    assert 0.0 <= choke_score <= 100.0
    assert 0.0 <= hwy_score <= 100.0

def test_hotspot_ranking_order(sample_multi_corridor_data):
    top = get_top_hotspots(sample_multi_corridor_data, top_n=10)
    # Rank 1 must be the chokepoint
    assert top.iloc[0]["location_id"] == "LOC_CHOKE"
    assert top.iloc[0]["rank"] == 1
    assert top.iloc[0]["severity"] in ["Critical Bottleneck", "High Congestion"]

def test_hotspot_empty_dataframe():
    empty_df = pd.DataFrame()
    res = calculate_hotspot_scores(empty_df)
    assert res.empty
