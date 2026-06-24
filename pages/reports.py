import streamlit as st
import pandas as pd
import plotly.express as px
from database import get_db

def render_page():
    st.markdown("<h2 style='font-weight: 800; color: #f8fafc; margin-bottom: 0.5rem;'>📊 Business Intelligence</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #94a3b8; font-size: 0.95rem; margin-bottom: 1.5rem;'>Live analytics, network health, and carrier utilization metrics.</p>", unsafe_allow_html=True)
    
    conn = get_db()
    
    try:
        # Fetch status distribution for Pie Chart
        df_status = pd.read_sql("SELECT status, COUNT(*) as count FROM shipments GROUP BY status", conn)
        
        # FIX: Switched to 'expected_delivery_date' as 'created_at' does not exist in the schema
        df_trends = pd.read_sql("SELECT expected_delivery_date as date, COUNT(*) as orders FROM orders GROUP BY expected_delivery_date ORDER BY expected_delivery_date", conn)
        
    except Exception as e:
        st.error(f"Analytics Engine Error: {e}")
        df_status = pd.DataFrame()
        df_trends = pd.DataFrame()
    finally:
        conn.close()

    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("<h4 style='color: #f8fafc; font-size: 1.1rem; font-family: \"Plus Jakarta Sans\";'>Shipment Status Distribution</h4>", unsafe_allow_html=True)
        if not df_status.empty:
            color_map = {'Delivered': '#10b981', 'In Transit': '#3b82f6', 'Delayed': '#f59e0b', 'Cancelled': '#ef4444', 'Pending': '#64748b'}
            fig1 = px.pie(df_status, values='count', names='status', hole=0.6, color='status', color_discrete_map=color_map)
            fig1.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='#94a3b8', family="Plus Jakarta Sans"), showlegend=False, margin=dict(t=20, b=20, l=0, r=0))
            fig1.update_traces(textposition='outside', textinfo='percent+label', marker=dict(line=dict(color='#0f172a', width=2)))
            st.plotly_chart(fig1, use_container_width=True)
        else:
            st.info("Insufficient data to render distribution.")

    with col2:
        st.markdown("<h4 style='color: #f8fafc; font-size: 1.1rem; font-family: \"Plus Jakarta Sans\";'>Expected Deliveries Timeline</h4>", unsafe_allow_html=True)
        if not df_trends.empty:
            fig2 = px.bar(df_trends, x='date', y='orders')
            fig2.update_traces(marker_color='#10b981', marker_line_color='#065f46', marker_line_width=1.5, opacity=0.8)
            fig2.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='#94a3b8', family="Plus Jakarta Sans"), xaxis_title="", yaxis_title="Orders Scheduled", margin=dict(t=20, b=20, l=0, r=0))
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("Insufficient data to render trends.")