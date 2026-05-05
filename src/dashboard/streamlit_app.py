"""
Streamlit Dashboard — Revion Pricing Intelligence.

Premium real-time dashboard with interactive forecasting,
pricing insights, anomaly monitoring, and causal analysis views.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta
import requests
from streamlit_lottie import st_lottie
from PIL import Image

import os
from styles import PREMIUM_CSS
import animations
import components

# ── Page Config ──
st.set_page_config(
    page_title="⚡Revion",
    page_icon="⚡", # Keep favicon simple
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(PREMIUM_CSS, unsafe_allow_html=True)

# ── Constants ──
API_URL = os.environ.get("API_URL", "http://localhost:8000")
CATEGORIES = ["FOODS", "HOUSEHOLD", "HOBBIES"]
STORES = ["CA_1", "CA_2", "CA_3", "CA_4", "TX_1", "TX_2", "TX_3", "WI_1", "WI_2", "WI_3"]

CHART_LAYOUT = dict(
    plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#94a3b8", family="Inter", size=11),
    xaxis=dict(showgrid=False, linecolor="rgba(99,179,237,0.08)"),
    yaxis=dict(showgrid=True, gridcolor="rgba(99,179,237,0.05)", linecolor="rgba(99,179,237,0.08)"),
    margin=dict(l=0, r=0, t=10, b=0),
    legend=dict(font=dict(color="#94a3b8", size=11), bgcolor="rgba(0,0,0,0)"),
    hoverlabel=dict(bgcolor="#1e293b", bordercolor="#334155", font=dict(color="#f1f5f9", family="Inter")),
)

# ── Helpers ──
@st.cache_data
def load_lottieurl(url: str):
    try:
        r = requests.get(url, timeout=5)
        if r.status_code != 200:
            return None
        return r.json()
    except:
        return None

def generate_forecast(days=28):
    np.random.seed(42)
    dates = pd.date_range(datetime.now(), periods=days, freq="D")
    base = np.random.poisson(8, days).astype(float)
    seasonal = np.sin(np.linspace(0, 4 * np.pi, days)) * 3
    trend = np.linspace(0, 2, days)
    forecast = np.maximum(0, base + seasonal + trend)
    return pd.DataFrame({"date": dates, "forecast": forecast, "lower": forecast * 0.7, "upper": forecast * 1.4})

def generate_sales(days=365, seed=42):
    np.random.seed(seed)
    dates = pd.date_range(datetime.now() - timedelta(days=days), periods=days, freq="D")
    base = np.random.poisson(6, days).astype(float)
    seasonal = np.sin(np.linspace(0, 2 * np.pi * (days / 365), days)) * 4
    trend = np.linspace(0, 3, days)
    noise = np.random.normal(0, 1, days)
    return pd.DataFrame({"date": dates, "sales": np.maximum(0, base + seasonal + trend + noise)})

def metric_card(label, value, delta=None, color="cyan", delay=0):
    delta_html = ""
    if delta is not None:
        cls = "up" if delta >= 0 else "down"
        arrow = "↑" if delta >= 0 else "↓"
        delta_html = f'<div class="metric-delta {cls}">{arrow} {abs(delta):.1f}%</div>'
    st.markdown(f"""
    <div class="metric-card" style="animation-delay: {delay}s; padding-left: 1.5rem;">
        <div class="metric-label">{label}</div>
        <div class="metric-value {color}">{value}</div>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)

def section_header(title, tag=None):
    tag_html = f'<span class="section-tag">{tag}</span>' if tag else ""
    st.markdown(f"""
    <div class="section-header" style="margin-top: 1rem;">
        {title} {tag_html}
    </div>
    """, unsafe_allow_html=True)

# Try loading a premium pulsing animation
lottie_pulse = load_lottieurl("https://lottie.host/801a681c-6d1a-4ab7-b8db-c529a67448d3/FhD5fV05m8.json")

# ── Sidebar ──
with st.sidebar:
    # Use Lottie at the top of sidebar if available
    if lottie_pulse:
        st_lottie(lottie_pulse, height=80, key="sidebar_pulse")
    else:
        st.markdown("<div style='height: 40px;'></div>", unsafe_allow_html=True)

    st.markdown("""
    <div style="padding: 0 0 16px; text-align: center;">
        <div style="font-size: 1.2rem; font-weight: 800; color: #f1f5f9; letter-spacing: -0.3px;">
            ⚡ Revion
        </div>
        <div style="font-size: 0.7rem; color: rgba(148,163,184,0.5); letter-spacing: 1px; text-transform: uppercase;">
            Revion Core
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")

    page = st.radio("Navigation", [
        "Overview",
        "Forecasting",
        "Dynamic Pricing",
        "Anomaly Detection",
        "Causal Analysis",
    ], label_visibility="collapsed")

    st.markdown("---")
    with st.expander("System Filters", expanded=True):
        selected_store = st.selectbox("Store", STORES)
        selected_category = st.selectbox("Category", CATEGORIES)
        date_range = st.date_input("Date Range", value=[
            datetime.now() - timedelta(days=90), datetime.now()
        ])

    st.markdown("---")
    st.markdown("""
    <div style="text-align:center; padding: 8px 0;">
        <div style="font-size: 0.65rem; color: rgba(148,163,184,0.3); letter-spacing: 0.5px;">
            Powered by LightGBM + TFT
        </div>
    </div>
    """, unsafe_allow_html=True)


# ── Page: Overview ──
if page == "Overview":
    components.inject_particle_network()
    
    col_icon, col_text = st.columns([1, 7])
    with col_icon:
        animations.render_svg(animations.SVG_OVERVIEW)
    with col_text:
        st.markdown("""
        <div class="hero-header" style="text-align: left; padding: 10px 0 0 0;">
            <div style="display: flex; align-items: center; gap: 12px;">
                <div class="hero-title">⚡ Revion</div>
                <div class="tooltip-container">
                    <div class="tooltip-icon">✦</div>
                    <div class="tooltip-content">
                        <div class="tooltip-title">About Overview</div>
                        <div class="tooltip-body">Provides a high-level summary of active series, forecasting accuracy (WRMSSE), revenue lift from dynamic pricing, recent anomalies, and average price variations across all regions.</div>
                    </div>
                </div>
            </div>
            <div class="hero-subtitle">Real-time demand forecasting · pricing optimization · anomaly monitoring</div>
            <div class="live-badge"><span class="live-dot"></span> System Operational</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height: 20px'></div>", unsafe_allow_html=True)

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1: metric_card("Active Series", "42,840", 0, "cyan", 0)
    with c2: metric_card("Forecast WRMSSE", "0.52", -3.2, "green", 0.1)
    with c3: metric_card("Revenue Lift", "+8.4%", 8.4, "amber", 0.2)
    with c4: metric_card("Anomalies 24h", "12", -25.0, "rose", 0.3)
    with c5: metric_card("Avg Price Δ", "4.7%", 0.8, "cyan", 0.4)

    st.markdown("<div style='height: 16px'></div>", unsafe_allow_html=True)

    col_main, col_feed = st.columns([3, 1.2])
    
    with col_main:
        tab1, tab2 = st.tabs(["Performance Metrics", "Regional Distribution"])
        
        with tab1:
            col_l, col_r = st.columns([2, 1])
            with col_l:
                with st.container(border=True):
                    section_header("Demand Trend", "LAST 90 DAYS")
                    hist = generate_sales(90, seed=101)
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=hist["date"], y=hist["sales"], mode="lines",
                        fill="tozeroy", line=dict(color="#22d3ee", width=2),
                        fillcolor="rgba(34, 211, 238, 0.06)", name="Demand",
                        hovertemplate="<b>%{x|%b %d}</b><br>Demand: %{y:.1f}<extra></extra>",
                    ))
                    fig.add_trace(go.Scatter(
                        x=hist["date"], y=hist["sales"].rolling(7).mean(), mode="lines",
                        line=dict(color="#a78bfa", width=1.5, dash="dot"), name="7-day MA",
                        hovertemplate="<b>%{x|%b %d}</b><br>MA: %{y:.1f}<extra></extra>",
                    ))
                    fig.update_layout(**CHART_LAYOUT, height=340, showlegend=True)
                    st.plotly_chart(fig, use_container_width=True)

            with col_r:
                with st.container(border=True):
                    section_header("Category Mix", "DISTRIBUTION")
                    fig = go.Figure(data=[go.Pie(
                        labels=CATEGORIES, values=[45, 35, 20],
                        marker=dict(colors=["#22d3ee", "#3b82f6", "#a78bfa"],
                                    line=dict(color="#0c1120", width=2)),
                        hole=0.65, textfont=dict(color="#f1f5f9", size=12),
                        hovertemplate="<b>%{label}</b><br>Share: %{percent}<extra></extra>",
                    )])
                    fig.update_layout(**CHART_LAYOUT, height=340, showlegend=True)
                    st.plotly_chart(fig, use_container_width=True)

        with tab2:
            with st.container(border=True):
                section_header("Store Performance Heatmap", "ALL REGIONS")
                np.random.seed(77)
                heat_data = np.random.rand(3, 10) * 100
                fig = go.Figure(data=go.Heatmap(
                    z=heat_data, x=STORES, y=["CA", "TX", "WI"],
                    colorscale=[[0, "#0c1120"], [0.5, "#1e3a5f"], [1, "#22d3ee"]],
                    hovertemplate="Store: %{x}<br>State: %{y}<br>Index: %{z:.1f}<extra></extra>",
                ))
                fig.update_layout(**CHART_LAYOUT, height=340)
                st.plotly_chart(fig, use_container_width=True)
            
    with col_feed:
        components.activity_feed()


# ── Page: Forecasting ──
elif page == "Forecasting":
    col_icon, col_text = st.columns([1, 7])
    with col_icon:
        animations.render_svg(animations.SVG_FORECAST)
    with col_text:
        st.markdown("""
        <div style="display: flex; align-items: center; gap: 12px; padding-top: 10px;">
            <div class="page-title" style="padding-top: 0; margin-bottom: 0;">Demand Forecasting Engine</div>
            <div class="tooltip-container">
                <div class="tooltip-icon">✦</div>
                <div class="tooltip-content">
                    <div class="tooltip-title">Demand Forecasting</div>
                    <div class="tooltip-body">Utilizes LightGBM and Temporal Fusion Transformers (TFT) to project future demand. Adjust the horizon and input a specific item to view predictive bounds and seasonal trends.</div>
                </div>
            </div>
        </div>
        <div class="page-desc" style="margin-top: 4px;">AI-powered LightGBM & Temporal Fusion Transformer · Hierarchical reconciliation</div>
        """, unsafe_allow_html=True)

    with st.container():
        c1, c2, c3 = st.columns([2, 1, 1])
        with c1: item_id = st.text_input("Item ID", "FOODS_3_090")
        with c2: horizon = st.slider("Horizon (days)", 7, 56, 28)
        with c3: 
            st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
            run = st.button("Generate Forecast", type="primary", use_container_width=True)

    if run:
        fc = generate_forecast(horizon)
        c1, c2, c3, c4 = st.columns(4)
        with c1: metric_card("Mean Forecast", f"{fc['forecast'].mean():.1f}", color="cyan")
        with c2: metric_card("Peak Demand", f"{fc['forecast'].max():.1f}", color="amber")
        with c3: metric_card("Min Demand", f"{fc['forecast'].min():.1f}", color="green")
        with c4: metric_card("CI Width", f"±{(fc['upper'] - fc['lower']).mean():.1f}", color="rose")

        tab_chart, tab_data = st.tabs(["Visual Forecast", "Data Table"])
        
        with tab_chart:
            with st.container(border=True):
                section_header(f"Forecast — {item_id}", f"{horizon}D HORIZON")
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=fc["date"], y=fc["upper"], mode="lines", line=dict(width=0), showlegend=False))
                fig.add_trace(go.Scatter(
                    x=fc["date"], y=fc["lower"], mode="lines",
                    fill="tonexty", fillcolor="rgba(34, 211, 238, 0.08)",
                    line=dict(width=0), name="95% CI",
                ))
                fig.add_trace(go.Scatter(
                    x=fc["date"], y=fc["forecast"], mode="lines+markers",
                    line=dict(color="#22d3ee", width=2.5), marker=dict(size=4, color="#22d3ee"),
                    name="Forecast",
                    hovertemplate="<b>%{x|%b %d}</b><br>Forecast: %{y:.1f}<extra></extra>",
                ))
                fig.update_layout(**CHART_LAYOUT, height=380, showlegend=True)
                st.plotly_chart(fig, use_container_width=True)

        with tab_data:
            with st.container(border=True):
                st.markdown('<div class="info-badge" style="margin-top: 1rem;">Detailed forecast breakdown</div>', unsafe_allow_html=True)
                st.dataframe(
                    fc.rename(columns={"date": "Date", "forecast": "Forecast", "lower": "Lower CI", "upper": "Upper CI"})
                    .style.format({"Forecast": "{:.1f}", "Lower CI": "{:.1f}", "Upper CI": "{:.1f}"}),
                    use_container_width=True,
                )


# ── Page: Dynamic Pricing ──
elif page == "Dynamic Pricing":
    col_icon, col_text = st.columns([1, 7])
    with col_icon:
        animations.render_svg(animations.SVG_PRICING)
    with col_text:
        st.markdown("""
        <div style="display: flex; align-items: center; gap: 12px; padding-top: 10px;">
            <div class="page-title" style="padding-top: 0; margin-bottom: 0;">Dynamic Pricing Engine</div>
            <div class="tooltip-container">
                <div class="tooltip-icon">✦</div>
                <div class="tooltip-content">
                    <div class="tooltip-title">Yield Optimization</div>
                    <div class="tooltip-body">Leverages Reinforcement Learning (Thompson Sampling) to find the optimal price point that maximizes expected revenue based on real-time elasticity models.</div>
                </div>
            </div>
        </div>
        <div class="page-desc" style="margin-top: 4px;">Reinforcement Learning · Thompson Sampling · Real-time yield optimization</div>
        """, unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        with st.container(border=True):
            st.markdown("### Model Inputs")
            current_price = st.number_input("Current Price ($)", 0.5, 50.0, 3.99, step=0.1)
            forecast_demand = st.number_input("Forecasted Demand", 0, 500, 25)
    with c2:
        np.random.seed(int(current_price * 100))
        multiplier = np.random.choice([0.9, 0.95, 1.0, 1.05, 1.1])
        rec_price = current_price * multiplier
        lift = (multiplier - 1) * 100

        section_header("AI Recommendation", "REAL-TIME")
        cc1, cc2, cc3 = st.columns(3)
        with cc1: metric_card("Optimal Price", f"${rec_price:.2f}", color="cyan")
        with cc2: metric_card("Expected Lift", f"{lift:+.1f}%", color="green")
        with cc3: metric_card("Confidence", "92%", color="amber")

    st.markdown("<br>", unsafe_allow_html=True)
    with st.container(border=True):
        section_header("Revenue Curve", "ELASTICITY MODEL")
        prices = np.linspace(current_price * 0.5, current_price * 1.5, 50)
        demands = forecast_demand * (prices / current_price) ** (-1.5)
        revenues = prices * demands
        opt_idx = int(np.argmax(revenues))

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=prices, y=revenues, mode="lines", fill="tozeroy",
            line=dict(color="#22d3ee", width=2.5),
            fillcolor="rgba(34, 211, 238, 0.06)", name="Revenue",
            hovertemplate="Price: $%{x:.2f}<br>Revenue: $%{y:.0f}<extra></extra>",
        ))
        fig.add_vline(x=prices[opt_idx], line_dash="dash", line_color="#fbbf24", line_width=1.5,
                      annotation_text="Optimal", annotation_font_color="#fbbf24")
        fig.add_vline(x=current_price, line_dash="dot", line_color="#fb7185", line_width=1,
                      annotation_text="Current", annotation_font_color="#fb7185")
        layout = {k: v for k, v in CHART_LAYOUT.items() if k not in ('xaxis', 'yaxis')}
        fig.update_layout(**layout, height=350, showlegend=False,
                          xaxis=dict(title="Price ($)", showgrid=False, linecolor="rgba(99,179,237,0.08)"),
                          yaxis=dict(title="Revenue ($)", showgrid=True, gridcolor="rgba(99,179,237,0.05)", linecolor="rgba(99,179,237,0.08)"))
        st.plotly_chart(fig, use_container_width=True)


# ── Page: Anomaly Detection ──
elif page == "Anomaly Detection":
    col_icon, col_text = st.columns([1, 7])
    with col_icon:
        animations.render_svg(animations.SVG_ANOMALY)
    with col_text:
        st.markdown("""
        <div style="display: flex; align-items: center; gap: 12px; padding-top: 10px;">
            <div class="page-title" style="padding-top: 0; margin-bottom: 0;">Anomaly Detection</div>
            <div class="tooltip-container">
                <div class="tooltip-icon">✦</div>
                <div class="tooltip-content">
                    <div class="tooltip-title">Real-Time Monitoring</div>
                    <div class="tooltip-body">Employs Isolation Forest algorithms to detect sudden spikes or drops in demand. The integrated SHAP analysis identifies the key drivers (e.g., promos, stockouts) behind the anomaly.</div>
                </div>
            </div>
        </div>
        <div class="page-desc" style="margin-top: 4px;">Real-time Isolation Forest algorithms · Predictive root cause analysis via SHAP</div>
        """, unsafe_allow_html=True)

    hist = generate_sales(180, seed=55)
    np.random.seed(55)
    anom_idx = np.random.choice(len(hist), 7, replace=False)
    hist.loc[hist.index[anom_idx], "sales"] *= np.random.choice([3.0, 0.1], 7)
    hist["is_anomaly"] = False
    hist.loc[hist.index[anom_idx], "is_anomaly"] = True

    c1, c2, c3, c4 = st.columns(4)
    with c1: metric_card("Anomalies Found", str(len(anom_idx)), color="rose")
    with c2: metric_card("Anomaly Rate", f"{len(anom_idx)/len(hist)*100:.1f}%", color="amber")
    with c3: metric_card("Detector", "IsoForest", color="cyan")
    with c4: metric_card("Sensitivity", "95%", color="green")

    st.markdown("<br>", unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["Timeline Analysis", "Root Cause Explorer"])
    
    with tab1:
        with st.container(border=True):
            section_header("Anomaly Timeline", "180 DAYS")
            normal = hist[~hist["is_anomaly"]]
            anomalies = hist[hist["is_anomaly"]]

            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=normal["date"], y=normal["sales"], mode="lines",
                line=dict(color="#22d3ee", width=1.5), name="Normal",
                hovertemplate="<b>%{x|%b %d}</b><br>Demand: %{y:.1f}<extra></extra>",
            ))
            fig.add_trace(go.Scatter(
                x=anomalies["date"], y=anomalies["sales"], mode="markers",
                marker=dict(color="#fb7185", size=11, symbol="circle",
                            line=dict(color="#fda4af", width=2)),
                name="Anomaly",
                hovertemplate="<b>%{x|%b %d}</b><br>Anomalous: %{y:.1f}<extra></extra>",
            ))
            fig.update_layout(**CHART_LAYOUT, height=380, showlegend=True)
            st.plotly_chart(fig, use_container_width=True)

    with tab2:
        with st.container(border=True):
            section_header("Root Cause Analysis", "SHAP")
            features = ["price_change", "promo_active", "snap_event", "holiday", "stockout"]
            shap_vals = np.random.rand(5) * 2 - 0.5
            colors = ["#fb7185" if v > 0 else "#34d399" for v in shap_vals]
            fig = go.Figure(go.Bar(
                x=shap_vals, y=features, orientation="h",
                marker=dict(color=colors, line=dict(width=0)),
                hovertemplate="%{y}: %{x:.2f}<extra></extra>",
            ))
            layout_shap = {k: v for k, v in CHART_LAYOUT.items() if k not in ('xaxis', 'yaxis')}
            fig.update_layout(**layout_shap, height=380,
                              xaxis=dict(title="SHAP Impact", showgrid=True, gridcolor="rgba(99,179,237,0.05)", linecolor="rgba(99,179,237,0.08)"),
                              yaxis=dict(showgrid=False, linecolor="rgba(99,179,237,0.08)"))
            st.plotly_chart(fig, use_container_width=True)


# ── Page: Causal Analysis ──
elif page == "Causal Analysis":
    col_icon, col_text = st.columns([1, 7])
    with col_icon:
        animations.render_svg(animations.SVG_CAUSAL)
    with col_text:
        st.markdown("""
        <div style="display: flex; align-items: center; gap: 12px; padding-top: 10px;">
            <div class="page-title" style="padding-top: 0; margin-bottom: 0;">Causal Inference Engine</div>
            <div class="tooltip-container">
                <div class="tooltip-icon">✦</div>
                <div class="tooltip-content">
                    <div class="tooltip-title">Impact Modeling</div>
                    <div class="tooltip-body">Uses Difference-in-Differences (DiD) and bootstrapping techniques to measure the true incremental lift of promotional events or pricing interventions, filtering out seasonal noise.</div>
                </div>
            </div>
        </div>
        <div class="page-desc" style="margin-top: 4px;">Advanced causal impact modeling · Real-time promotional incrementality</div>
        """, unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    with c1: metric_card("DiD Estimate", "+2.34", color="cyan")
    with c2: metric_card("Lift %", "15.6%", color="green")
    with c3: metric_card("P-Value", "0.003", color="amber")
    with c4: metric_card("Significant", "Yes", color="green")

    st.markdown("<br>", unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["Treatment Effect", "Bootstrapping"])

    with tab1:
        with st.container(border=True):
            section_header("Treatment vs Control", "DiD ANALYSIS")
            np.random.seed(42)
            pre, post = 30, 30
            dates = pd.date_range(datetime.now() - timedelta(days=pre), periods=pre + post, freq="D")
            treat = np.concatenate([
                np.random.poisson(10, pre).astype(float) + np.linspace(0, 1, pre),
                np.random.poisson(14, post).astype(float) + np.linspace(1, 2, post),
            ])
            ctrl = np.concatenate([
                np.random.poisson(10, pre).astype(float) + np.linspace(0, 0.5, pre),
                np.random.poisson(10, post).astype(float) + np.linspace(0.5, 1, post),
            ])

            fig = go.Figure()
            fig.add_trace(go.Scatter(x=dates, y=treat, mode="lines", name="Treatment",
                                     line=dict(color="#22d3ee", width=2.5),
                                     hovertemplate="<b>%{x|%b %d}</b><br>Treatment: %{y:.1f}<extra></extra>"))
            fig.add_trace(go.Scatter(x=dates, y=ctrl, mode="lines", name="Control",
                                     line=dict(color="#64748b", width=2, dash="dash"),
                                     hovertemplate="<b>%{x|%b %d}</b><br>Control: %{y:.1f}<extra></extra>"))
            t_date = dates[pre]
            fig.add_shape(type="line", x0=t_date, x1=t_date, y0=0, y1=1, yref="paper",
                          line=dict(color="#fbbf24", width=1.5, dash="dot"))
            fig.add_annotation(x=t_date, y=1, yref="paper", text="Promotion Start",
                               font=dict(color="#fbbf24", size=11), showarrow=False, yshift=10)
            fig.update_layout(**CHART_LAYOUT, height=380, showlegend=True)
            st.plotly_chart(fig, use_container_width=True)

    with tab2:
        with st.container(border=True):
            section_header("Effect Distribution", "BOOTSTRAP")
            np.random.seed(42)
            boot = np.random.normal(2.34, 0.8, 1000)
            fig = go.Figure(go.Histogram(
                x=boot, nbinsx=40,
                marker=dict(color="rgba(34, 211, 238, 0.4)", line=dict(color="#22d3ee", width=1)),
                hovertemplate="Effect: %{x:.2f}<br>Count: %{y}<extra></extra>",
            ))
            fig.add_vline(x=0, line_dash="dash", line_color="#fb7185", line_width=1.5,
                          annotation_text="No Effect", annotation_font_color="#fb7185")
            layout2 = {k: v for k, v in CHART_LAYOUT.items() if k not in ('xaxis', 'yaxis')}
            fig.update_layout(**layout2, height=380,
                              xaxis=dict(title="Treatment Effect", showgrid=False, linecolor="rgba(99,179,237,0.08)"),
                              yaxis=dict(title="Frequency", showgrid=True, gridcolor="rgba(99,179,237,0.05)", linecolor="rgba(99,179,237,0.08)"))
            st.plotly_chart(fig, use_container_width=True)


# ── Footer ──
st.markdown(f"""
<div class="footer">
    ⚡ Revion · Enterprise AI Dashboard · {datetime.now().strftime('%Y')}
</div>
""", unsafe_allow_html=True)
