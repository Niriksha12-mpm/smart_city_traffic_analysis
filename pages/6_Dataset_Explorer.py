"""
Page 6: Dataset Explorer, Schema Dictionary, and Audit Reporting.
"""

import os
import streamlit as st
import pandas as pd

from src.dashboard_utils import (
    get_cleaned_data,
    apply_custom_theme,
    render_sidebar_filters,
    render_kpi_card,
)
from src.data_loader import load_raw_traffic_data, get_file_metadata
from src.config import RAW_DATA_PATH

st.set_page_config(page_title="Dataset Explorer | Smart City Analytics", page_icon="📁", layout="wide")
apply_custom_theme()

st.title("📁 Dataset Explorer & Quality Audit")
st.markdown("Inspect raw telemetry ingestion, data cleaning pipeline audit metrics, and complete schema dictionary.")

# Ingestion audit
try:
    meta = get_file_metadata(RAW_DATA_PATH)
except Exception as e:
    meta = {}

df, audit_report = get_cleaned_data()
filtered_df = render_sidebar_filters(df)

# Audit Summary Cards
st.subheader("🛡️ Data Cleaning & Quality Audit Metrics")
a1, a2, a3, a4, a5 = st.columns(5)
with a1:
    render_kpi_card("Raw Ingested Rows", f"{audit_report['raw_record_count']:,}", f"File size: {meta.get('file_size_mb', 1.3)} MB")
with a2:
    render_kpi_card("Duplicates Dropped", f"{audit_report['duplicates_removed']:,}", "Identical key records")
with a3:
    render_kpi_card("Missing Imputed", f"{audit_report['missing_speed_imputed'] + audit_report['missing_count_imputed']:,}", "Temporal median fill")
with a4:
    render_kpi_card("Anomalies Clipped", f"{audit_report['anomalous_speeds_clipped'] + audit_report['anomalous_counts_clipped']:,}", "Impossible physical values")
with a5:
    render_kpi_card("Cleaned Production Rows", f"{audit_report['cleaned_record_count']:,}", "100% Validated Telemetry")

st.markdown("---")

# Tabs for Raw vs Cleaned Data
tab_clean, tab_raw, tab_dict, tab_stats = st.tabs([
    "✨ Cleaned & Feature-Engineered Dataset",
    "📜 Raw Sensor Observations",
    "📖 Field Dictionary & Schema",
    "📊 Statistical Summaries"
])

with tab_clean:
    st.markdown(f"**Showing {len(filtered_df):,} records** matching active sidebar filters.")
    st.dataframe(filtered_df.head(200), use_container_width=True)
    
    # Download Buttons
    col_d1, col_d2 = st.columns(2)
    with col_d1:
        csv_bytes = filtered_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Cleaned Dataset (CSV)",
            data=csv_bytes,
            file_name="cleaned_smart_city_traffic_data.csv",
            mime="text/csv",
            use_container_width=True
        )
    with col_d2:
        pdf_file_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "Smart_City_Traffic_Analytics_Report.pdf"
        )
        if os.path.exists(pdf_file_path):
            with open(pdf_file_path, "rb") as f:
                pdf_bytes = f.read()
            st.download_button(
                label="📑 Download VTU Project Report (PDF)",
                data=pdf_bytes,
                file_name="Smart_City_Traffic_Analytics_Report.pdf",
                mime="application/pdf",
                use_container_width=True
            )

with tab_raw:
    st.markdown("Raw data before deduplication, anomaly removal, and median imputation:")
    raw_df = load_raw_traffic_data()
    st.dataframe(raw_df.head(100), use_container_width=True)

with tab_dict:
    st.markdown("### Schema Specification & Feature Engineering Definitions")
    dict_data = [
        {"Column": "timestamp", "Type": "Datetime", "Description": "Timestamp of the hourly sensor reading (YYYY-MM-DD HH:MM:SS)."},
        {"Column": "location_id", "Type": "String", "Description": "Unique sensor corridor identifier (e.g. LOC_01)."},
        {"Column": "location_name", "Type": "String", "Description": "Human-readable urban corridor or intersection name."},
        {"Column": "latitude / longitude", "Type": "Float", "Description": "Geographic coordinates of the sensing station."},
        {"Column": "vehicle_count", "Type": "Integer", "Description": "Hourly volume of vehicles passing through the sensor zone."},
        {"Column": "average_speed", "Type": "Float", "Description": "Harmonic mean velocity of traffic stream (km/h)."},
        {"Column": "road_capacity", "Type": "Integer", "Description": "Theoretical maximum design throughput (veh/hr)."},
        {"Column": "speed_limit", "Type": "Integer", "Description": "Enforced regulatory arterial speed limit (km/h)."},
        {"Column": "volume_capacity_ratio (V/C)", "Type": "Float", "Description": "Capacity saturation index (vehicle_count / road_capacity)."},
        {"Column": "speed_performance_index (SPI)", "Type": "Float", "Description": "Velocity efficiency (average_speed / speed_limit)."},
        {"Column": "congestion_level", "Type": "String", "Description": "Four-tier classification: Low (<0.6), Moderate (0.6-0.85), Heavy (0.85-1.0), Severe (≥1.0)."},
        {"Column": "time_period", "Type": "String", "Description": "Diurnal window: Morning Peak, Midday Off-Peak, Evening Peak, Night Off-Peak."},
        {"Column": "is_weekend", "Type": "Integer", "Description": "Binary flag (1 for Saturday/Sunday, 0 for Monday-Friday)."},
        {"Column": "weather_condition", "Type": "String", "Description": "Ambient weather: Clear, Rainy, Foggy, Overcast."}
    ]
    st.dataframe(pd.DataFrame(dict_data), use_container_width=True)

with tab_stats:
    st.markdown("### Numerical Column Summary Statistics")
    st.dataframe(filtered_df.describe().round(2).transpose(), use_container_width=True)
