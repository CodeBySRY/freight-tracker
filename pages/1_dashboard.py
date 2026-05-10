import streamlit as st
import pandas as pd
from database import get_db

# Security: Redirect to login if accessed directly
if 'user' not in st.session_state or st.session_state.user is None:
    st.switch_page("app.py")

user = st.session_state.user

st.title("Logistics Dashboard")
st.write(f"Welcome back, **{user['full_name']}**.")

# Fetch Dashboard Metrics
conn = get_db()
cur = conn.cursor()

cur.execute("SELECT COUNT(*) AS total FROM orders")
total_orders = cur.fetchone()['total']

cur.execute("SELECT COUNT(*) AS total FROM shipments WHERE status = 'In Transit'")
active_shipments = cur.fetchone()['total']

cur.execute("SELECT COUNT(*) AS total FROM shipments WHERE status = 'Delivered' AND delivered_at > NOW() - INTERVAL '7 days'")
delivered_this_week = cur.fetchone()['total']

cur.execute("""
    SELECT COUNT(*) AS total FROM orders o 
    LEFT JOIN shipments s ON o.order_id = s.order_id 
    WHERE s.shipment_id IS NULL
""")
unassigned_orders = cur.fetchone()['total']

# Build the UI using Streamlit Columns and Metrics
st.markdown("### Quick Stats")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(label="Total Orders", value=total_orders)
with col2:
    st.metric(label="Active Shipments", value=active_shipments)
with col3:
    st.metric(label="Delivered (7 Days)", value=delivered_this_week)
with col4:
    # Highlight unassigned orders in red if there are any
    delta_val = -unassigned_orders if unassigned_orders > 0 else 0
    st.metric(label="Unassigned Orders", value=unassigned_orders, delta=delta_val, delta_color="inverse")

st.divider()

# Show a quick preview of recent activity using Streamlit DataFrames
st.markdown("### Recent Orders")
cur.execute("""
    SELECT o.order_id AS "Order #", o.customer_name AS "Customer", 
           o.origin_city || ' → ' || o.destination_city AS "Route",
           COALESCE(s.status, 'Unassigned') AS "Status"
    FROM orders o
    LEFT JOIN shipments s ON o.order_id = s.order_id
    ORDER BY o.created_at DESC LIMIT 5
""")
recent_orders = cur.fetchall()
conn.close()

if recent_orders:
    # Convert to Pandas DataFrame for a beautiful, sortable UI table
    df = pd.DataFrame(recent_orders)
    # Hide the default index number column
    st.dataframe(df, hide_index=True, use_container_width=True)
else:
    st.info("No orders found in the system.")