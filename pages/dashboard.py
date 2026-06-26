import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

def render_page(module_name="Dashboard"):
    # ── CSS Optimization for Dashboard Data Density ──
    st.markdown("""
    <style>
        /* Typography Hierarchy Improvements */
        .breadcrumb { font-size: 0.75rem; font-weight: 700; color: var(--text-muted); text-transform: uppercase; letter-spacing: 1px; margin-bottom: 0.25rem; }
        .dashboard-title { font-size: 2rem; font-weight: 800; color: var(--text-main); letter-spacing: -0.5px; margin-bottom: 1.5rem; line-height: 1.1; }
        .section-header { font-size: 1rem; font-weight: 700; color: var(--text-main); margin: 2rem 0 1rem 0; border-bottom: 1px solid var(--border-color); padding-bottom: 0.5rem; }
        
        /* Status Ribbon */
        .status-ribbon { display: flex; gap: 2rem; background: var(--card-bg); border: 1px solid var(--border-color); border-radius: 8px; padding: 0.75rem 1.5rem; margin-bottom: 2rem; }
        .ribbon-item { display: flex; align-items: center; gap: 0.5rem; font-size: 0.8rem; font-weight: 600; color: var(--text-muted); }
        .ribbon-val { color: var(--text-main); font-weight: 700; }
        .dot-green { width: 8px; height: 8px; background: #10b981; border-radius: 50%; box-shadow: 0 0 8px #10b981; }
        .dot-amber { width: 8px; height: 8px; background: #f59e0b; border-radius: 50%; }

        /* KPI Cards Contextual Redesign */
        .kpi-container { background: var(--card-bg); border: 1px solid var(--border-color); border-radius: 8px; padding: 1.25rem; transition: all 0.2s ease; cursor: default; }
        .kpi-container:hover { border-color: var(--text-muted); transform: translateY(-2px); box-shadow: 0 8px 15px rgba(0,0,0,0.05); }
        .kpi-top { display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem; }
        .kpi-label { font-size: 0.8rem; font-weight: 600; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.5px; }
        .kpi-icon { width: 32px; height: 32px; border-radius: 6px; background: rgba(255,255,255,0.05); display: flex; align-items: center; justify-content: center; font-size: 1rem; border: 1px solid var(--border-color); }
        .kpi-value { font-size: 2rem; font-weight: 800; color: var(--text-main); line-height: 1; margin-bottom: 0.5rem; }
        .kpi-trend { font-size: 0.75rem; font-weight: 600; display: flex; align-items: center; gap: 0.25rem; }
        .trend-up { color: #10b981; background: rgba(16,185,129,0.1); padding: 2px 6px; border-radius: 4px; }
        .trend-down { color: #ef4444; background: rgba(239,68,68,0.1); padding: 2px 6px; border-radius: 4px; }
        .trend-desc { color: var(--text-muted); font-weight: 500; }
        
        /* Chart Container */
        .chart-card { background: var(--card-bg); border: 1px solid var(--border-color); border-radius: 8px; padding: 1rem; }
    </style>
    """, unsafe_allow_html=True)

    # ── Hierarchy: Breadcrumb & Title ──
    st.markdown(f"<div class='breadcrumb'>Workspace / {module_name}</div>", unsafe_allow_html=True)
    st.markdown("<div class='dashboard-title'>Command Center</div>", unsafe_allow_html=True)

    # ── Operational Context: Status Ribbon ──
    st.markdown("""
        <div class='status-ribbon'>
            <div class='ribbon-item'><div class='dot-green'></div> System: <span class='ribbon-val'>Operational</span></div>
            <div class='ribbon-item'><div class='dot-green'></div> Fleet Ready: <span class='ribbon-val'>94%</span></div>
            <div class='ribbon-item'><div class='dot-amber'></div> Active Dispatches: <span class='ribbon-val'>18</span></div>
            <div class='ribbon-item' style='margin-left: auto; color: #10b981;'>Live Sync Active ⚡</div>
        </div>
    """, unsafe_allow_html=True)

    # ── Quick Actions (Workflow Shortcuts) ──
    qa_c1, qa_c2, qa_c3, qa_c4 = st.columns(4)
    qa_c1.button("➕ Create Shipment", use_container_width=True, type="primary")
    qa_c2.button("🚚 Assign Fleet", use_container_width=True)
    qa_c3.button("📄 Generate Report", use_container_width=True)
    qa_c4.button("🔍 Search Records", use_container_width=True)

    st.markdown("<div class='section-header'>Network Overview</div>", unsafe_allow_html=True)

    # ── High-Level Contextual KPIs ──
    kpi_c1, kpi_c2, kpi_c3, kpi_c4 = st.columns(4)
    
    with kpi_c1:
        st.markdown("""
        <div class='kpi-container'>
            <div class='kpi-top'><span class='kpi-label'>Total Orders</span><div class='kpi-icon'>📦</div></div>
            <div class='kpi-value'>1,248</div>
            <div class='kpi-trend'><span class='trend-up'>↑ 12.5%</span> <span class='trend-desc'>vs yesterday</span></div>
        </div>
        """, unsafe_allow_html=True)
        
    with kpi_c2:
        st.markdown("""
        <div class='kpi-container'>
            <div class='kpi-top'><span class='kpi-label'>Active Fleet</span><div class='kpi-icon'>🚚</div></div>
            <div class='kpi-value'>342</div>
            <div class='kpi-trend'><span class='trend-up'>↑ 4.1%</span> <span class='trend-desc'>utilization</span></div>
        </div>
        """, unsafe_allow_html=True)
        
    with kpi_c3:
        st.markdown("""
        <div class='kpi-container'>
            <div class='kpi-top'><span class='kpi-label'>Delayed</span><div class='kpi-icon'>⚠️</div></div>
            <div class='kpi-value'>12</div>
            <div class='kpi-trend'><span class='trend-down'>↓ 2.0%</span> <span class='trend-desc'>improving</span></div>
        </div>
        """, unsafe_allow_html=True)
        
    with kpi_c4:
        st.markdown("""
        <div class='kpi-container'>
            <div class='kpi-top'><span class='kpi-label'>Revenue (PKR)</span><div class='kpi-icon'>💵</div></div>
            <div class='kpi-value'>4.2M</div>
            <div class='kpi-trend'><span class='trend-up'>↑ 8.3%</span> <span class='trend-desc'>vs last week</span></div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div class='section-header'>Analytical Insights</div>", unsafe_allow_html=True)

    # ── Lightweight Data Visualizations (Plotly) ──
    # Determine chart theme colors based on Streamlit state
    chart_bg = 'rgba(0,0,0,0)'
    text_col = '#f8fafc' if st.session_state.theme == 'dark' else '#0f172a'
    grid_col = 'rgba(255,255,255,0.05)' if st.session_state.theme == 'dark' else 'rgba(0,0,0,0.05)'

    chart_c1, chart_c2 = st.columns([6, 4], gap="large")

    with chart_c1:
        st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
        # Dummy Data for 7-Day Trend
        dates = [(datetime.now() - timedelta(days=i)).strftime('%b %d') for i in range(6, -1, -1)]
        volumes = [150, 180, 175, 210, 250, 240, 310]
        df_trend = pd.DataFrame({'Date': dates, 'Volume': volumes})
        
        fig1 = px.line(df_trend, x='Date', y='Volume', title='7-Day Shipment Volume', markers=True)
        fig1.update_traces(line_color='#10b981', line_width=3, marker=dict(size=8, color='#10b981'))
        fig1.update_layout(
            paper_bgcolor=chart_bg, plot_bgcolor=chart_bg, font_color=text_col,
            margin=dict(l=20, r=20, t=40, b=20), height=300,
            xaxis=dict(showgrid=False, title=""), yaxis=dict(gridcolor=grid_col, title="")
        )
        st.plotly_chart(fig1, use_container_width=True, config={'displayModeBar': False})
        st.markdown("</div>", unsafe_allow_html=True)

    with chart_c2:
        st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
        # Dummy Data for Fleet Distribution
        df_fleet = pd.DataFrame({'Status': ['In Transit', 'Loading', 'Maintenance', 'Idle'], 'Count': [210, 85, 12, 35]})
        
        fig2 = px.pie(df_fleet, values='Count', names='Status', hole=0.7, title='Live Fleet Distribution')
        fig2.update_traces(marker=dict(colors=['#3b82f6', '#10b981', '#ef4444', '#64748b']), textinfo='none')
        fig2.update_layout(
            paper_bgcolor=chart_bg, font_color=text_col,
            margin=dict(l=20, r=20, t=40, b=20), height=300,
            showlegend=True, legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
        )
        st.plotly_chart(fig2, use_container_width=True, config={'displayModeBar': False})
        st.markdown("</div>", unsafe_allow_html=True)