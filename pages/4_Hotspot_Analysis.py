"""
Page 4: Congestion Hotspot Detection & Ranking.
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
from src.hotspot_detection import get_top_hotspots, calculate_hotspot_scores

st.set_page_config(page_title="Hotspot Analysis | Smart City Analytics", page_icon="🚨", layout="wide")
apply_custom_theme()

st.title("🚨 Congestion Hotspot Detection & Ranking")
st.markdown("Multi-criteria scoring algorithm identifying recurring arterial bottlenecks using volume-to-capacity saturation and velocity degradation.")

df, _ = get_cleaned_data()
filtered_df = render_sidebar_filters(df)

if filtered_df.empty:
    st.warning("⚠️ No data available for selected filter combination.")
    st.stop()

# Calculate Hotspot Scores
hotspots = get_top_hotspots(filtered_df, top_n=10)

if hotspots.empty:
    st.info("No hotspots detected in current selection.")
    st.stop()

# Highlights
top_hotspot = hotspots.iloc[0]
k1, k2, k3, k4 = st.columns(4)
with k1:
    render_kpi_card("Top Bottleneck", top_hotspot["location_name"], f"CHI Score: {top_hotspot['chi_score']}/100")
with k2:
    render_kpi_card("Bottleneck Severity", top_hotspot["severity"], f"Peak V/C: {top_hotspot['peak_vc_ratio']}")
with k3:
    render_kpi_card("Speed Degradation", f"{top_hotspot['speed_deficit_pct']}%", f"Avg: {top_hotspot['avg_speed']} / Limit: {top_hotspot['speed_limit']} km/h")
with k4:
    render_kpi_card("Severe Frequency", f"{top_hotspot['severe_frequency_pct']}%", "Hours with V/C ≥ 0.85")

st.markdown("---")

# Horizontal 4-Factor Breakdown Banner
st.subheader("⚖️ The 4 Factors Evaluated in Horizontal Layout")
st.markdown("Every corridor is diagnosed across these four factors arranged horizontally:")

hf1, hf2, hf3, hf4 = st.columns(4)
with hf1:
    st.markdown("""
    <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 12px; text-align: center;">
        <span style="font-size: 0.75rem; font-weight: bold; color: #64748b; text-transform: uppercase;">Factor 1: Road Saturation</span>
        <div style="font-size: 1.25rem; font-weight: bold; color: #0284c7; margin: 4px 0;">Volume ÷ Capacity</div>
        <p style="font-size: 0.75rem; color: #475569; margin: 0;">Weight: <b>35%</b> (Physical demand vs supply)</p>
    </div>
    """, unsafe_allow_html=True)
with hf2:
    st.markdown("""
    <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 12px; text-align: center;">
        <span style="font-size: 0.75rem; font-weight: bold; color: #64748b; text-transform: uppercase;">Factor 2: Speed Loss</span>
        <div style="font-size: 1.25rem; font-weight: bold; color: #e11d48; margin: 4px 0;">Velocity Deficit</div>
        <p style="font-size: 0.75rem; color: #475569; margin: 0;">Weight: <b>35%</b> (Speed drop below limit)</p>
    </div>
    """, unsafe_allow_html=True)
with hf3:
    st.markdown("""
    <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 12px; text-align: center;">
        <span style="font-size: 0.75rem; font-weight: bold; color: #64748b; text-transform: uppercase;">Factor 3: Jam Frequency</span>
        <div style="font-size: 1.25rem; font-weight: bold; color: #d97706; margin: 4px 0;">Severe Congestion %</div>
        <p style="font-size: 0.75rem; color: #475569; margin: 0;">Weight: <b>20%</b> (Fraction of hours V/C ≥ 0.85)</p>
    </div>
    """, unsafe_allow_html=True)
with hf4:
    st.markdown("""
    <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 12px; text-align: center;">
        <span style="font-size: 0.75rem; font-weight: bold; color: #64748b; text-transform: uppercase;">Factor 4: Stop-and-Go</span>
        <div style="font-size: 1.25rem; font-weight: bold; color: #059669; margin: 4px 0;">Speed Volatility</div>
        <p style="font-size: 0.75rem; color: #475569; margin: 0;">Weight: <b>10%</b> (Flow jerkiness & shockwaves)</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Section 1: Ranked Hotspots Bar Chart
st.subheader("🏆 Top Ranked Urban Congestion Corridors")

fig_rank = px.bar(
    hotspots.sort_values("chi_score", ascending=True),
    x="chi_score",
    y="location_name",
    orientation="h",
    color="severity",
    color_discrete_map={
        "Critical Bottleneck": "#ef4444",
        "High Congestion": "#f97316",
        "Moderate Delay": "#eab308",
        "Free Flowing": "#10b981"
    },
    text="chi_score",
    title="Congestion Hotspot Index (CHI) Ranking (Scale 0 - 100)",
    labels={"chi_score": "Composite CHI Score", "location_name": "Arterial Corridor", "severity": "Severity Level"}
)
fig_rank.update_traces(texttemplate='%{text:.1f}', textposition='outside')
fig_rank.update_layout(height=420, margin=dict(l=40, r=40, t=50, b=40))
st.plotly_chart(fig_rank, use_container_width=True)

st.markdown("---")

# Section 2: Hotspot Table & Bottleneck Diagnoses
col_tbl, col_diag = st.columns([3, 2])

with col_tbl:
    st.subheader("📋 Hotspot Performance Matrix")
    display_cols = [
        "rank", "location_name", "chi_score", "severity",
        "mean_vc_ratio", "peak_vc_ratio", "avg_speed", "speed_deficit_pct", "severe_frequency_pct"
    ]
    renamed_cols = {
        "rank": "Rank",
        "location_name": "Corridor",
        "chi_score": "CHI Score",
        "severity": "Severity",
        "mean_vc_ratio": "Mean V/C",
        "peak_vc_ratio": "Peak V/C",
        "avg_speed": "Avg Speed (km/h)",
        "speed_deficit_pct": "Speed Drop %",
        "severe_frequency_pct": "Severe %"
    }
    st.dataframe(
        hotspots[display_cols].rename(columns=renamed_cols).set_index("Rank"),
        use_container_width=True
    )

with col_diag:
    st.subheader("🔍 Bottleneck Root-Cause Diagnostics")
    for _, row in hotspots.head(4).iterrows():
        st.markdown(f"""
        <div style="background-color: #f1f5f9; padding: 10px 14px; border-radius: 8px; margin-bottom: 8px; border-left: 4px solid {row['severity_color']};">
            <b style="color: #0f172a;">#{row['rank']} {row['location_name']}</b> 
            <span style="font-size: 0.75rem; background: {row['severity_color']}; color: white; padding: 2px 8px; border-radius: 10px; margin-left: 6px;">{row['severity']}</span>
            <p style="margin: 4px 0 0 0; font-size: 0.82rem; color: #334155;">{row['diagnosis']}</p>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")

# Section 3: Methodology and Mathematical Formulation
with st.expander("📐 Congestion Hotspot Index (CHI) Mathematical Formulation", expanded=False):
    st.markdown("""
    ### Ranking Methodology & Weighting
    The **Congestion Hotspot Index (CHI)** evaluates corridors across four complementary dimensions:

    $$\\text{CHI} = \\left( w_1 \\cdot \\min(1.0, \\overline{VCR}) + w_2 \\cdot \\text{Deficit}_{\\text{speed}} + w_3 \\cdot F_{\\text{severe}} + w_4 \\cdot \\sigma_{\\text{norm}} \\right) \\times 100$$

    | Dimension | Weight | Definition & Engineering Rationale |
    | :--- | :---: | :--- |
    | **Capacity Saturation ($w_1$)** | **35%** | Mean Volume-to-Capacity ratio ($\\overline{VCR} = \\frac{\\text{Volume}}{\\text{Capacity}}$). Identifies systemic road supply deficits. |
    | **Speed Deficit ($w_2$)** | **35%** | Relative velocity degradation below speed limit ($1 - \\frac{\\text{Avg Speed}}{\\text{Speed Limit}}$). Measures direct commuter delay. |
    | **Severe Congestion Frequency ($w_3$)** | **20%** | Fraction of operating hours with $V/C \\ge 0.85$. Highlights persistent vs. isolated congestion. |
    | **Speed Volatility ($w_4$)** | **10%** | Coefficient of variation in operating speeds ($\\frac{\\sigma}{\\mu}$). Captures stop-and-go shockwaves. |

    > [!IMPORTANT]
    > **Engineering Governance Note**: This algorithm identifies **congestion and throughput bottlenecks** based strictly on flow and velocity sensor telemetry. Corridors are **never** labeled "accident-prone" unless explicit police incident collision records are verified.
    """)
