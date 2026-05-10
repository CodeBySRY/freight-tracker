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

# Fetch all orders (excluding cancelled ones from the main view for clarity, or flag them)
cur.execute("""
    SELECT o.*, c.company_name AS carrier_name, s.status, s.shipment_id
    FROM orders o
    LEFT JOIN shipments s ON o.order_id = s.order_id
    LEFT JOIN carriers c ON s.carrier_id = c.carrier_id
    ORDER BY o.created_at DESC
""")
orders = cur.fetchall()

if not orders:
    st.info("No orders found. Use 'New Order' to create one.")
else:
    col1, col2, col3, col4, col5 = st.columns([1, 2, 2, 2, 1])
    col1.caption("Order #")
    col2.caption("Customer")
    col3.caption("Route")
    col4.caption("Status")
    col5.caption("ETA")
    st.divider()

    for order in orders:
        if order['is_cancelled']:
            status_text = "Cancelled"
            eta_display = "N/A"
        else:
            status_text = order['status'] if order['status'] else 'Unassigned'
            eta_display = "Not Set"
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

        col1, col2, col3, col4, col5 = st.columns([1, 2, 2, 2, 1])
        col1.write(f"**#{order['order_id']}**")
        col2.write(order['customer_name'])
        col3.write(f"{order['origin_city']} → {order['destination_city']}")
        col4.write(f"`{status_text}`")
        col5.write(eta_display)

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
            
            st.divider()

            # --- ACTIONS AREA ---
            if order['is_cancelled']:
                st.error("This order has been cancelled.")
                
            elif not order['shipment_id']:
                # Unassigned Order Actions
                if user['role'] == 'Admin':
                    # FEATURE 5: Admin Cancel
                    if st.button("🚫 Cancel Order", key=f"cancel_{order['order_id']}"):
                        cur.execute("UPDATE orders SET is_cancelled = TRUE WHERE order_id = %s", (order['order_id'],))
                        conn.commit()
                        st.rerun()

                if user['role'] != 'Warehouse':
                    # Assign Carrier Form
                    st.markdown("**Assign Carrier**")
                    with st.form(key=f"assign_{order['order_id']}"):
                        cur.execute("SELECT carrier_id, company_name, vehicle_type FROM carriers WHERE is_available = TRUE")
                        avail_carriers = cur.fetchall()
                        
                        carrier_options = {c['carrier_id']: f"{c['company_name']} ({c['vehicle_type']})" for c in avail_carriers}
                        selected_carrier = st.selectbox("Select Logistics Partner", options=carrier_options.keys(), format_func=lambda x: carrier_options[x])
                        
                        if st.form_submit_button("Confirm Assignment", type="primary"):
                            try:
                                cur.execute("BEGIN")
                                cur.execute("""
                                    INSERT INTO shipments (order_id, carrier_id, status, assigned_at) 
                                    VALUES (%s, %s, 'Pending', CURRENT_TIMESTAMP) RETURNING shipment_id
                                """, (order['order_id'], selected_carrier))
                                new_ship_id = cur.fetchone()['shipment_id']
                                cur.execute("""
                                    INSERT INTO status_log (shipment_id, new_status, changed_by) 
                                    VALUES (%s, 'Pending', %s)
                                """, (new_ship_id, user['user_id']))
                                cur.execute("COMMIT")
                                st.rerun()
                            except Exception as e:
                                cur.execute("ROLLBACK")
                                st.error(f"Transaction failed: {e}")

            elif order['shipment_id'] and status_text not in ['Delivered', 'Cancelled']:
                # Assigned Order Actions (Update Status)
                st.markdown("**Update Shipment Status**")
                with st.form(key=f"status_{order['order_id']}"):
                    new_status = st.selectbox("New Status", ["In Transit", "Delivered", "Cancelled"])
                    # FEATURE 6: Notes on Status Update
                    update_notes = st.text_area("Audit Notes (Optional)", help="Reason for status change, delays, etc.")
                    
                    if st.form_submit_button("Save Update", type="primary"):
                        try:
                            cur.execute("BEGIN")
                            cur.execute("UPDATE shipments SET status = %s WHERE shipment_id = %s", (new_status, order['shipment_id']))
                            if new_status == 'Delivered':
                                cur.execute("UPDATE shipments SET delivered_at = CURRENT_TIMESTAMP WHERE shipment_id = %s", (order['shipment_id'],))
                            cur.execute("""
                                INSERT INTO status_log (shipment_id, old_status, new_status, changed_by, notes) 
                                VALUES (%s, %s, %s, %s, %s)
                            """, (order['shipment_id'], status_text, new_status, user['user_id'], update_notes))
                            cur.execute("COMMIT")
                            st.rerun()
                        except Exception as e:
                            cur.execute("ROLLBACK")
                            st.error(f"Update failed: {e}")

conn.close()