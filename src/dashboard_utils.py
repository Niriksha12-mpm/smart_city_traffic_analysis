"""
Dashboard Utilities, Filter Widgets, Theming, and Data Caching for Streamlit.
"""

from typing import Tuple, Dict, Any, Optional
import streamlit as st
import pandas as pd
from datetime import datetime

from src.data_loader import load_raw_traffic_data
from src.data_cleaning import clean_traffic_data
from src.spark_processor import SparkTrafficProcessor

@st.cache_data(show_spinner="Ingesting and cleaning traffic sensor stream...")
def get_cleaned_data() -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Cached data loading and cleaning pipeline.
    """
    raw_df = load_raw_traffic_data()
    cleaned_df, report = clean_traffic_data(raw_df)
    return cleaned_df, report

def apply_custom_theme():
    """Inject polished Smart City styling, metric card styles, and layout typography."""
    st.markdown("""
    <style>
        /* General page layout and typography */
        .main {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        }
        
        /* Metric cards */
        .kpi-card {
            background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
            border-radius: 12px;
            padding: 16px 20px;
            color: #f8fafc;
            border: 1px solid rgba(255, 255, 255, 0.08);
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
            margin-bottom: 12px;
        }
        .kpi-title {
            font-size: 0.85rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: #94a3b8;
            margin-bottom: 4px;
        }
        .kpi-value {
            font-size: 1.85rem;
            font-weight: 700;
            color: #ffffff;
            margin-bottom: 4px;
        }
        .kpi-subtitle {
            font-size: 0.75rem;
            color: #38bdf8;
            font-weight: 500;
        }

        /* Spark Status pill */
        .spark-badge {
            display: inline-flex;
            align-items: center;
            background: rgba(14, 165, 233, 0.15);
            border: 1px solid rgba(14, 165, 233, 0.4);
            border-radius: 20px;
            padding: 4px 12px;
            font-size: 0.78rem;
            font-weight: 600;
            color: #0284c7;
            margin-bottom: 14px;
        }
        .spark-dot {
            width: 8px;
            height: 8px;
            background-color: #10b981;
            border-radius: 50%;
            margin-right: 8px;
            display: inline-block;
        }

        /* Callout cards */
        .info-card {
            background-color: #f8fafc;
            border-left: 4px solid #0284c7;
            padding: 12px 16px;
            border-radius: 6px;
            font-size: 0.9rem;
            color: #334155;
            margin: 10px 0;
        }
    </style>
    """, unsafe_allow_html=True)

def render_sidebar_filters(df: pd.DataFrame) -> pd.DataFrame:
    """
    Render global sidebar filters and return the filtered slice of data.
    """
    st.sidebar.markdown("### 🎛️ Network Filters")
    
    # Spark Engine Status
    st.sidebar.markdown("""
    <div class="spark-badge">
        <span class="spark-dot"></span> PySpark 4.2.0 Engine Active
    </div>
    """, unsafe_allow_html=True)

    # 1. Location filter
    all_locations = sorted(df["location_name"].unique().tolist())
    selected_locations = st.sidebar.multiselect(
        "Corridor / Location:",
        options=all_locations,
        default=all_locations,
        help="Select one or more arterial corridors to filter metrics."
    )

    # 2. Date Range filter
    min_date = df["timestamp"].min().date()
    max_date = df["timestamp"].max().date()
    
    date_range = st.sidebar.date_input(
        "Observation Date Window:",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
        help="Select observation time span."
    )

    # 3. Day of week filter
    day_type = st.sidebar.radio(
        "Commuter Schedule:",
        options=["All Days", "Weekdays Only (Mon-Fri)", "Weekends Only (Sat-Sun)"],
        index=0
    )

    # 4. Weather filter
    if "weather_condition" in df.columns:
        weather_options = ["All Conditions"] + sorted(df["weather_condition"].dropna().unique().tolist())
        selected_weather = st.sidebar.selectbox("Weather Condition:", weather_options, index=0)
    else:
        selected_weather = "All Conditions"

    # Apply Filters
    filtered_df = df.copy()

    # Filter locations
    if selected_locations:
        filtered_df = filtered_df[filtered_df["location_name"].isin(selected_locations)]
    else:
        st.sidebar.warning("⚠️ No corridor selected. Showing empty dataset.")
        return filtered_df.iloc[0:0]

    # Filter dates
    if isinstance(date_range, tuple) and len(date_range) == 2:
        start_date, end_date = date_range
        filtered_df = filtered_df[
            (filtered_df["timestamp"].dt.date >= start_date) &
            (filtered_df["timestamp"].dt.date <= end_date)
        ]

    # Filter day type
    if day_type == "Weekdays Only (Mon-Fri)":
        filtered_df = filtered_df[filtered_df["is_weekend"] == 0]
    elif day_type == "Weekends Only (Sat-Sun)":
        filtered_df = filtered_df[filtered_df["is_weekend"] == 1]

    # Filter weather
    if selected_weather != "All Conditions":
        filtered_df = filtered_df[filtered_df["weather_condition"] == selected_weather]

    # Sidebar Summary Counter
    st.sidebar.markdown("---")
    st.sidebar.caption(f"📊 **Active Sample**: {len(filtered_df):,} / {len(df):,} records ({len(filtered_df)/len(df):.1%})")

    # Download Project Report PDF
    pdf_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "Smart_City_Traffic_Analytics_Report.pdf"
    )
    if os.path.exists(pdf_path):
        with open(pdf_path, "rb") as f:
            pdf_bytes = f.read()
        st.sidebar.download_button(
            label="📑 Download VTU Report (PDF)",
            data=pdf_bytes,
            file_name="Smart_City_Traffic_Analytics_Report.pdf",
            mime="application/pdf",
            use_container_width=True
        )

    return filtered_df

def render_kpi_card(title: str, value: str, subtitle: str = ""):
    """Render a styled KPI card in Streamlit."""
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">{title}</div>
        <div class="kpi-value">{value}</div>
        <div class="kpi-subtitle">{subtitle}</div>
    </div>
    """, unsafe_allow_html=True)

def build_scatter_map(df, lat="latitude", lon="longitude", **kwargs):
    """
    Universal Plotly map generator supporting Plotly 7+ (scatter_map / map_style)
    and Plotly 5/6 (scatter_mapbox / mapbox_style).
    """
    import plotly.express as px
    if hasattr(px, "scatter_map"):
        fig = px.scatter_map(df, lat=lat, lon=lon, **kwargs)
        fig.update_layout(map_style="carto-positron")
    else:
        fig = px.scatter_mapbox(df, lat=lat, lon=lon, **kwargs)
        fig.update_layout(mapbox_style="carto-positron")
    return fig

