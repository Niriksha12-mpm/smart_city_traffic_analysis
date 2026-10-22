"""
Data Ingestion and Loading Module for Smart City Traffic Analytics.
"""

import os
from pathlib import Path
from typing import Dict, Any, Tuple, Optional
import pandas as pd
from src.config import RAW_DATA_PATH, MANDATORY_COLUMNS

def get_file_metadata(file_path: str | Path) -> Dict[str, Any]:
    """Retrieve metadata about the raw dataset file."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Traffic dataset not found at: {path.resolve()}")
    
    file_size_bytes = os.path.getsize(path)
    file_size_mb = round(file_size_bytes / (1024 * 1024), 2)
    
    # Read sample to inspect columns without loading full file
    sample_df = pd.read_csv(path, nrows=5)
    
    return {
        "file_path": str(path.resolve()),
        "file_name": path.name,
        "file_size_mb": file_size_mb,
        "sample_columns": list(sample_df.columns),
        "is_synthetic": True,
        "data_source_note": "Realistic synthetic sensor network data calibrated to smart city arterial dynamics."
    }

def load_raw_traffic_data(file_path: Optional[str | Path] = None) -> pd.DataFrame:
    """
    Load raw traffic observations from CSV.
    
    Args:
        file_path: Path to raw CSV. Defaults to RAW_DATA_PATH.
        
    Returns:
        pd.DataFrame containing raw sensor observations.
    """
    path = Path(file_path) if file_path else RAW_DATA_PATH
    if not path.exists():
        raise FileNotFoundError(f"Dataset file does not exist: {path.resolve()}")
    
    df = pd.read_csv(path)
    return df

def validate_raw_schema(df: pd.DataFrame) -> Tuple[bool, list]:
    """
    Validate that mandatory columns are present in the ingested dataframe.
    
    Returns:
        (is_valid: bool, missing_columns: list)
    """
    missing = [col for col in MANDATORY_COLUMNS if col not in df.columns]
    return (len(missing) == 0, missing)
