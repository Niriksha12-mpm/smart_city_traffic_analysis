"""
Congestion Hotspot Detection and Ranking Module.

Calculates multi-criteria Congestion Hotspot Index (CHI) scores, ranks top bottleneck
corridors, and provides data-driven capacity-speed diagnostics.
"""

from typing import Dict, Any, List
import numpy as np
import pandas as pd
from src.config import HOTSPOT_WEIGHTS

def calculate_hotspot_scores(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute multi-factor Congestion Hotspot Index (CHI) for each monitored corridor.
    
    Formula:
        CHI = [ w1 * Normalized(V/C) + w2 * Speed_Deficit + w3 * Severe_Frequency + w4 * Speed_Volatility ] * 100
        
    Weights:
        w1 (V/C Ratio): 0.35
        w2 (Speed Deficit): 0.35
        w3 (Severe Congestion Frequency): 0.20
        w4 (Speed Volatility / Stop-and-Go): 0.10
    """
    if df.empty:
        return pd.DataFrame()

    records = []
    
    for loc_name, group in df.groupby("location_name"):
        total_obs = len(group)
        if total_obs == 0:
            continue
            
        loc_id = group["location_id"].iloc[0] if "location_id" in group.columns else "N/A"
        lat = group["latitude"].iloc[0] if "latitude" in group.columns else 0.0
        lon = group["longitude"].iloc[0] if "longitude" in group.columns else 0.0
        capacity = group["road_capacity"].iloc[0] if "road_capacity" in group.columns else 2500
        speed_limit = group["speed_limit"].iloc[0] if "speed_limit" in group.columns else 60

        avg_speed = group["average_speed"].mean()
        avg_volume = group["vehicle_count"].mean()
        peak_volume = group["vehicle_count"].max()
        min_speed = group["average_speed"].min()
        std_speed = group["average_speed"].std() if total_obs > 1 else 0.0

        # Mean Volume-to-Capacity ratio
        mean_vc = (group["vehicle_count"] / capacity).mean()
        peak_vc = (group["vehicle_count"] / capacity).max()

        # Severe congestion frequency (hours where V/C >= 0.85)
        severe_hours = (group["volume_capacity_ratio"] >= 0.85).sum() if "volume_capacity_ratio" in group.columns else 0
        severe_freq = severe_hours / total_obs

        # Normalized Components (0.0 to 1.0)
        c_vc = min(1.0, mean_vc)
        c_speed_deficit = max(0.0, min(1.0, 1.0 - (avg_speed / speed_limit)))
        c_freq = severe_freq
        c_volatility = min(1.0, std_speed / (avg_speed + 1e-6))

        # Composite CHI Score (0 - 100)
        chi_score = (
            HOTSPOT_WEIGHTS["vc_ratio"] * c_vc +
            HOTSPOT_WEIGHTS["speed_drop"] * c_speed_deficit +
            HOTSPOT_WEIGHTS["severe_frequency"] * c_freq +
            HOTSPOT_WEIGHTS["speed_volatility"] * c_volatility
        ) * 100.0

        # Primary peak period identification
        peak_period = (
            group.groupby("time_period")["vehicle_count"]
            .mean()
            .idxmax()
            if "time_period" in group.columns else "Evening Peak"
        )

        # Severity categorization
        if chi_score >= 68.0:
            severity = "Critical Bottleneck"
            severity_color = "#E63946"  # Red
        elif chi_score >= 52.0:
            severity = "High Congestion"
            severity_color = "#F4A261"  # Orange
        elif chi_score >= 38.0:
            severity = "Moderate Delay"
            severity_color = "#E9C46A"  # Yellow
        else:
            severity = "Free Flowing"
            severity_color = "#2A9D8F"  # Green

        # Diagnostic Bottleneck Summary
        speed_drop_pct = round(((speed_limit - avg_speed) / speed_limit) * 100, 1)
        diagnosis = (
            f"Operates at {mean_vc:.1%} average capacity with a {speed_drop_pct}% speed degradation "
            f"below {speed_limit} km/h limit. Severe congestion occurs {severe_freq:.1%} of observed hours, "
            f"concentrated in {peak_period}."
        )

        records.append({
            "location_id": loc_id,
            "location_name": loc_name,
            "latitude": lat,
            "longitude": lon,
            "chi_score": round(chi_score, 1),
            "severity": severity,
            "severity_color": severity_color,
            "avg_volume": round(avg_volume, 0),
            "peak_volume": int(peak_volume),
            "road_capacity": int(capacity),
            "mean_vc_ratio": round(mean_vc, 3),
            "peak_vc_ratio": round(peak_vc, 3),
            "speed_limit": int(speed_limit),
            "avg_speed": round(avg_speed, 1),
            "min_speed": round(min_speed, 1),
            "speed_deficit_pct": speed_drop_pct,
            "severe_frequency_pct": round(severe_freq * 100, 1),
            "primary_peak_period": peak_period,
            "diagnosis": diagnosis,
        })

    hotspot_df = pd.DataFrame(records)
    if not hotspot_df.empty:
        hotspot_df = hotspot_df.sort_values(by="chi_score", ascending=False).reset_index(drop=True)
        hotspot_df["rank"] = hotspot_df.index + 1
        
    return hotspot_df

def get_top_hotspots(df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    """
    Return the ranked top N congestion hotspots with metadata.
    """
    scores = calculate_hotspot_scores(df)
    return scores.head(top_n)
