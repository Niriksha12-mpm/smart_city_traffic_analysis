"""
Page 1: Traffic Overview & Network KPIs.
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

from src.dashboard_utils import (
    get_cleaned_data,
    apply_custom_theme,
    render_sidebar_filters,
    render_kpi_card,
)
from src.traffic_analysis import compute_network_kpis

st.set_page_config(page_title="Traffic Overview | Smart City Analytics", page_icon="📊", layout="wide")
apply_custom_theme()

st.title("📊 Traffic Overview & Network Velocity")
st.markdown("Examine macroscopic network metrics, velocity curves, and volume distributions across arterial corridors.")

df, _ = get_cleaned_data()
filtered_df = render_sidebar_filters(df)

if filtered_df.empty:
    st.warning("⚠️ No data available for selected filter combination.")
    st.stop()

# KPIs
kpis = compute_network_kpis(filtered_df)
c1, c2, c3, c4, c5 = st.columns(5)
with c1:
    render_kpi_card("Total Flow Monitored", f"{kpis['total_volume']:,}", "Vehicles recorded")
with c2:
    render_kpi_card("Network Avg Speed", f"{kpis['avg_speed']} km/h", "Mean arterial velocity")
with c3:
    render_kpi_card("Mean V/C Ratio", f"{kpis['mean_vc_ratio']}", "Road capacity utilization")
with c4:
    render_kpi_card("Severe Congestion", f"{kpis['network_congestion_pct']}%", "Hours where V/C ≥ 0.85")
with c5:
    render_kpi_card("Active Corridors", f"{kpis['active_corridors']}", "Monitored sensor zones")

st.markdown("---")

# Section 1: Diurnal Volume & Speed Curves (Dual-Axis Chart)
st.subheader("📈 Diurnal Network Commuter Profile (24-Hour Velocity & Flow)")

hourly_profile = filtered_df.groupby("hour").agg(
    avg_volume=("vehicle_count", "mean"),
    avg_speed=("average_speed", "mean")
).reset_index()

fig_diurnal = make_subplots(specs=[[{"secondary_y": True}]])
fig_diurnal.add_trace(
    go.Bar(
        x=hourly_profile["hour"],
        y=hourly_profile["avg_volume"],
        name="Average Hourly Volume (veh/hr)",
        marker_color="#0284c7",
        opacity=0.75
    ),
    secondary_y=False
)
fig_diurnal.add_trace(
    go.Scatter(
        x=hourly_profile["hour"],
        y=hourly_profile["avg_speed"],
        name="Average Speed (km/h)",
        mode="lines+markers",
        line=dict(color="#e11d48", width=3),
        marker=dict(size=7)
    ),
    secondary_y=True
)
fig_diurnal.update_layout(
    title="24-Hour Network Profile: Traffic Flow vs Speed Degradation",
    xaxis=dict(title="Hour of Day (00:00 - 23:00)", tickmode="linear", tick0=0, dtick=1),
    yaxis=dict(title="Vehicle Volume (veh/hr)", showgrid=True),
    yaxis2=dict(title="Average Speed (km/h)", overlaying="y", side="right", showgrid=False),
    height=450,
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    margin=dict(l=40, r=40, t=60, b=40)
)
st.plotly_chart(fig_diurnal, use_container_width=True)

# Section 2: Speed vs Volume (Greenshields Fundamental Diagram) & Flow Distribution
st.markdown("---")
col_scatter, col_dist = st.columns([3, 2])

with col_scatter:
    st.subheader("🔬 Fundamental Traffic Flow Diagram (Speed vs. Volume)")
    # Sample 1500 points for crisp interactive plotting
    sample_scatter = filtered_df.sample(min(len(filtered_df), 1500), random_state=42)
    fig_flow = px.scatter(
        sample_scatter,
        x="vehicle_count",
        y="average_speed",
        color="congestion_level",
        color_discrete_map={
            "Low": "#10b981",
            "Moderate": "#eab308",
            "Heavy": "#f97316",
            "Severe": "#ef4444"
        },
        hover_data=["location_name", "hour", "volume_capacity_ratio"],
        title="Speed-Flow Relationship by Congestion Classification",
        labels={"vehicle_count": "Vehicle Count (veh/hr)", "average_speed": "Average Speed (km/h)", "congestion_level": "Congestion Level"}
    )
    fig_flow.update_layout(height=420, margin=dict(l=40, r=40, t=50, b=40))
    st.plotly_chart(fig_flow, use_container_width=True)

with col_dist:
    st.subheader("📊 Velocity & Volume Distributions")
    fig_box = px.box(
        filtered_df,
        x="congestion_level",
        y="average_speed",
        color="congestion_level",
        color_discrete_map={
            "Low": "#10b981",
            "Moderate": "#eab308",
            "Heavy": "#f97316",
            "Severe": "#ef4444"
        },
        title="Operating Speed Spread Across Congestion States",
        labels={"congestion_level": "Level", "average_speed": "Speed (km/h)"}
    )
    fig_box.update_layout(height=420, showlegend=False, margin=dict(l=40, r=40, t=50, b=40))
    st.plotly_chart(fig_box, use_container_width=True)

# Section 3: Corridor Breakdown Bar Chart
st.markdown("---")
st.subheader("🏢 Comparative Flow by Arterial Corridor")
corridor_vol = filtered_df.groupby("location_name").agg(
    total_volume=("vehicle_count", "sum"),
    avg_speed=("average_speed", "mean"),
    road_capacity=("road_capacity", "first")
).reset_index().sort_values(by="total_volume", ascending=False)

fig_bar = px.bar(
    corridor_vol,
    x="total_volume",
    y="location_name",
    orientation="h",
    color="avg_speed",
    color_continuous_scale="Viridis",
    title="Cumulative Volume Monitored per Corridor (Colored by Mean Velocity)",
    labels={"total_volume": "Total Vehicle Volume", "location_name": "Corridor", "avg_speed": "Avg Speed (km/h)"}
)
fig_bar.update_layout(height=420, yaxis={'categoryorder':'total ascending'})
st.plotly_chart(fig_bar, use_container_width=True)
