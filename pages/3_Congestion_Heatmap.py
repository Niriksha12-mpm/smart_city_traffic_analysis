"""
Page 3: Congestion Heatmap & Spatiotemporal Visualization.
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

st.set_page_config(page_title="Congestion Heatmap | Smart City Analytics", page_icon="🗺️", layout="wide")
apply_custom_theme()

st.title("🗺️ Spatiotemporal Congestion Heatmap")
st.markdown("Visualize spatial bottleneck distribution across urban corridors and dynamic temporal congestion intensity.")

df, _ = get_cleaned_data()
filtered_df = render_sidebar_filters(df)

if filtered_df.empty:
    st.warning("⚠️ No data available for selected filter combination.")
    st.stop()

# Metric selection toggle for heatmaps
metric_choice = st.radio(
    "Select Heatmap Intensity Metric:",
    options=["Volume-to-Capacity Ratio (V/C)", "Average Speed (km/h)", "Vehicle Count (veh/hr)"],
    index=0,
    horizontal=True
)

metric_col_map = {
    "Volume-to-Capacity Ratio (V/C)": ("volume_capacity_ratio", "YlOrRd", False),
    "Average Speed (km/h)": ("average_speed", "Viridis_r", True),
    "Vehicle Count (veh/hr)": ("vehicle_count", "Blues", False)
}

target_col, color_palette, reverse_scale = metric_col_map[metric_choice]

st.markdown("---")

# Section 1: Corridor-by-Hour Temporal Matrix Heatmap
st.subheader("🔥 Corridor vs. Hour-of-Day Congestion Matrix")
st.markdown("Identifies exact peak congestion windows across individual smart city arterials.")

corridor_hour_matrix = filtered_df.groupby(["location_name", "hour"])[target_col].mean().reset_index()
pivot_table = corridor_hour_matrix.pivot(index="location_name", columns="hour", values=target_col)
pivot_table.columns = [f"{h:02d}:00" for h in pivot_table.columns]

# Sort corridors by highest peak stress
pivot_table["max_val"] = pivot_table.max(axis=1)
pivot_table = pivot_table.sort_values(by="max_val", ascending=False).drop(columns=["max_val"])

fig_matrix = px.imshow(
    pivot_table,
    labels=dict(x="Hour of Day", y="Arterial Corridor", color=metric_choice),
    color_continuous_scale=color_palette,
    aspect="auto",
    title=f"Spatiotemporal Intensity Matrix: {metric_choice} by Corridor and Hour"
)
fig_matrix.update_layout(height=480, margin=dict(l=40, r=40, t=50, b=40))
st.plotly_chart(fig_matrix, use_container_width=True)

st.markdown("---")

# Section 2: Interactive Geographic Density Map by Time of Day
st.subheader("📍 Geospatial Congestion Density Map")

# Interactive Hour Slider for Spatial Exploration
selected_hour = st.slider(
    "Explore Congestion at Hour of Day (0 = Midnight, 12 = Noon, 18 = Evening Rush):",
    min_value=0,
    max_value=23,
    value=18,
    format="%02d:00"
)

hour_slice = filtered_df[filtered_df["hour"] == selected_hour]

if hour_slice.empty:
    st.info(f"No records available for {selected_hour:02d}:00 with current sidebar filters.")
else:
    map_agg = hour_slice.groupby("location_name").agg(
        latitude=("latitude", "first"),
        longitude=("longitude", "first"),
        val=(target_col, "mean"),
        volume=("vehicle_count", "mean"),
        speed=("average_speed", "mean"),
        capacity=("road_capacity", "first")
    ).reset_index()

    map_agg["val"] = map_agg["val"].round(2)
    map_agg["volume"] = map_agg["volume"].round(0)
    map_agg["speed"] = map_agg["speed"].round(1)

    fig_geo = build_scatter_map(
        map_agg,
        lat="latitude",
        lon="longitude",
        hover_name="location_name",
        hover_data={"latitude": False, "longitude": False, "val": True, "volume": True, "speed": True, "capacity": True},
        color="val",
        size="volume",
        color_continuous_scale=color_palette,
        size_max=24,
        zoom=10.5,
        center={"lat": float(map_agg["latitude"].mean()), "lon": float(map_agg["longitude"].mean())},
        title=f"Urban Arterial Heatmap at {selected_hour:02d}:00 (Size = Flow, Color = {metric_choice})"
    )
    fig_geo.update_layout(
        margin={"r": 0, "t": 40, "l": 0, "b": 0},
        height=480,
        coloraxis_colorbar=dict(title=metric_choice.split()[0])
    )
    st.plotly_chart(fig_geo, use_container_width=True)
