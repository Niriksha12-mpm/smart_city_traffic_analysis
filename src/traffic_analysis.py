"""
Traffic Pattern & Peak-Hour Analytics Engine.

Computes network-level KPIs, diurnal commuter curves, weekday vs weekend differentials,
and dynamic smart city traffic insights.
"""

from typing import Dict, Any, List
import numpy as np
import pandas as pd

def compute_network_kpis(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Compute executive network-level Key Performance Indicators (KPIs).
    """
    if df.empty:
        return {
            "total_volume": 0,
            "avg_speed": 0.0,
            "mean_vc_ratio": 0.0,
            "network_congestion_pct": 0.0,
            "peak_congestion_rate": 0.0,
            "active_corridors": 0,
            "total_records": 0,
            "date_range": "N/A"
        }

    total_volume = int(df["vehicle_count"].sum())
    avg_speed = round(float(df["average_speed"].mean()), 1)
    mean_vc = round(float(df["volume_capacity_ratio"].mean()), 3) if "volume_capacity_ratio" in df.columns else 0.0
    
    # Severe congestion rate overall (% of records where V/C >= 0.85)
    severe_records = (df["volume_capacity_ratio"] >= 0.85).sum() if "volume_capacity_ratio" in df.columns else 0
    network_congestion_pct = round((severe_records / len(df)) * 100, 1)

    # Congestion rate specifically during morning and evening rush hours
    peak_mask = df["hour"].isin([7, 8, 9, 10, 16, 17, 18, 19, 20])
    peak_df = df[peak_mask]
    if not peak_df.empty and "volume_capacity_ratio" in peak_df.columns:
        peak_severe = (peak_df["volume_capacity_ratio"] >= 0.85).sum()
        peak_congestion_rate = round((peak_severe / len(peak_df)) * 100, 1)
    else:
        peak_congestion_rate = 0.0

    active_corridors = df["location_name"].nunique() if "location_name" in df.columns else 0
    
    min_date = str(df["date"].min()) if "date" in df.columns else "N/A"
    max_date = str(df["date"].max()) if "date" in df.columns else "N/A"
    date_range = f"{min_date} to {max_date}"

    return {
        "total_volume": total_volume,
        "avg_speed": avg_speed,
        "mean_vc_ratio": mean_vc,
        "network_congestion_pct": network_congestion_pct,
        "peak_congestion_rate": peak_congestion_rate,
        "active_corridors": active_corridors,
        "total_records": len(df),
        "date_range": date_range
    }

def analyze_peak_hours(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Perform deep-dive analysis on diurnal traffic patterns and rush hours.
    """
    if df.empty:
        return {}

    hourly_agg = df.groupby("hour").agg(
        avg_volume=("vehicle_count", "mean"),
        avg_speed=("average_speed", "mean"),
        avg_vc=("volume_capacity_ratio", "mean"),
        severe_count=("volume_capacity_ratio", lambda s: (s >= 0.85).sum()),
        total_obs=("vehicle_count", "count")
    ).reset_index()

    hourly_agg["avg_volume"] = hourly_agg["avg_volume"].round(0)
    hourly_agg["avg_speed"] = hourly_agg["avg_speed"].round(1)
    hourly_agg["avg_vc"] = hourly_agg["avg_vc"].round(3)
    hourly_agg["severe_rate_pct"] = (
        (hourly_agg["severe_count"] / hourly_agg["total_obs"]) * 100
    ).round(1)

    # Identify peak volume hour
    busiest_hour_row = hourly_agg.loc[hourly_agg["avg_volume"].idxmax()]
    busiest_hour = int(busiest_hour_row["hour"])
    busiest_hour_vol = float(busiest_hour_row["avg_volume"])

    # Identify lowest speed hour (peak bottleneck)
    slowest_hour_row = hourly_agg.loc[hourly_agg["avg_speed"].idxmin()]
    slowest_hour = int(slowest_hour_row["hour"])
    slowest_speed = float(slowest_hour_row["avg_speed"])

    # Period breakdown
    period_agg = df.groupby("time_period").agg(
        avg_volume=("vehicle_count", "mean"),
        avg_speed=("average_speed", "mean"),
        avg_vc=("volume_capacity_ratio", "mean")
    ).round(2).to_dict(orient="index")

    return {
        "hourly_summary": hourly_agg,
        "busiest_hour": busiest_hour,
        "busiest_hour_volume": busiest_hour_vol,
        "slowest_hour": slowest_hour,
        "slowest_hour_speed": slowest_speed,
        "period_breakdown": period_agg
    }

def compare_weekday_weekend(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Contrast traffic volume, speed, and diurnal peak dynamics between weekdays and weekends.
    """
    if df.empty:
        return {}

    day_type_agg = df.groupby("is_weekend").agg(
        avg_volume=("vehicle_count", "mean"),
        avg_speed=("average_speed", "mean"),
        avg_vc=("volume_capacity_ratio", "mean")
    ).round(2)

    weekday_vol = float(day_type_agg.loc[0, "avg_volume"]) if 0 in day_type_agg.index else 0.0
    weekend_vol = float(day_type_agg.loc[1, "avg_volume"]) if 1 in day_type_agg.index else 0.0
    
    vol_diff_pct = round(((weekday_vol - weekend_vol) / (weekend_vol + 1e-6)) * 100, 1)

    weekday_speed = float(day_type_agg.loc[0, "avg_speed"]) if 0 in day_type_agg.index else 0.0
    weekend_speed = float(day_type_agg.loc[1, "avg_speed"]) if 1 in day_type_agg.index else 0.0

    # Daily breakdown (Monday to Sunday)
    day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    daily_agg = df.groupby(["day_of_week_num", "day_of_week"]).agg(
        avg_volume=("vehicle_count", "mean"),
        avg_speed=("average_speed", "mean"),
        avg_vc=("volume_capacity_ratio", "mean")
    ).reset_index().sort_values("day_of_week_num")

    daily_agg["avg_volume"] = daily_agg["avg_volume"].round(0)
    daily_agg["avg_speed"] = daily_agg["avg_speed"].round(1)
    daily_agg["avg_vc"] = daily_agg["avg_vc"].round(3)

    # Hourly curves per day type
    hourly_comparison = df.groupby(["is_weekend", "hour"]).agg(
        avg_volume=("vehicle_count", "mean"),
        avg_speed=("average_speed", "mean")
    ).reset_index()
    hourly_comparison["day_type"] = hourly_comparison["is_weekend"].map({0: "Weekday", 1: "Weekend"})
    hourly_comparison["avg_volume"] = hourly_comparison["avg_volume"].round(0)
    hourly_comparison["avg_speed"] = hourly_comparison["avg_speed"].round(1)

    return {
        "weekday_avg_volume": weekday_vol,
        "weekend_avg_volume": weekend_vol,
        "volume_diff_pct": vol_diff_pct,
        "weekday_avg_speed": weekday_speed,
        "weekend_avg_speed": weekend_speed,
        "daily_breakdown": daily_agg,
        "hourly_comparison": hourly_comparison
    }

def generate_traffic_insights(df: pd.DataFrame) -> List[str]:
    """
    Generate dynamic, contextual, data-backed analytical insights from the current dataset slice.
    """
    if df.empty:
        return ["No data available to generate insights."]

    insights = []
    kpis = compute_network_kpis(df)
    peaks = analyze_peak_hours(df)
    ww = compare_weekday_weekend(df)

    # 1. Volume & speed overview
    insights.append(
        f"**Network-Wide Flow**: Monitored {kpis['total_volume']:,} total vehicle passages with an average network operating speed of {kpis['avg_speed']} km/h across {kpis['active_corridors']} smart arterial corridors."
    )

    # 2. Rush hour insights
    if peaks:
        b_hr = peaks['busiest_hour']
        s_hr = peaks['slowest_hour']
        insights.append(
            f"**Peak Hour Divergence**: The busiest network hour occurs at {b_hr:02d}:00 with an average flow of {int(peaks['busiest_hour_volume']):,} veh/hr, while minimum network speeds occur at {s_hr:02d}:00 ({peaks['slowest_hour_speed']} km/h)."
        )

    # 3. Weekday vs Weekend
    if ww:
        v_diff = ww['volume_diff_pct']
        direction = "higher" if v_diff > 0 else "lower"
        insights.append(
            f"**Commuter Rhythm**: Weekday traffic volume is {abs(v_diff)}% {direction} than weekends ({int(ww['weekday_avg_volume'])} vs {int(ww['weekend_avg_volume'])} veh/hr), driven by structured office and school transit schedules."
        )

    # 4. Severe Congestion Rate
    insights.append(
        f"**Peak Chokepoint Pressure**: During recognized peak commuting windows, {kpis['peak_congestion_rate']}% of all corridor observations operate in severe congestion (Volume/Capacity ratio ≥ 0.85)."
    )

    return insights
