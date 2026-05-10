import streamlit as st
import pandas as pd
from database import get_db
from datetime import date

if 'user' not in st.session_state or st.session_state.user is None:
    st.switch_page("app.py")

user = st.session_state.user

st.title("Freight Orders")

conn = get_db()
cur = conn.cursor()

# Fetch all orders with carrier and shipment status
cur.execute("""
    SELECT o.*, c.company_name AS carrier_name, s.status, s.shipment_id
    FROM orders o
    LEFT JOIN shipments s ON o.order_id = s.order_id
    LEFT JOIN carriers c ON s.carrier_id = c.carrier_id
    ORDER BY o.created_at DESC
""")
orders = cur.fetchall()
conn.close()

if not orders:
    st.info("No orders found. Use 'New Order' to create one.")
else:
    # Display headers for the list
    col1, col2, col3, col4, col5 = st.columns([1, 2, 2, 2, 1])
    col1.caption("Order #")
    col2.caption("Customer")
    col3.caption("Route")
    col4.caption("Status")
    col5.caption("ETA")
    st.divider()

    # Loop through orders and create an expandable card for each
    for order in orders:
        status_text = order['status'] if order['status'] else 'Unassigned'
        
        # Calculate ETA logic
        eta_display = "Not Set"
        eta_color = "normal"
        if order['expected_delivery_date']:
            days_left = (order['expected_delivery_date'] - date.today()).days
            if status_text == 'Delivered':
                eta_display = "Done"
            elif days_left < 0:
                eta_display = f":red[Overdue ({abs(days_left)}d)]"
            elif days_left == 0:
                eta_display = ":orange[Due Today]"
            else:
                eta_display = f":green[{days_left} days]"

        # Create the visible row
        col1, col2, col3, col4, col5 = st.columns([1, 2, 2, 2, 1])
        col1.write(f"**#{order['order_id']}**")
        col2.write(order['customer_name'])
        col3.write(f"{order['origin_city']} → {order['destination_city']}")
        col4.write(f"`{status_text}`")
        col5.write(eta_display)

        # Feature 1: The Cargo Details Expander
        with st.expander("View Cargo Details & Actions"):
            st.markdown("#### Cargo Breakdown")
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Weight", f"{order['cargo_weight_kg'] or 0} kg")
            c2.metric("Type", order['cargo_type'] or "N/A")
            c3.metric("Priority", order['priority'] or "Standard")
            c4.metric("Carrier", order['carrier_name'] or "None Assigned")
            
            st.write(f"**Description:** {order['cargo_description']}")
            if order['special_instructions']:
                st.info(f"**Special Instructions:** {order['special_instructions']}")
            
            # Action Buttons (Placeholder for the next phase)
            st.divider()
            if not order['shipment_id'] and user['role'] != 'Warehouse':
                st.button("Assign Carrier", key=f"assign_{order['order_id']}")
            elif order['shipment_id']:
                st.button("Update Status", key=f"status_{order['order_id']}")