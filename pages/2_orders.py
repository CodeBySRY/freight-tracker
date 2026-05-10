import streamlit as st
import pandas as pd
from database import get_db
from datetime import date

if 'user' not in st.session_state or st.session_state.user is None:
    st.switch_page("app.py")

user = st.session_state.user

st.title("Freight Command Center")
st.write("Live control panel for order assignment, tracking, and logistics auditing.")

conn = get_db()
cur = conn.cursor()

# ─── THE SCALABILITY FIX: SEARCH & FILTERS ─────────────────────────────
col_f1, col_f2 = st.columns([3, 1])
with col_f1:
    search_query = st.text_input("🔍 Search by Customer, Origin, or Destination...", placeholder="e.g., Pharma & Co, Karachi...")
with col_f2:
    status_filter = st.selectbox("Filter by Status", ["All Orders", "Unassigned", "In Transit", "Delivered", "Cancelled"])

# Dynamic SQL based on filters
base_query = """
    SELECT o.order_id, o.customer_name, o.origin_city, o.destination_city, 
           o.cargo_description, o.expected_delivery_date, o.priority, 
           o.cargo_weight_kg, o.cargo_type, o.special_instructions,
           c.company_name AS carrier_name, s.status, s.shipment_id, 
           o.created_at, o.is_cancelled
    FROM orders o
    LEFT JOIN shipments s ON o.order_id = s.order_id
    LEFT JOIN carriers c ON s.carrier_id = c.carrier_id
    WHERE 1=1
"""
params = []

if search_query:
    base_query += " AND (o.customer_name ILIKE %s OR o.origin_city ILIKE %s OR o.destination_city ILIKE %s)"
    params.extend([f"%{search_query}%", f"%{search_query}%", f"%{search_query}%"])

if status_filter != "All Orders":
    if status_filter == "Unassigned":
        base_query += " AND s.shipment_id IS NULL AND o.is_cancelled = FALSE"
    elif status_filter == "Cancelled":
        base_query += " AND o.is_cancelled = TRUE"
    else:
        base_query += " AND s.status = %s AND o.is_cancelled = FALSE"
        params.append(status_filter)

base_query += " ORDER BY o.created_at DESC"

cur.execute(base_query, tuple(params))
orders_data = cur.fetchall()

# ─── THE ADMIN EDIT DIALOG (Streamlit Pop-up) ──────────────────────────
@st.dialog("Edit Unassigned Order")
def edit_order_dialog(order):
    with st.form(key=f"edit_form_{order['order_id']}"):
        st.caption("Update routing or cargo details. This action cannot be undone.")
        new_customer = st.text_input("Customer Name", value=order['customer_name'])
        new_eta = st.date_input("Expected Delivery Date", value=order['expected_delivery_date'])
        new_instructions = st.text_area("Special Instructions", value=order['special_instructions'])
        
        if st.form_submit_button("Save Changes", type="primary"):
            try:
                cur.execute("""
                    UPDATE orders 
                    SET customer_name = %s, expected_delivery_date = %s, special_instructions = %s 
                    WHERE order_id = %s
                """, (new_customer, new_eta, new_instructions, order['order_id']))
                conn.commit()
                st.success("Order updated successfully!")
                st.rerun()
            except Exception as e:
                st.error(f"Failed to update: {e}")

# ─── COMMAND PANEL RENDER LOGIC ────────────────────────────────────────
if not orders_data:
    st.info("No freight orders match your current filters.")
else:
    col1, col2, col3, col4, col5 = st.columns([1, 2, 2, 1.5, 1.5])
    col1.caption("Order #")
    col2.caption("Customer")
    col3.caption("Route")
    col4.caption("Status")
    col5.caption("ETA (Days Remaining)")
    st.divider()

    for order in orders_data:
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

        col1, col2, col3, col4, col5 = st.columns([1, 2, 2, 1.5, 1.5])
        col1.write(f"**#{order['order_id']}**")
        col2.write(order['customer_name'])
        col3.write(f"{order['origin_city']} → {order['destination_city']}")
        
        badge_style = "display: inline-block; padding: 0.25rem 0.75rem; border-radius: 9999px; font-size: 0.8rem; font-weight: 600;"
        if status_text == 'Unassigned':
            color = "#ff8c00"
        elif status_text == 'Delivered':
            color = "#22c55e"
        elif status_text == 'In Transit':
            color = "#00d4ff"
        else:
            color = "#ef4444"
        col4.markdown(f"<span style='{badge_style} background-color: {color}1A; color: {color};'>{status_text}</span>", unsafe_allow_html=True)
        col5.write(eta_display)

        with st.expander("View Cargo Details, Actions & Audit Log"):
            # --- 1. Cargo Metrics ---
            st.markdown("#### Cargo Breakdown")
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Weight (kg)", f"{order['cargo_weight_kg'] or 0:.2f}")
            c2.metric("Type", order['cargo_type'] or "N/A")
            c3.metric("Priority", order['priority'] or "Standard")
            c4.metric("Carrier Partner", order['carrier_name'] or "None Assigned")
            st.write(f"**General Description:** {order['cargo_description']}")
            if order['special_instructions']:
                st.info(f"**Special Instructions:** {order['special_instructions']}")
            st.divider()

            # --- 2. Action & Audit Area ---
            if order['is_cancelled']:
                st.error("This order has been permanently cancelled.")
                
            elif not order['shipment_id']:
                # UNASSIGNED STATE
                st.markdown("#### Dispatch Assignment")
                
                # FEATURE 5 FIX: Admin Edit & Cancel
                if user['role'] == 'Admin':
                    btn_col1, btn_col2 = st.columns([1, 1])
                    with btn_col1:
                        if st.button("✏️ Edit Order", key=f"edit_{order['order_id']}", use_container_width=True):
                            edit_order_dialog(order)
                    with btn_col2:
                        if st.button("🚫 Cancel Order", key=f"cancel_{order['order_id']}", use_container_width=True):
                            cur.execute("UPDATE orders SET is_cancelled = TRUE WHERE order_id = %s", (order['order_id'],))
                            conn.commit()
                            st.rerun()
                    st.write("") # spacing

                if user['role'] != 'Warehouse':
                    with st.form(key=f"assign_{order['order_id']}"):
                        cur.execute("SELECT carrier_id, company_name, vehicle_type FROM carriers WHERE is_available = TRUE")
                        avail_carriers = cur.fetchall()
                        
                        if avail_carriers:
                            carrier_options = {c['carrier_id']: f"{c['company_name']} ({c['vehicle_type']})" for c in avail_carriers}
                            selected_carrier = st.selectbox("Select Logistics Partner", options=list(carrier_options.keys()), format_func=lambda x: carrier_options[x])
                            
                            if st.form_submit_button("Confirm Assignment", type="primary"):
                                try:
                                    cur.execute("BEGIN")
                                    cur.execute("""
                                        INSERT INTO shipments (order_id, carrier_id, status, assigned_at) 
                                        VALUES (%s, %s, 'Pending', CURRENT_TIMESTAMP) RETURNING shipment_id
                                    """, (order['order_id'], selected_carrier))
                                    new_ship_id = cur.fetchone()['shipment_id']
                                    
                                    cur.execute("""
                                        INSERT INTO status_log (shipment_id, new_status, changed_by, notes) 
                                        VALUES (%s, 'Pending', %s, 'Initial dispatch assignment.')
                                    """, (new_ship_id, user['user_id']))
                                    
                                    cur.execute("COMMIT")
                                    st.rerun()
                                except Exception as e:
                                    cur.execute("ROLLBACK")
                                    st.error(f"Transaction failed: {e}")
                        else:
                            st.warning("No available carriers to assign. Check Fleet Management.")

            else:
                # ASSIGNED STATE: Show Timeline and Status Updater
                st.markdown("#### Status History Audit Log")
                cur.execute("""
                    SELECT sl.old_status, sl.new_status, sl.changed_at, sl.notes, u.full_name
                    FROM status_log sl
                    JOIN users u ON sl.changed_by = u.user_id
                    WHERE sl.shipment_id = %s
                    ORDER BY sl.changed_at DESC
                """, (order['shipment_id'],))
                logs = cur.fetchall()
                
                for log in logs:
                    old_s = log['old_status'] if log['old_status'] else "Creation"
                    note_text = f" — *\"{log['notes']}\"*" if log['notes'] else ""
                    st.caption(f"**{log['changed_at'].strftime('%Y-%m-%d %H:%M')}** | **{log['full_name']}** updated from `{old_s}` to `{log['new_status']}`{note_text}")
                
                st.write("")
                
                if status_text not in ['Delivered', 'Cancelled']:
                    st.markdown("#### Perform Status Update")
                    with st.form(key=f"update_{order['order_id']}"):
                        new_status = st.selectbox("New Status", ["In Transit", "Delivered", "Cancelled"])
                        update_notes = st.text_area("Audit Notes (Optional)", help="Reason for status change, checkpoint delays, etc.")
                        
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
                                st.error(f"Status update failed: {e}")

conn.close()