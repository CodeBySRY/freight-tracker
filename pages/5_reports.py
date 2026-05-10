import streamlit as st
import pandas as pd
from database import get_db

# Security & RBAC: Redirect if not logged in or wrong role
if 'user' not in st.session_state or st.session_state.user is None:
    st.switch_page("app.py")

user = st.session_state.user
if user['role'] not in ['Admin', 'Dispatcher']:
    st.error("Access Denied. You do not have clearance to view analytics.")
    st.stop()

st.title("📊 Analytics & Reporting")
st.markdown("Real-time logistical performance and fleet metrics.")
st.write("") # Spacer

conn = get_db()
cur = conn.cursor()

# UI Polish: Using Tabs to organize data cleanly instead of a long scrolling page
tab1, tab2, tab3, tab4 = st.tabs([
    "📈 Carrier Performance", 
    "📅 Weekly Deliveries", 
    "🚨 Overdue Orders", 
    "🚚 Active Shipments"
])

# --- TAB 1: Carrier Performance ---
with tab1:
    st.subheader("Carrier Success Rates")
    cur.execute("""
        SELECT c.company_name, 
               COUNT(s.shipment_id) AS total_jobs, 
               COUNT(*) FILTER (WHERE s.status = 'Delivered') AS delivered, 
               COUNT(*) FILTER (WHERE s.status = 'Cancelled') AS cancelled 
        FROM carriers c 
        LEFT JOIN shipments s ON c.carrier_id = s.carrier_id 
        GROUP BY c.company_name 
        ORDER BY delivered DESC
    """)
    perf_data = cur.fetchall()
    
    if perf_data:
        df_perf = pd.DataFrame(perf_data)
        df_perf.set_index("company_name", inplace=True)
        
        col1, col2 = st.columns([2, 1])
        with col1:
            # Render a clean, native bar chart
            st.bar_chart(df_perf[['delivered', 'cancelled']], color=["#22c55e", "#ef4444"])
        with col2:
            st.dataframe(df_perf, use_container_width=True)
    else:
        st.info("Not enough data to generate carrier performance metrics.")

# --- TAB 2: Weekly Deliveries ---
with tab2:
    st.subheader("Delivery Trends (Last 28 Days)")
    cur.execute("""
        SELECT DATE_TRUNC('week', delivered_at)::DATE AS week, 
               COUNT(*) AS deliveries 
        FROM shipments 
        WHERE status = 'Delivered' AND delivered_at >= NOW() - INTERVAL '28 days' 
        GROUP BY DATE_TRUNC('week', delivered_at) 
        ORDER BY week
    """)
    trend_data = cur.fetchall()
    
    if trend_data:
        df_trend = pd.DataFrame(trend_data)
        df_trend.set_index("week", inplace=True)
        st.area_chart(df_trend, color="#00d4ff")
    else:
        st.info("No deliveries recorded in the last 28 days.")

# --- TAB 3: Overdue Orders ---
with tab3:
    st.subheader("Action Required: Overdue Shipments")
    cur.execute("""
        SELECT o.order_id, o.customer_name, o.expected_delivery_date, 
               CURRENT_DATE - o.expected_delivery_date AS days_overdue 
        FROM orders o 
        LEFT JOIN shipments s ON o.order_id = s.order_id 
        WHERE o.expected_delivery_date < CURRENT_DATE 
          AND (s.status IS NULL OR s.status NOT IN ('Delivered','Cancelled')) 
        ORDER BY days_overdue DESC
    """)
    overdue_data = cur.fetchall()
    
    if overdue_data:
        df_overdue = pd.DataFrame(overdue_data)
        # UI Polish: Format the dataframe to highlight the severity
        st.dataframe(
            df_overdue, 
            hide_index=True, 
            use_container_width=True,
            column_config={
                "order_id": "Order #",
                "customer_name": "Customer",
                "expected_delivery_date": st.column_config.DateColumn("Expected Date"),
                "days_overdue": st.column_config.NumberColumn("Days Overdue", format="%d days ⚠️")
            }
        )
    else:
        st.success("All clear! No orders are currently overdue.")

# --- TAB 4: Active Shipments ---
with tab4:
    st.subheader("Live Freight in Transit")
    cur.execute("""
        SELECT o.customer_name, o.origin_city || ' → ' || o.destination_city AS route, 
               c.company_name AS carrier, o.expected_delivery_date 
        FROM shipments s 
        JOIN orders o ON s.order_id = o.order_id 
        JOIN carriers c ON s.carrier_id = c.carrier_id 
        WHERE s.status = 'In Transit'
    """)
    active_data = cur.fetchall()
    
    if active_data:
        df_active = pd.DataFrame(active_data)
        st.dataframe(df_active, hide_index=True, use_container_width=True)
    else:
        st.info("No shipments are currently in transit.")

conn.close()