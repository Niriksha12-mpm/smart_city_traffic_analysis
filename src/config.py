"""
Global Configuration and Settings for Smart City Traffic Analytics.
"""

import os
import sys
from pathlib import Path

# Paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_PATH = DATA_DIR / "traffic_data.csv"
CLEANED_DATA_PATH = DATA_DIR / "cleaned_traffic_data.parquet"
EXPORT_CLEANED_CSV = DATA_DIR / "cleaned_traffic_data.csv"

# Ensure data dir exists
os.makedirs(DATA_DIR, exist_ok=True)

# Java & PySpark Environment Setup for Windows & Linux
def configure_environment():
    """Ensure JAVA_HOME, PATH, and PySpark Python bindings are correctly configured."""
    # Ensure current python executable is used by PySpark workers
    os.environ["PYSPARK_PYTHON"] = sys.executable
    os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable

    # Detect JAVA_HOME if not already set or invalid
    java_home = os.environ.get("JAVA_HOME")
    candidate_jdk_dirs = [
        r"C:\Program Files\Microsoft\jdk-17.0.20.101-hotspot",
        r"C:\Program Files\Eclipse Adoptium\jdk-17",
        r"C:\Program Files\Java\jdk-17",
        r"C:\Program Files\Java\jdk-11",
        r"C:\Program Files\Java\jdk1.8.0",
    ]
    if not java_home or not os.path.exists(java_home):
        for candidate in candidate_jdk_dirs:
            if os.path.exists(candidate):
                os.environ["JAVA_HOME"] = candidate
                bin_dir = os.path.join(candidate, "bin")
                if bin_dir not in os.environ.get("PATH", ""):
                    os.environ["PATH"] = bin_dir + os.pathsep + os.environ.get("PATH", "")
                break

configure_environment()

# Spark Configurations
SPARK_APP_NAME = "SmartCityTrafficAnalytics"
SPARK_MASTER = "local[*]"
SPARK_DRIVER_MEMORY = "2g"
SPARK_SHUFFLE_PARTITIONS = "4"

# Schema Specifications
MANDATORY_COLUMNS = [
    "timestamp",
    "location_id",
    "location_name",
    "latitude",
    "longitude",
    "vehicle_count",
    "average_speed",
    "road_capacity",
    "speed_limit",
]

NUMERIC_COLUMNS = [
    "latitude",
    "longitude",
    "vehicle_count",
    "average_speed",
    "road_capacity",
    "speed_limit",
]

# Physical and Boundary Constraints
MIN_SPEED_KMH = 1.0
MAX_SPEED_KMH = 160.0
MIN_VEHICLE_COUNT = 0
MAX_CAPACITY_FACTOR = 2.5  # Max vehicle count cannot exceed 2.5x physical capacity

# Peak-Hour Windows (Hours in 24h clock)
TIME_PERIODS = {
    "Morning Peak": (7, 10),      # 7:00 AM - 10:59 AM
    "Midday Off-Peak": (11, 15),  # 11:00 AM - 3:59 PM
    "Evening Peak": (16, 20),     # 4:00 PM - 8:59 PM
    "Night Off-Peak": (21, 6),    # 9:00 PM - 6:59 AM
}

# Congestion Thresholds (Volume / Capacity Ratio)
VC_THRESHOLDS = {
    "Low": 0.60,
    "Moderate": 0.85,
    "Heavy": 1.00,
    "Severe": float("inf"),
}

# Speed Performance Index Thresholds (Speed / Speed Limit)
SPI_THRESHOLDS = {
    "Smooth": 0.75,
    "Mild Delay": 0.50,
    "Heavy Congestion": 0.25,
    "Gridlock": 0.0,
}

# Hotspot Scoring Formula Weights
# CHI = w1 * (Normalized V/C) + w2 * (Speed Deficit) + w3 * (Severe Congestion Frequency) + w4 * (Speed Volatility)
HOTSPOT_WEIGHTS = {
    "vc_ratio": 0.35,
    "speed_drop": 0.35,
    "severe_frequency": 0.20,
    "speed_volatility": 0.10,
}

# Machine Learning Forecasting Parameters
FORECAST_TRAIN_RATIO = 0.80  # Chronological split: 80% train, 20% test
FORECAST_LAG_HOURS = [1, 2, 3, 24, 168]  # Lags: 1h, 2h, 3h, 24h (same hour yesterday), 168h (same hour last week)
FORECAST_ROLLING_WINDOWS = [3, 6]  # 3-hour and 6-hour moving averages
