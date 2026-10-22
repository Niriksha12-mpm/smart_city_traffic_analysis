"""
Synthetic Traffic Data Generator for Smart City Big Data Analytics.

Generates realistic hourly sensor observations across 10 strategic urban corridors
over a 60-day period. Incorporates realistic diurnal commuter curves, weekend patterns,
weather effects, volume-capacity dynamics, and intentionally injected anomalies
for data cleaning pipeline validation.
"""

import os
import random
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

def generate_dataset(output_path: str, days: int = 60, seed: int = 42):
    np.random.seed(seed)
    random.seed(seed)
    
    locations = [
        {
            "location_id": "LOC_01",
            "location_name": "Outer Ring Road (Tech Corridor)",
            "latitude": 12.9352,
            "longitude": 77.6946,
            "road_capacity": 4500,
            "speed_limit": 80,
            "commute_type": "tech_hub"
        },
        {
            "location_id": "LOC_02",
            "location_name": "Downtown Central (MG Road)",
            "latitude": 12.9756,
            "longitude": 77.6066,
            "road_capacity": 2200,
            "speed_limit": 50,
            "commute_type": "commercial"
        },
        {
            "location_id": "LOC_03",
            "location_name": "Airport Expressway",
            "latitude": 13.1986,
            "longitude": 77.7066,
            "road_capacity": 5000,
            "speed_limit": 100,
            "commute_type": "highway"
        },
        {
            "location_id": "LOC_04",
            "location_name": "University Boulevard",
            "latitude": 12.9421,
            "longitude": 77.5658,
            "road_capacity": 1800,
            "speed_limit": 40,
            "commute_type": "campus"
        },
        {
            "location_id": "LOC_05",
            "location_name": "Financial District Hub",
            "latitude": 12.9784,
            "longitude": 77.6408,
            "road_capacity": 3200,
            "speed_limit": 50,
            "commute_type": "commercial"
        },
        {
            "location_id": "LOC_06",
            "location_name": "Industrial Port Parkway",
            "latitude": 12.8512,
            "longitude": 77.6685,
            "road_capacity": 3800,
            "speed_limit": 60,
            "commute_type": "industrial"
        },
        {
            "location_id": "LOC_07",
            "location_name": "Midtown Shopping Promenade",
            "latitude": 12.9815,
            "longitude": 77.5928,
            "road_capacity": 2000,
            "speed_limit": 40,
            "commute_type": "shopping"
        },
        {
            "location_id": "LOC_08",
            "location_name": "West End Arterial",
            "latitude": 12.9602,
            "longitude": 77.5218,
            "road_capacity": 2800,
            "speed_limit": 60,
            "commute_type": "residential"
        },
        {
            "location_id": "LOC_09",
            "location_name": "North Ridge Bypass",
            "latitude": 13.0450,
            "longitude": 77.5820,
            "road_capacity": 4200,
            "speed_limit": 80,
            "commute_type": "bypass"
        },
        {
            "location_id": "LOC_10",
            "location_name": "South Link Flyover",
            "latitude": 12.9165,
            "longitude": 77.6101,
            "road_capacity": 2500,
            "speed_limit": 60,
            "commute_type": "chokepoint"
        }
    ]

    start_date = datetime(2026, 8, 1, 0, 0, 0)
    weather_options = ["Clear", "Rainy", "Overcast", "Foggy"]
    weather_weights = [0.65, 0.15, 0.15, 0.05]

    records = []
    
    for day_offset in range(days):
        current_day = start_date + timedelta(days=day_offset)
        is_weekend = current_day.weekday() >= 5
        
        # Day-level weather condition
        day_weather = np.random.choice(weather_options, p=weather_weights)

        for hour in range(24):
            timestamp = current_day.replace(hour=hour)
            
            for loc in locations:
                cap = loc["road_capacity"]
                limit = loc["speed_limit"]
                ctype = loc["commute_type"]

                # Base diurnal multiplier according to corridor archetype and hour
                if is_weekend:
                    if ctype == "shopping":
                        # High weekend traffic in afternoon/evening
                        hour_curve = 0.2 + 0.7 * np.exp(-0.5 * ((hour - 17) / 4.0) ** 2)
                    elif ctype == "tech_hub" or ctype == "campus":
                        # Low weekend traffic
                        hour_curve = 0.15 + 0.3 * np.exp(-0.5 * ((hour - 14) / 5.0) ** 2)
                    else:
                        # Leisure / midday curve
                        hour_curve = 0.2 + 0.6 * np.exp(-0.5 * ((hour - 14) / 4.5) ** 2)
                else:
                    # Weekday with distinct Morning (8-10 AM) and Evening (17-20 PM) peaks
                    morning_peak = 0.75 * np.exp(-0.5 * ((hour - 9) / 1.5) ** 2)
                    evening_peak = 0.85 * np.exp(-0.5 * ((hour - 18) / 1.8) ** 2)
                    midday_flow = 0.40 * np.exp(-0.5 * ((hour - 13) / 2.5) ** 2)
                    base_flow = 0.12
                    
                    if ctype == "chokepoint":
                        # Chokepoints surge above capacity during evening rush
                        evening_peak *= 1.25
                    elif ctype == "industrial":
                        # Industrial has freight movement early morning & late night
                        base_flow = 0.30
                        morning_peak *= 0.6
                        evening_peak *= 0.6
                    
                    hour_curve = base_flow + morning_peak + evening_peak + midday_flow

                # Add stochastic variation
                noise = np.random.normal(0, 0.06)
                multiplier = max(0.05, min(1.35, hour_curve + noise))
                
                vehicle_count = int(round(cap * multiplier))
                
                # Volume-to-Capacity ratio
                vc_ratio = vehicle_count / cap
                
                # Congestion speed degradation curve (Greenshields-inspired)
                free_flow_speed = limit * 0.95
                if vc_ratio <= 0.4:
                    speed = free_flow_speed + np.random.normal(0, 2)
                elif vc_ratio <= 0.8:
                    speed = free_flow_speed - (limit * 0.25 * ((vc_ratio - 0.4) / 0.4)) + np.random.normal(0, 2.5)
                elif vc_ratio <= 1.0:
                    speed = (limit * 0.70) - (limit * 0.35 * ((vc_ratio - 0.8) / 0.2)) + np.random.normal(0, 3)
                else:
                    # Severe breakdown
                    speed = max(12.0, (limit * 0.35) / (vc_ratio ** 1.5)) + np.random.normal(0, 2)

                # Incident simulation (1% probability during peak, 0.3% off-peak)
                is_incident = 0
                incident_prob = 0.015 if (7 <= hour <= 10 or 17 <= hour <= 20) else 0.003
                if np.random.rand() < incident_prob:
                    is_incident = 1
                    speed = max(8.0, speed * 0.45) # severe bottleneck due to lane blockage
                    vehicle_count = int(vehicle_count * 0.8) # queued upstream or diverted

                # Weather effect
                if day_weather == "Rainy":
                    speed *= 0.82
                elif day_weather == "Foggy":
                    speed *= 0.88

                speed = round(float(np.clip(speed, 6.0, limit * 1.15)), 1)

                records.append({
                    "timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                    "location_id": loc["location_id"],
                    "location_name": loc["location_name"],
                    "latitude": loc["latitude"],
                    "longitude": loc["longitude"],
                    "vehicle_count": vehicle_count,
                    "average_speed": speed,
                    "road_capacity": cap,
                    "speed_limit": limit,
                    "weather_condition": day_weather,
                    "incident_flag": is_incident
                })

    df = pd.DataFrame(records)
    print(f"Base records generated: {len(df)}")

    # Invalidate a few records deliberately for robust Data Cleaning Pipeline validation
    # 1. Duplicate records (~35 rows)
    dup_indices = np.random.choice(len(df), size=35, replace=False)
    dup_rows = df.iloc[dup_indices].copy()
    
    # 2. Missing values (~40 rows with NaN in vehicle_count or average_speed)
    nan_speed_idx = np.random.choice(len(df), size=25, replace=False)
    nan_count_idx = np.random.choice(len(df), size=20, replace=False)
    df.loc[nan_speed_idx, "average_speed"] = np.nan
    df.loc[nan_count_idx, "vehicle_count"] = np.nan

    # 3. Impossible numeric outliers (~15 rows)
    outlier_speed_neg = np.random.choice(len(df), size=5, replace=False)
    outlier_speed_huge = np.random.choice(len(df), size=5, replace=False)
    outlier_count_neg = np.random.choice(len(df), size=5, replace=False)
    df.loc[outlier_speed_neg, "average_speed"] = -15.0
    df.loc[outlier_speed_huge, "average_speed"] = 380.0
    df.loc[outlier_count_neg, "vehicle_count"] = -50

    # Combine with duplicates
    df = pd.concat([df, dup_rows], ignore_index=True)
    
    # Shuffle slightly so anomalies are dispersed
    df = df.sample(frac=1.0, random_state=seed).reset_index(drop=True)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"Successfully generated {len(df)} records into: {output_path}")
    return df

if __name__ == "__main__":
    out_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "traffic_data.csv")
    generate_dataset(out_file, days=60)
