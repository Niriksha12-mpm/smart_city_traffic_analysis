"""
Smart City Traffic Pattern & Congestion Analytics - Executive Dashboard.
Main Landing Page: Project Overview, Big Data Architecture, and System Telemetry.
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

from src.dashboard_utils import (
    get_cleaned_data,
    apply_custom_theme,
    render_sidebar_filters,
    render_kpi_card,
    build_scatter_map,
)
from src.spark_processor import SparkTrafficProcessor
from src.traffic_analysis import compute_network_kpis, generate_traffic_insights

# Configure Streamlit page
st.set_page_config(
    page_title="Smart City Traffic Analytics",
    page_icon="🚦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Apply styling
apply_custom_theme()

# Header & Introduction
st.title("🚦 Smart City Traffic Pattern & Congestion Analytics")
st.markdown("""
**An Enterprise Big Data Analytics Platform** powered by **Apache Spark (PySpark)**, **Scikit-Learn**, and **Streamlit**.
This platform ingests distributed urban traffic sensor telemetry, detects bottlenecks, analyzes rush-hour dynamics, and forecasts network traffic flow.
""")

# Load cached cleaned dataset
try:
    df, audit_report = get_cleaned_data()
except Exception as e:
    st.error(f"❌ Failed to load dataset: {e}")
    st.stop()

# Sidebar filters
filtered_df = render_sidebar_filters(df)

if filtered_df.empty:
    st.warning("⚠️ No data available for the selected filter combination. Please broaden your selection.")
    st.stop()

# Compute network KPIs
kpis = compute_network_kpis(filtered_df)

# Top KPI Metric Cards
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    render_kpi_card("Total Monitored Flow", f"{kpis['total_volume']:,}", "Total vehicle passages")
with col2:
    render_kpi_card("Network Avg Speed", f"{kpis['avg_speed']} km/h", "Average corridor velocity")
with col3:
    render_kpi_card("Mean V/C Ratio", f"{kpis['mean_vc_ratio']}", "Capacity utilization index")
with col4:
    render_kpi_card("Severe Congestion", f"{kpis['network_congestion_pct']}%", "Hours with V/C ≥ 0.85")
with col5:
    render_kpi_card("Peak Stress Rate", f"{kpis['peak_congestion_rate']}%", "Rush-hour severe rate")

st.markdown("---")

# Layout: Corridor Map & Executive Insights
left_col, right_col = st.columns([3, 2])

with left_col:
    st.subheader("🗺️ Monitored Smart City Corridor Network")
    
    # Aggregated corridor stats for map representation
    corridor_map_df = filtered_df.groupby("location_name").agg(
        latitude=("latitude", "first"),
        longitude=("longitude", "first"),
        avg_volume=("vehicle_count", "mean"),
        avg_speed=("average_speed", "mean"),
        mean_vc=("volume_capacity_ratio", "mean"),
        capacity=("road_capacity", "first")
    ).reset_index()

    corridor_map_df["avg_volume"] = corridor_map_df["avg_volume"].round(0)
    corridor_map_df["avg_speed"] = corridor_map_df["avg_speed"].round(1)
    corridor_map_df["mean_vc"] = corridor_map_df["mean_vc"].round(3)

    fig_map = build_scatter_map(
        corridor_map_df,
        lat="latitude",
        lon="longitude",
        hover_name="location_name",
        hover_data={
            "latitude": False,
            "longitude": False,
            "avg_volume": True,
            "avg_speed": True,
            "mean_vc": True,
            "capacity": True
        },
        color="mean_vc",
        size="avg_volume",
        color_continuous_scale="Turbo",
        size_max=22,
        zoom=10.5,
        center={"lat": float(corridor_map_df["latitude"].mean()), "lon": float(corridor_map_df["longitude"].mean())},
        title="Urban Corridor Sensor Locations (Size = Flow Volume, Color = V/C Stress)"
    )
    fig_map.update_layout(
        margin={"r": 0, "t": 35, "l": 0, "b": 0},
        height=420,
        coloraxis_colorbar=dict(title="V/C Ratio")
    )
    st.plotly_chart(fig_map, use_container_width=True)

with right_col:
    st.subheader("💡 Executive Traffic Insights")
    insights = generate_traffic_insights(filtered_df)
    for insight in insights:
        st.markdown(f"""
        <div class="info-card">
            {insight}
        </div>
        """, unsafe_allow_html=True)

    st.markdown("##### ⚡ Big Data Engine Diagnostics")
    processor = SparkTrafficProcessor()
    try:
        spark_meta = processor.get_spark_engine_metadata()
        st.caption(f"""
        - **Engine**: Apache Spark `{spark_meta['spark_version']}`
        - **Cluster Master**: `{spark_meta['master']}` (Parallelism: {spark_meta['default_parallelism']} cores)
        - **Shuffle Partitions**: `{spark_meta['shuffle_partitions']}` (Adaptive Execution: `{spark_meta['adaptive_execution']}`)
        - **JVM Environment**: OpenJDK 17 LTS Hotspot
        """)
    except Exception as e:
        st.caption(f"PySpark telemetry offline: {e}")

st.markdown("---")

# Big Data Architecture Diagram & Scalability Blueprint
st.subheader("🏗️ Big Data Analytics Architecture")

st.markdown("""
```
 +------------------------+      +---------------------------+      +---------------------------------+
 | Smart City IoT Sensors | ---> |   Apache Spark (PySpark)  | ---> | Scikit-Learn Predictive Models  |
 | 14,400+ Hourly Records |      | Windowing, Aggregation,   |      | Chronological Lag Features,     |
 | Corridors, V/C, Speeds |      | Congestion Ranking Engine |      | Random Forest & Ridge Regressor |
 +------------------------+      +---------------------------+      +---------------------------------+
                                               |                                     |
                                               v                                     v
                                 +-------------------------------------------------------------+
                                 |         Streamlit Multi-Page Interactive Dashboard          |
                                 | Overview • Peak Hours • Heatmap • Hotspots • ML Forecasting |
                                 +-------------------------------------------------------------+
```
""")

with st.expander("📖 College Viva & Placement Interview Quick Explanations", expanded=False):
    st.markdown("""
    ### Key Viva Q&A:
    1. **Why Apache Spark over native Pandas for Smart City Analytics?**
       - In real-world smart cities, millions of IoT sensor readings are collected every hour across thousands of junctions.
       - PySpark provides distributed memory caching (RDDs/DataFrames), Catalyst query optimization, and horizontal scaling across multi-node clusters (e.g. AWS EMR or Databricks), preventing memory overflow (`OutOfMemoryError`).
    2. **What is the Volume-to-Capacity (V/C) Ratio?**
       - The ratio of observed traffic volume to the road's physical design capacity. A ratio $\ge 0.85$ signifies heavy congestion; $\ge 1.0$ indicates forced flow or breakdown.
    3. **How is Data Leakage prevented in the Forecasting pipeline?**
       - Time series data is split strictly chronologically (first 80% train, subsequent 20% test). Standard random train/test splits leak future patterns into past training rows.
    """)

st.caption("Smart City Traffic Analytics Platform • Powered by Apache Spark & Streamlit")
