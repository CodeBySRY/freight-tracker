import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from services.reporting_service import (
    fetch_shipment_status_distribution,
    fetch_orders_timeline,
    fetch_carrier_utilization,
    fetch_delivery_performance,
)

# ─── SHARED PLOTLY LAYOUT ────────────────────────────────────────────────────
_PLOTLY_BASE = dict(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(color='#94a3b8', family='Plus Jakarta Sans', size=12),
    margin=dict(t=10, b=10, l=0, r=0),
)

STATUS_COLORS = {
    'Delivered': '#10b981',
    'In Transit': '#3b82f6',
    'Delayed': '#f59e0b',
    'Cancelled': '#ef4444',
    'Pending': '#64748b',
    'On Time': '#10b981',
    'Late': '#f59e0b',
    'In Progress': '#3b82f6',
}

GRID_COLOR = '#1e293b'


def _chart_wrapper(title: str, subtitle: str = ""):
    html = f"""
    <div style='margin-bottom:0.5rem;'>
        <div style='color:#f8fafc;font-size:0.95rem;font-weight:700;'>{title}</div>
        {'<div style="color:#475569;font-size:0.78rem;margin-top:2px;">' + subtitle + '</div>' if subtitle else ''}
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def render_page():
    # ── Page header ──────────────────────────────────────────────────────────
    st.markdown("""
        <div style='margin-bottom:1.75rem;'>
            <div style='color:#475569;font-size:0.7rem;font-weight:800;letter-spacing:1.5px;text-transform:uppercase;margin-bottom:4px;'>INTELLIGENCE</div>
            <h2 style='color:#f8fafc;font-weight:800;font-size:1.75rem;margin:0;letter-spacing:-0.5px;'>Business Analytics</h2>
            <p style='color:#64748b;font-size:0.88rem;margin:4px 0 0 0;'>Network health, carrier performance, and operational trends.</p>
        </div>
    """, unsafe_allow_html=True)

    # ── Fetch all data ────────────────────────────────────────────────────────
    df_status  = fetch_shipment_status_distribution()
    df_trends  = fetch_orders_timeline()
    df_carriers = fetch_carrier_utilization()
    df_perf    = fetch_delivery_performance()

    # ── ROW 1: Status donut + Delivery performance ────────────────────────────
    col1, col2 = st.columns(2, gap="medium")

    with col1:
        _chart_wrapper("Shipment Status Distribution", "Breakdown by current state across all shipments")
        if not df_status.empty:
            fig = px.pie(
                df_status, values='count', names='status', hole=0.60,
                color='status', color_discrete_map=STATUS_COLORS,
            )
            total = int(df_status['count'].sum())
            fig.add_annotation(
                text=f"<b>{total}</b><br><span style='font-size:10px'>TOTAL</span>",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=18, color='#f8fafc', family='Plus Jakarta Sans'),
            )
            fig.update_layout(
                **_PLOTLY_BASE,
                showlegend=True,
                legend=dict(orientation="h", x=0.5, xanchor="center", y=-0.1,
                            font=dict(color='#94a3b8', size=11)),
                height=300,
            )
            fig.update_traces(
                textposition='outside', textinfo='percent+label',
                textfont=dict(color='#cbd5e1', size=10),
                marker=dict(line=dict(color='#020617', width=2)),
                hovertemplate='<b>%{label}</b><br>Count: %{value}<br>%{percent}<extra></extra>',
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No shipment data available yet.")

    with col2:
        _chart_wrapper("Delivery Performance", "On-time, delayed, and in-progress breakdown")
        if not df_perf.empty:
            fig2 = px.bar(
                df_perf, x='count', y='performance', orientation='h',
                color='performance', color_discrete_map=STATUS_COLORS,
                text='count',
            )
            fig2.update_traces(
                textposition='outside',
                textfont=dict(color='#cbd5e1', size=12),
                marker_line_width=0,
            )
            fig2.update_layout(
                **_PLOTLY_BASE,
                showlegend=False, height=300,
                xaxis=dict(showgrid=True, gridcolor=GRID_COLOR, zeroline=False, title=''),
                yaxis=dict(showgrid=False, title=''),
                bargap=0.35,
            )
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("No delivery performance data available yet.")

    st.markdown("<hr style='border:none;border-top:1px solid #1e293b;margin:1.25rem 0;'>", unsafe_allow_html=True)

    # ── ROW 2: Orders timeline ────────────────────────────────────────────────
    _chart_wrapper("Expected Delivery Timeline", "Volume of orders by scheduled delivery date")
    if not df_trends.empty:
        fig3 = go.Figure()
        fig3.add_trace(go.Bar(
            x=df_trends['date'],
            y=df_trends['orders'],
            marker_color='#10b981',
            marker_line_color='#065f46',
            marker_line_width=1,
            opacity=0.85,
            hovertemplate='<b>%{x}</b><br>Orders: %{y}<extra></extra>',
        ))
        fig3.update_layout(
            **_PLOTLY_BASE,
            height=220,
            xaxis=dict(showgrid=False, title='', tickfont=dict(color='#64748b', size=11)),
            yaxis=dict(showgrid=True, gridcolor=GRID_COLOR, zeroline=False, title='Orders', tickfont=dict(color='#64748b', size=11)),
            bargap=0.25,
        )
        st.plotly_chart(fig3, use_container_width=True)
    else:
        st.info("No order timeline data available yet.")

    st.markdown("<hr style='border:none;border-top:1px solid #1e293b;margin:1.25rem 0;'>", unsafe_allow_html=True)

    # ── ROW 3: Carrier utilization ────────────────────────────────────────────
    _chart_wrapper("Carrier Utilization", "Total shipments handled per carrier, with delivery outcomes")
    if not df_carriers.empty:
        fig4 = go.Figure()
        fig4.add_trace(go.Bar(
            name='Delivered',
            x=df_carriers['carrier'],
            y=df_carriers['delivered'],
            marker_color='#10b981',
            marker_line_width=0,
            hovertemplate='<b>%{x}</b><br>Delivered: %{y}<extra></extra>',
        ))
        fig4.add_trace(go.Bar(
            name='In Transit',
            x=df_carriers['carrier'],
            y=df_carriers['in_transit'],
            marker_color='#3b82f6',
            marker_line_width=0,
            hovertemplate='<b>%{x}</b><br>In Transit: %{y}<extra></extra>',
        ))
        fig4.update_layout(
            **_PLOTLY_BASE,
            barmode='stack',
            height=280,
            showlegend=True,
            legend=dict(orientation="h", x=0.5, xanchor="center", y=1.08,
                        font=dict(color='#94a3b8', size=11)),
            xaxis=dict(showgrid=False, title='', tickfont=dict(color='#64748b', size=11)),
            yaxis=dict(showgrid=True, gridcolor=GRID_COLOR, zeroline=False,
                       title='Shipments', tickfont=dict(color='#64748b', size=11)),
            bargap=0.3,
        )
        st.plotly_chart(fig4, use_container_width=True)

        # Carrier status pills below chart
        st.markdown("<div style='display:flex;flex-wrap:wrap;gap:0.5rem;margin-top:0.5rem;'>", unsafe_allow_html=True)
        pill_html = ""
        for _, row in df_carriers.iterrows():
            color = "#10b981" if row['current_status'] == 'Available' else "#f59e0b"
            bg    = "#022c22" if row['current_status'] == 'Available' else "#451a03"
            pill_html += f"<span style='background:{bg};color:{color};border:1px solid {color}33;border-radius:20px;padding:3px 12px;font-size:0.75rem;font-weight:700;'>{row['carrier']} · {row['current_status']}</span>"
        st.markdown(f"<div style='display:flex;flex-wrap:wrap;gap:0.5rem;'>{pill_html}</div>", unsafe_allow_html=True)
    else:
        st.info("No carrier data available yet.")
