"""
Page 5: Traffic Volume Forecasting & ML Predictive Workbench.
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

from src.dashboard_utils import (
    get_cleaned_data,
    apply_custom_theme,
    render_kpi_card,
)
from src.traffic_forecasting import (
    create_forecasting_features,
    train_and_evaluate_forecaster,
)

st.set_page_config(page_title="Traffic Forecasting | Smart City Analytics", page_icon="🔮", layout="wide")
apply_custom_theme()

st.title("🔮 Traffic Volume Forecasting Engine")
st.markdown("Chronological machine learning forecasting pipeline predicting corridor traffic volume with leakage-free lag features and baseline comparison.")

df, _ = get_cleaned_data()

# Controls row
c_corridor, c_model, c_split = st.columns([2, 1, 1])

all_locations = sorted(df["location_name"].unique().tolist())
with c_corridor:
    selected_corridor = st.selectbox(
        "Select Target Corridor for Forecasting:",
        options=all_locations,
        index=0
    )

with c_model:
    model_choice = st.selectbox(
        "Machine Learning Algorithm:",
        options=["RandomForest", "Ridge"],
        index=0,
        help="Random Forest captures non-linear diurnal curves; Ridge provides fast L2 regularized regression."
    )

with c_split:
    train_split = st.slider(
        "Chronological Train Ratio:",
        min_value=0.60,
        max_value=0.90,
        value=0.80,
        step=0.05,
        format="%d%%"
    )

st.markdown("---")

# Feature extraction & Model Training
with st.spinner(f"Building chronological lag features and training {model_choice} model for {selected_corridor}..."):
    try:
        feature_df = create_forecasting_features(df, location_name=selected_corridor)
        results = train_and_evaluate_forecaster(feature_df, model_type=model_choice, train_ratio=train_split)
    except Exception as e:
        st.error(f"Error training forecaster: {e}")
        st.stop()

# KPI Cards: Model Performance vs Baseline
k1, k2, k3, k4 = st.columns(4)
with k1:
    render_kpi_card("ML Model MAE", f"{results['ml_mae']} veh/hr", f"Mean Absolute Error ({model_choice})")
with k2:
    render_kpi_card("ML Model RMSE", f"{results['ml_rmse']} veh/hr", "Root Mean Squared Error")
with k3:
    render_kpi_card("Accuracy Gain", f"{results['mae_improvement_pct']:+.1f}%", "Error reduction vs 24h Baseline")
with k4:
    render_kpi_card("Explained Variance", f"{results['ml_r2']:.3f}", "R² Coefficient of Determination")

# Data Leakage Prevention Banner
st.markdown(f"""
<div class="info-card">
    <b>🛡️ Leakage-Free Chronological Split:</b><br/>
    • <b>Training Window ({results['train_samples']} hrs):</b> {results['train_date_range']}<br/>
    • <b>Out-of-Sample Test Window ({results['test_samples']} hrs):</b> {results['test_date_range']}<br/>
    <i>All features rely strictly on past historical lags ($lag_{{1h}}, lag_{{2h}}, lag_{{24h}}, lag_{{168h}}$). Future values are never leaked.</i>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# Section 1: Actual vs Predicted Time-Series Plot
st.subheader("📈 Chronological Out-of-Sample Evaluation: Actual vs. Forecast")

comp_df = results["comparison_df"].copy()
# Take latest 120 hours (5 days) of test set for clear visual inspection
test_slice = comp_df.tail(120)

fig_forecast = go.Figure()
fig_forecast.add_trace(
    go.Scatter(
        x=test_slice["timestamp"],
        y=test_slice["actual"],
        mode="lines+markers",
        name="Actual Observed Volume",
        line=dict(color="#0f172a", width=2.5),
        marker=dict(size=4)
    )
)
fig_forecast.add_trace(
    go.Scatter(
        x=test_slice["timestamp"],
        y=test_slice["ml_pred"],
        mode="lines",
        name=f"Predicted ({model_choice})",
        line=dict(color="#0284c7", width=2.5, dash="dash")
    )
)
fig_forecast.add_trace(
    go.Scatter(
        x=test_slice["timestamp"],
        y=test_slice["baseline_pred"],
        mode="lines",
        name="Baseline (Same-Hour Yesterday)",
        line=dict(color="#94a3b8", width=1.5, dash="dot")
    )
)
fig_forecast.update_layout(
    title=f"5-Day Out-of-Sample Validation Curve for {selected_corridor}",
    xaxis_title="Timeline",
    yaxis_title="Traffic Volume (veh/hr)",
    height=450,
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    margin=dict(l=40, r=40, t=60, b=40)
)
st.plotly_chart(fig_forecast, use_container_width=True)

st.markdown("---")

# Section 2: Metrics Comparison Table & Feature Importance
col_metrics, col_feat = st.columns([2, 2])

with col_metrics:
    st.subheader("📊 Rigorous Metric Comparison")
    st.markdown("Quantifying the accuracy advantage of machine learning over a naive persistence baseline.")
    st.dataframe(results["metrics_table"].set_index("Model"), use_container_width=True)

    # Residual Error Histogram
    st.markdown("##### 📉 Prediction Residuals Distribution")
    fig_res = px.histogram(
        comp_df,
        x="residual_error",
        nbins=30,
        title="Residual Error Distribution (Actual - Predicted)",
        labels={"residual_error": "Residual Error (veh/hr)"},
        color_discrete_sequence=["#0ea5e9"]
    )
    fig_res.update_layout(height=280, margin=dict(l=30, r=30, t=40, b=30))
    st.plotly_chart(fig_res, use_container_width=True)

with col_feat:
    st.subheader("🧠 Model Feature Importance")
    if results["feature_importance"] is not None:
        fig_feat = px.bar(
            results["feature_importance"].sort_values("importance", ascending=True),
            x="importance",
            y="feature",
            orientation="h",
            title="Feature Predictive Weight Distribution",
            labels={"importance": "Relative Importance", "feature": "Engineered Feature"},
            color="importance",
            color_continuous_scale="Blues"
        )
        fig_feat.update_layout(height=420, margin=dict(l=30, r=30, t=40, b=30))
        st.plotly_chart(fig_feat, use_container_width=True)
    else:
        st.info("Feature importance is not available for this model type.")

# Disclaimer
st.warning(
    "⚠️ **Forecasting Estimation Disclaimer**: All traffic volume forecasts are statistical estimates generated "
    "from synthetic sensor data calibrated to urban corridor characteristics. In real-world municipal deployments, "
    "models must be continuously updated with live camera streams, weather forecasts, and emergency roadwork feeds."
)
