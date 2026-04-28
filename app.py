"""
⚡ FCAS Bidding Bot — Streamlit Web App
ML-optimized FCAS bid strategy for BESS in the Australian NEM.

Launch: streamlit run app.py --server.address 0.0.0.0
"""
import os, pickle, time
from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

# ── Page Config ──────────────────────────────────────────────────────
st.set_page_config(
    page_title="⚡ FCAS Bidding Bot",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── FCAS Metadata ────────────────────────────────────────────────────
FCAS_META = {
    'RAISE6SEC':  {'short': 'R6S',  'color': '#ff6b6b'},
    'RAISE60SEC': {'short': 'R60S', 'color': '#ffa502'},
    'RAISE5MIN':  {'short': 'R5M',  'color': '#ffd166'},
    'RAISEREG':   {'short': 'RREG', 'color': '#ff6348'},
    'LOWER6SEC':  {'short': 'L6S',  'color': '#4488ff'},
    'LOWER60SEC': {'short': 'L60S', 'color': '#00d2d3'},
    'LOWER5MIN':  {'short': 'L5M',  'color': '#48dbfb'},
    'LOWERREG':   {'short': 'LREG', 'color': '#0abde3'},
}

# ── Sidebar ──────────────────────────────────────────────────────────
st.sidebar.title("⚡ FCAS Bidding Bot")
st.sidebar.markdown("---")

st.sidebar.header("🎛️ Configuration")
nem_region = st.sidebar.selectbox("NEM Region", ["SA1", "VIC1", "NSW1", "QLD1", "TAS1"], index=0)
target_year = st.sidebar.number_input("Target Year", 2023, 2026, 2025)
target_month = st.sidebar.selectbox("Target Month", list(range(1, 13)), index=0)

st.sidebar.markdown("---")
st.sidebar.header("🔋 BESS Parameters")
bess_power = st.sidebar.slider("Power (MW)", 10, 500, 100, 10)
bess_capacity = st.sidebar.slider("Capacity (MWh)", 20, 1000, 200, 20)
bess_eta = st.sidebar.slider("Round-trip Efficiency (%)", 80, 98, 90, 1)
soc_min = st.sidebar.slider("SoC Min (%)", 5, 30, 10, 5)
soc_max = st.sidebar.slider("SoC Max (%)", 70, 95, 90, 5)

st.sidebar.markdown("---")
st.sidebar.header("📊 FCAS Services")
active_services = []
for svc, meta in FCAS_META.items():
    if st.sidebar.checkbox(meta['short'], value=True, key=svc):
        active_services.append(svc)

# ── Load Results ─────────────────────────────────────────────────────
@st.cache_data
def load_results():
    """Load pre-computed results from CSV files."""
    results = {}
    for fname, key in [
        ('outputs/fcas_price_forecast.csv', 'forecast'),
        ('outputs/fcas_bid_schedule.csv', 'bids'),
        ('outputs/fcas_revenue.csv', 'revenue'),
        ('outputs/soc_trace.csv', 'soc'),
    ]:
        if Path(fname).exists():
            df = pd.read_csv(fname, index_col=0, parse_dates=True)
            results[key] = df
    return results

results = load_results()

# ── Main Content ─────────────────────────────────────────────────────
st.title("⚡ FCAS Bidding Bot")
st.markdown(f"**Region:** {nem_region} | **Target:** {target_year}-{target_month:02d} | "
            f"**BESS:** {bess_power} MW / {bess_capacity} MWh")

if not results:
    st.warning("No pre-computed results found. Run the notebook first to generate outputs.")
    st.info("```\njupyter notebook FCAS_Bidding_Bot.ipynb\n```")
    st.stop()

# ── KPI Row ──────────────────────────────────────────────────────────
if 'revenue' in results:
    rev = results['revenue']
    fcas_cols = [c for c in rev.columns if c in FCAS_META]
    total_rev = rev['total'].sum() if 'total' in rev.columns else rev.sum().sum()
    fcas_rev = rev[fcas_cols].sum().sum() if fcas_cols else 0
    energy_rev = rev['energy'].sum() if 'energy' in rev.columns else 0

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Revenue", f"${total_rev:,.0f}")
    col2.metric("FCAS Revenue", f"${fcas_rev:,.0f}")
    col3.metric("Energy Revenue", f"${energy_rev:,.0f}")
    col4.metric("FCAS Share", f"{fcas_rev/max(total_rev,1)*100:.1f}%")

st.markdown("---")

# ── Tab Layout ───────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(["📈 FCAS Forecast", "🎯 Bid Schedule", "💰 Revenue", "📊 Day Detail"])

with tab1:
    st.subheader("FCAS Price Forecast")
    if 'forecast' in results:
        fc = results['forecast']
        fig = go.Figure()
        for svc in active_services:
            if svc in fc.columns:
                fig.add_trace(go.Scatter(
                    x=fc.index, y=fc[svc],
                    name=FCAS_META[svc]['short'],
                    line=dict(color=FCAS_META[svc]['color'], width=1),
                ))
        fig.update_layout(
            template='plotly_dark',
            title=f'FCAS Price Forecast — {nem_region}',
            yaxis_title='FCAS Price ($/MWh)',
            height=500,
        )
        st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.subheader("FCAS Bid Allocation")
    if 'bids' in results:
        bids = results['bids']
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                            subplot_titles=['Raise Services (MW)', 'Lower Services (MW)'])
        for svc in active_services:
            if svc in bids.columns:
                row = 1 if 'RAISE' in svc else 2
                fig.add_trace(go.Scatter(
                    x=bids.index, y=bids[svc],
                    name=FCAS_META[svc]['short'],
                    fill='tonexty' if row == 1 else 'tozeroy',
                    line=dict(color=FCAS_META[svc]['color'], width=0.5),
                ), row=row, col=1)
        fig.update_layout(template='plotly_dark', height=600)
        st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.subheader("Revenue Analysis")
    if 'revenue' in results:
        rev = results['revenue']

        # Cumulative revenue
        fig = go.Figure()
        if 'total' in rev.columns:
            fig.add_trace(go.Scatter(
                x=rev.index, y=rev['total'].cumsum(),
                name='Total', line=dict(color='#00e676', width=2),
            ))
        fcas_cum = rev[[c for c in rev.columns if c in FCAS_META]].sum(axis=1).cumsum()
        fig.add_trace(go.Scatter(
            x=rev.index, y=fcas_cum,
            name='FCAS', line=dict(color='#c084fc', width=1.5),
        ))
        fig.update_layout(
            template='plotly_dark',
            title='Cumulative Revenue ($)',
            yaxis_title='Revenue ($)',
            height=400,
        )
        st.plotly_chart(fig, use_container_width=True)

        # Revenue by service (bar)
        svc_rev = {FCAS_META[s]['short']: rev[s].sum() for s in active_services if s in rev.columns}
        if 'energy' in rev.columns:
            svc_rev['Energy'] = rev['energy'].sum()
        fig2 = px.bar(
            x=list(svc_rev.keys()), y=list(svc_rev.values()),
            color=list(svc_rev.keys()),
            title='Revenue by Source ($)',
            template='plotly_dark',
        )
        fig2.update_layout(height=400)
        st.plotly_chart(fig2, use_container_width=True)

with tab4:
    st.subheader("Day Detail View")
    if 'forecast' in results:
        fc = results['forecast']
        available_dates = sorted(set(fc.index.date))
        selected_date = st.date_input(
            "Select Date",
            value=available_dates[len(available_dates)//2] if available_dates else None,
            min_value=available_dates[0] if available_dates else None,
            max_value=available_dates[-1] if available_dates else None,
        )
        
        if selected_date:
            mask = fc.index.date == selected_date
            d_fc = fc[mask]
            
            if len(d_fc) > 0:
                fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                                    subplot_titles=['FCAS Prices', 'Bid Allocation'])
                for svc in active_services:
                    if svc in d_fc.columns:
                        fig.add_trace(go.Scatter(
                            x=d_fc.index, y=d_fc[svc],
                            name=FCAS_META[svc]['short'],
                            line=dict(color=FCAS_META[svc]['color']),
                        ), row=1, col=1)
                
                if 'bids' in results:
                    d_bids = results['bids'][results['bids'].index.date == selected_date]
                    for svc in active_services:
                        if svc in d_bids.columns:
                            fig.add_trace(go.Bar(
                                x=d_bids.index, y=d_bids[svc],
                                name=f'Bid {FCAS_META[svc]["short"]}',
                                marker_color=FCAS_META[svc]['color'],
                                opacity=0.7,
                            ), row=2, col=1)
                
                fig.update_layout(template='plotly_dark', height=600)
                st.plotly_chart(fig, use_container_width=True)

# ── Download Section ─────────────────────────────────────────────────
st.markdown("---")
st.subheader("📥 Download Results")
col1, col2, col3 = st.columns(3)

for col, (fname, label) in zip(
    [col1, col2, col3],
    [('outputs/fcas_price_forecast.csv', 'FCAS Forecast'),
     ('outputs/fcas_bid_schedule.csv', 'Bid Schedule'),
     ('outputs/fcas_revenue.csv', 'Revenue')]):
    if Path(fname).exists():
        with open(fname, 'r') as f:
            col.download_button(f"⬇️ {label}", f.read(), fname.split('/')[-1], 'text/csv')

st.sidebar.markdown("---")
st.sidebar.info("Built with Master ML/DL Framework — 12 Steps, 5 Phases")
