"""
Page 2: Peak-Hour Analytics & Commuter Rhythm.
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
)
from src.traffic_analysis import analyze_peak_hours, compare_weekday_weekend

st.set_page_config(page_title="Peak-Hour Analysis | Smart City Analytics", page_icon="⏰", layout="wide")
apply_custom_theme()

st.title("⏰ Peak-Hour Analytics & Rush-Hour Dynamics")
st.markdown("Identify urban bottleneck hours, contrast morning and evening commute surges, and examine weekday vs weekend mobility shifts.")

df, _ = get_cleaned_data()
filtered_df = render_sidebar_filters(df)

if filtered_df.empty:
    st.warning("⚠️ No data available for selected filter combination.")
    st.stop()

# Run peak analysis
peak_res = analyze_peak_hours(filtered_df)
ww_res = compare_weekday_weekend(filtered_df)

# Top highlight cards
b_hr = peak_res.get("busiest_hour", 18)
b_vol = peak_res.get("busiest_hour_volume", 0)
s_hr = peak_res.get("slowest_hour", 18)
s_spd = peak_res.get("slowest_hour_speed", 0)
v_diff = ww_res.get("volume_diff_pct", 0)

k1, k2, k3, k4 = st.columns(4)
with k1:
    render_kpi_card("Busiest Rush Hour", f"{b_hr:02d}:00", f"Mean {int(b_vol):,} veh/hr")
with k2:
    render_kpi_card("Maximum Delay Hour", f"{s_hr:02d}:00", f"Lowest velocity: {s_spd} km/h")
with k3:
    render_kpi_card("Weekday Commute Premium", f"{v_diff:+.1f}%", "Vs. weekend average volume")
with k4:
    weekday_spd = ww_res.get("weekday_avg_speed", 0)
    weekend_spd = ww_res.get("weekend_avg_speed", 0)
    render_kpi_card("Velocity Shift", f"{weekend_spd - weekday_spd:+.1f} km/h", f"Weekend: {weekend_spd} vs Wkday: {weekday_spd}")

st.markdown("---")

# Section 1: Morning, Afternoon, Evening, and Night Comparison
st.subheader("🌅 Diurnal Period Contrast: Morning vs. Midday vs. Evening vs. Night")

period_data = []
if "period_breakdown" in peak_res:
    for period, stats in peak_res["period_breakdown"].items():
        period_data.append({
            "Time Period": period,
            "Avg Volume (veh/hr)": stats["avg_volume"],
            "Avg Speed (km/h)": stats["avg_speed"],
            "Mean V/C Ratio": stats["avg_vc"]
        })
period_df = pd.DataFrame(period_data)

# Reorder logically
order_dict = {"Morning Peak": 1, "Midday Off-Peak": 2, "Evening Peak": 3, "Night Off-Peak": 4}
period_df["order"] = period_df["Time Period"].map(order_dict).fillna(5)
period_df = period_df.sort_values("order").drop(columns=["order"])

col_p_chart, col_p_tbl = st.columns([3, 2])

with col_p_chart:
    fig_period = px.bar(
        period_df,
        x="Time Period",
        y="Avg Volume (veh/hr)",
        color="Avg Speed (km/h)",
        color_continuous_scale="Reds_r",
        text="Avg Volume (veh/hr)",
        title="Mean Corridor Volume Across Diurnal Windows (Color = Operating Speed)"
    )
    fig_period.update_traces(texttemplate='%{text:.0f}', textposition='outside')
    fig_period.update_layout(height=380, margin=dict(l=30, r=30, t=50, b=30))
    st.plotly_chart(fig_period, use_container_width=True)

with col_p_tbl:
    st.markdown("##### 📋 Diurnal Performance Breakdown")
    st.dataframe(
        period_df.set_index("Time Period").style.format({
            "Avg Volume (veh/hr)": "{:,.0f}",
            "Avg Speed (km/h)": "{:.1f}",
            "Mean V/C Ratio": "{:.3f}"
        }),
        use_container_width=True
    )
    st.markdown("""
    <div class="info-card">
        <b>Commuter Insight:</b> The <b>Evening Peak</b> generally sustains higher congestion than the Morning Peak because outbound commuter trips overlap with retail, dining, and freight deliveries.
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Section 2: Weekday vs Weekend Hourly Curves
st.subheader("📅 Weekday vs. Weekend Commuter Curves")

if "hourly_comparison" in ww_res:
    hc_df = ww_res["hourly_comparison"]
    fig_ww = px.line(
        hc_df,
        x="hour",
        y="avg_volume",
        color="day_type",
        color_discrete_map={"Weekday": "#0284c7", "Weekend": "#f59e0b"},
        markers=True,
        title="24-Hour Diurnal Volume Curves: Weekdays vs Weekends",
        labels={"hour": "Hour of Day (00:00 - 23:00)", "avg_volume": "Average Volume (veh/hr)", "day_type": "Schedule"}
    )
    fig_ww.update_layout(
        xaxis=dict(tickmode="linear", tick0=0, dtick=1),
        height=400,
        margin=dict(l=30, r=30, t=50, b=30),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig_ww, use_container_width=True)

# Section 3: Day of Week Heatmap (Day of Week x Hour of Day)
st.markdown("---")
st.subheader("🔥 Day-of-Week Diurnal Congestion Matrix")

dow_matrix = filtered_df.groupby(["day_of_week", "hour"])["volume_capacity_ratio"].mean().reset_index()
# Pivot for heatmap
dow_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
heatmap_pivot = dow_matrix.pivot(index="day_of_week", columns="hour", values="volume_capacity_ratio")
heatmap_pivot = heatmap_pivot.reindex(dow_order)

fig_dow_heat = px.imshow(
    heatmap_pivot,
    labels=dict(x="Hour of Day", y="Day of Week", color="V/C Ratio"),
    x=[f"{h:02d}:00" for h in range(24)],
    y=dow_order,
    color_continuous_scale="YlOrRd",
    title="Average Volume-to-Capacity (V/C) Stress by Day of Week & Hour"
)
fig_dow_heat.update_layout(height=380, margin=dict(l=30, r=30, t=50, b=30))
st.plotly_chart(fig_dow_heat, use_container_width=True)
