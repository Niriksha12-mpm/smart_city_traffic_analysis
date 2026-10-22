"""
Tests for PySpark Big Data Processing Engine.
"""

import pytest
import os
import pandas as pd

from src.spark_processor import SparkTrafficProcessor, PYSPARK_AVAILABLE

@pytest.mark.skipif(not PYSPARK_AVAILABLE, reason="PySpark not available")
def test_spark_processor_lifecycle():
    processor = SparkTrafficProcessor()
    spark = processor.get_spark_session()
    assert spark is not None
    assert processor.get_spark_session() is spark  # Singleton check

    meta = processor.get_spark_engine_metadata()
    assert "spark_version" in meta
    assert meta["app_name"] == "SmartCityTrafficAnalytics"

@pytest.mark.skipif(not PYSPARK_AVAILABLE, reason="PySpark not available")
def test_spark_dataframe_aggregations(tmp_path):
    # Create mini temporary CSV
    csv_file = tmp_path / "mini_traffic.csv"
    data = [
        "timestamp,location_id,location_name,latitude,longitude,vehicle_count,average_speed,road_capacity,speed_limit,weather_condition,incident_flag",
        "2026-08-01 08:00:00,LOC_01,Corridor Alpha,12.93,77.69,2100,35.0,2500,60,Clear,0",
        "2026-08-01 09:00:00,LOC_01,Corridor Alpha,12.93,77.69,2400,28.0,2500,60,Clear,0",
        "2026-08-01 14:00:00,LOC_02,Corridor Beta,12.97,77.60,900,48.0,2000,50,Clear,0"
    ]
    csv_file.write_text("\n".join(data), encoding="utf-8")

    processor = SparkTrafficProcessor()
    sdf = processor.load_traffic_spark_df(str(csv_file))
    assert sdf.count() == 3

    # Test Spark location ranking
    ranking_pdf = processor.compute_location_congestion_ranking(sdf)
    assert len(ranking_pdf) == 2
    assert "congestion_rank" in ranking_pdf.columns
    assert ranking_pdf["congestion_rank"].min() == 1

    # Test Spark hourly matrix
    matrix_pdf = processor.compute_hourly_location_matrix(sdf)
    assert not matrix_pdf.empty
    assert "avg_volume" in matrix_pdf.columns
