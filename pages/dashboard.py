import streamlit as st
import re
from database import get_db
from services.reporting_service import fetch_executive_overview

# ─── CONTEXTUAL WORKFLOWS (MODAL DIALOGS) ──────────────────────────────
@st.dialog("📦 Draft Comprehensive Freight Order")
def draft_order_dialog():
    st.markdown("<p style='color: #94a3b8; font-size: 0.9rem; margin-top: -10px;'>Create a new contract. All fields marked * are required.</p>", unsafe_allow_html=True)
    
    customer = st.text_input("Customer Name *", placeholder="e.g., Giga Group")
    col1, col2 = st.columns(2)
    with col1: origin = st.text_input("Origin City *", placeholder="e.g., Karachi")
    with col2: dest = st.text_input("Destination City *", placeholder="e.g., Islamabad")
    
    desc = st.text_input("Cargo Description", placeholder="e.g., Electronics Pallets")
    
    col3, col4 = st.columns(2)
    with col3: c_type = st.selectbox("Cargo Type", ["Standard", "Fragile", "Hazardous", "Refrigerated"])
    with col4: weight = st.number_input("Weight (kg)", min_value=0.0, step=10.5)
    
    col5, col6 = st.columns(2)
    with col5: priority = st.selectbox("Priority Level", ["Standard", "Expedited", "Overnight", "Critical"])
    with col6: exp_date = st.date_input("Expected Delivery Date")
    
    instructions = st.text_area("Special Instructions", height=68, placeholder="Gate codes, handling protocols...")
    
    if st.button("Save Order to Database", type="primary", use_container_width=True):
        if customer and origin and dest:
            conn = get_db()
            cur = conn.cursor()
            try:
                query = "INSERT INTO orders (customer_name, origin_city, destination_city, cargo_description, cargo_type, cargo_weight_kg, priority, special_instructions, expected_delivery_date, created_by) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                cur.execute(query, (customer, origin, dest, desc, c_type, weight, priority, instructions, exp_date, st.session_state.user['user_id']))
                conn.commit()
                st.success(f"Order validated and saved for {customer}!")
                st.rerun() 
            except Exception as e:
                conn.rollback()
                st.error(f"Database error: {e}")
            finally:
                conn.close()
        else:
            st.error("Customer, Origin, and Destination are mandatory fields.")

@st.dialog("🚚 Dispatch Fleet")
def dispatch_fleet_dialog():
    # ─── ZERO TRUST SECURITY CHECK ───
    if st.session_state.user['role'] not in ["System Administrator", "Dispatcher"]:
        st.error("SECURITY VIOLATION: Unauthorized clearance level.")
        st.stop()

    st.markdown("<p style='color: #94a3b8; font-size: 0.9rem; margin-top: -10px;'>Assign a pending order to an available carrier.</p>", unsafe_allow_html=True)
    
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT order_id, origin_city, destination_city FROM orders WHERE order_id NOT IN (SELECT order_id FROM shipments)")
    pending_orders = cur.fetchall()
    cur.execute("SELECT carrier_id, company_name FROM carriers WHERE is_available = TRUE")
    available_carriers = cur.fetchall()
    conn.close()
    
    if not pending_orders:
        st.info("No pending orders available to dispatch.")
    elif not available_carriers:
        st.warning("No carriers available. Please wait for an active delivery to complete, or register a new carrier.")
    else:
        order_opts = {f"Order #{o['order_id']} ({o['origin_city']} ➔ {o['destination_city']})": o['order_id'] for o in pending_orders}
        carrier_opts = {c['company_name']: c['carrier_id'] for c in available_carriers}
        
        sel_order = st.selectbox("Select Pending Order", options=list(order_opts.keys()))
        sel_carrier = st.selectbox("Assign to Carrier", options=list(carrier_opts.keys()))
        
        if st.button("Initiate Dispatch", type="primary", use_container_width=True):
            o_id = order_opts[sel_order]
            c_id = carrier_opts[sel_carrier]
            
            conn = get_db()
            cur = conn.cursor()
            try:
                cur.execute("INSERT INTO shipments (order_id, carrier_id, status) VALUES (%s, %s, 'In Transit') RETURNING shipment_id", (o_id, c_id))
                new_ship_id = cur.fetchone()['shipment_id']
                cur.execute("INSERT INTO status_log (shipment_id, old_status, new_status, changed_by) VALUES (%s, 'Pending', 'In Transit', %s)", (new_ship_id, st.session_state.user['user_id']))
                cur.execute("UPDATE carriers SET is_available = FALSE WHERE carrier_id = %s", (c_id,))
                conn.commit()
                st.success("Fleet dispatched securely. Carrier locked.")
                st.rerun()
            except Exception as e:
                conn.rollback()
                st.error(f"Transaction failed. Error: {e}")
            finally:
                conn.close()

@st.dialog("✅ Update Delivery Status")
def update_status_dialog():
    # ─── ZERO TRUST SECURITY CHECK ───
    if st.session_state.user['role'] not in ["System Administrator", "Warehouse Manager"]:
        st.error("SECURITY VIOLATION: Unauthorized clearance level.")
        st.stop()

    st.markdown("<p style='color: #94a3b8; font-size: 0.9rem; margin-top: -10px;'>Record delivery progress or mark delays.</p>", unsafe_allow_html=True)
    
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT s.shipment_id, o.order_id, o.destination_city, c.company_name 
        FROM shipments s JOIN orders o ON s.order_id = o.order_id JOIN carriers c ON s.carrier_id = c.carrier_id
        WHERE s.status IN ('In Transit', 'Delayed')
    """)
    active_ships = cur.fetchall()
    conn.close()

    if not active_ships:
        st.info("No active shipments awaiting delivery updates.")
    else:
        ship_opts = {f"Ship #{s['shipment_id']} (Order #{s['order_id']} ➔ {s['destination_city']} via {s['company_name']})": s['shipment_id'] for s in active_ships}
        
        sel_ship = st.selectbox("Select Active Shipment", options=list(ship_opts.keys()))
        new_status = st.selectbox("New Status", ["Delivered", "Delayed", "Cancelled"])
        notes = st.text_input("Receiving Notes", placeholder="e.g., Signed by receiver at Dock 4.")
        
        if st.button("Confirm Status Update", type="primary", use_container_width=True):
            s_id = ship_opts[sel_ship]
            conn = get_db()
            cur = conn.cursor()
            try:
                cur.execute("SELECT status, carrier_id FROM shipments WHERE shipment_id = %s", (s_id,))
                ship_data = cur.fetchone()
                old_status, c_id = ship_data['status'], ship_data['carrier_id']

                if new_status == 'Delivered':
                    cur.execute("UPDATE shipments SET status = %s, actual_delivery_date = CURRENT_DATE, delivered_at = CURRENT_TIMESTAMP WHERE shipment_id = %s", (new_status, s_id))
                else:
                    cur.execute("UPDATE shipments SET status = %s WHERE shipment_id = %s", (new_status, s_id))

                cur.execute("INSERT INTO status_log (shipment_id, old_status, new_status, notes, changed_by) VALUES (%s, %s, %s, %s, %s)", (s_id, old_status, new_status, notes, st.session_state.user['user_id']))

                if new_status in ['Delivered', 'Cancelled']:
                    cur.execute("UPDATE carriers SET is_available = TRUE WHERE carrier_id = %s", (c_id,))

                conn.commit()
                st.success(f"Shipment #{s_id} marked as {new_status}. Fleet status updated.")
                st.rerun()
            except Exception as e:
                conn.rollback()
                st.error(f"Transaction failed. Error: {e}")
            finally:
                conn.close()

@st.dialog("🏢 Register Fleet Carrier")
def add_carrier_dialog():
    # ─── ZERO TRUST SECURITY CHECK ───
    if st.session_state.user['role'] != "System Administrator":
        st.error("SECURITY VIOLATION: Unauthorized clearance level.")
        st.stop()

    st.markdown("<p style='color: #94a3b8; font-size: 0.9rem; margin-top: -10px;'>Add a new vehicle to the logistics network.</p>", unsafe_allow_html=True)
    col_c1, col_c2 = st.columns(2)
    with col_c1: company = st.text_input("Carrier Company Name *", placeholder="e.g., TCS Logistics")
    with col_c2: phone = st.text_input("Dispatch Contact Phone *", placeholder="+92 300 1234567")
    v_type = st.selectbox("Vehicle Classification *", ["Select...", "Flatbed", "Box Truck", "Reefer (Refrigerated)", "LTL Van"])
    
    if st.button("Add to Fleet", type="primary", use_container_width=True):
        if not company or not phone or v_type == "Select...":
            st.error("Please fill all mandatory fields.")
        else:
            conn = get_db()
            cur = conn.cursor()
            try:
                cur.execute("INSERT INTO carriers (company_name, contact_phone, vehicle_type, is_available) VALUES (%s, %s, %s, TRUE)", (company, phone, v_type))
                conn.commit()
                st.success(f"{company} registered safely into the dispatch network.")
                st.rerun()
            except Exception as e:
                conn.rollback()
                st.error(f"Transaction failed. Error: {e}")
            finally:
                conn.close()


# ─── MAIN DASHBOARD RENDERING ──────────────────────────────────────────
def render_page():
    st.markdown("<h2 style='font-weight: 800; color: #f8fafc; margin-bottom: 1.5rem;'>🌐 Command Center</h2>", unsafe_allow_html=True)
    
    # 1. EXECUTIVE OVERVIEW
    metrics = fetch_executive_overview()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f'<div class="kpi-card" style="border-top: 4px solid #3b82f6;"><div class="kpi-title">Total Orders</div><div class="kpi-value">{metrics.get("total_orders", 0)}</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="kpi-card" style="border-top: 4px solid #10b981;"><div class="kpi-title">Active (In Transit)</div><div class="kpi-value">{metrics.get("active_shipments", 0)}</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="kpi-card" style="border-top: 4px solid #f59e0b;"><div class="kpi-title">Delayed</div><div class="kpi-value">{metrics.get("delayed_shipments", 0)}</div></div>', unsafe_allow_html=True)
    with col4:
        st.markdown(f'<div class="kpi-card" style="border-top: 4px solid #8b5cf6;"><div class="kpi-title">Available Fleet</div><div class="kpi-value">{metrics.get("available_carriers", 0)}</div></div>', unsafe_allow_html=True)
        
    st.markdown("<br><br>", unsafe_allow_html=True)

    # 2. ACTION CARDS (Contextual Workflows) - Now with 4 Columns
    st.markdown("<h3 style='font-weight: 700; color: #f8fafc; margin-bottom: 1rem;'>⚡ Operational Workflows</h3>", unsafe_allow_html=True)
    
    ac1, ac2, ac3, ac4 = st.columns(4)
    user_role = st.session_state.user['role']
    
    with ac1:
        st.markdown("""
        <div class="feature-card" style="padding: 1.5rem;">
            <h4 style="color: #f8fafc; margin-top: 0; font-size: 1.1rem;">📦 Draft Order</h4>
            <p style="color: #94a3b8; font-size: 0.8rem; margin-bottom: 1rem;">Create and validate a new freight contract into the pending queue.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Initiate Draft", key="btn_draft", use_container_width=True):
            draft_order_dialog() 
            
    with ac2:
        if user_role in ["System Administrator", "Dispatcher"]:
            st.markdown("""
            <div class="feature-card" style="padding: 1.5rem;">
                <h4 style="color: #f8fafc; margin-top: 0; font-size: 1.1rem;">🚚 Dispatch</h4>
                <p style="color: #94a3b8; font-size: 0.8rem; margin-bottom: 1rem;">Assign pending orders to available carriers and deploy trucks.</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Open Dispatch UI", key="btn_dispatch", use_container_width=True):
                dispatch_fleet_dialog()
        else:
            st.markdown("""
            <div class="feature-card" style="padding: 1.5rem; opacity: 0.5;">
                <h4 style="color: #f8fafc; margin-top: 0; font-size: 1.1rem;">🚚 Dispatch</h4>
                <p style="color: #94a3b8; font-size: 0.8rem; margin-bottom: 1rem;">Clearance Level Insufficient. Please contact Dispatch.</p>
            </div>
            """, unsafe_allow_html=True)
            st.button("Restricted", key="btn_dispatch_locked", disabled=True, use_container_width=True)

    with ac3:
        if user_role in ["System Administrator", "Warehouse Manager"]:
            st.markdown("""
            <div class="feature-card" style="padding: 1.5rem;">
                <h4 style="color: #f8fafc; margin-top: 0; font-size: 1.1rem;">✅ Update Log</h4>
                <p style="color: #94a3b8; font-size: 0.8rem; margin-bottom: 1rem;">Record delivery progress, mark delays, or close out shipments.</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Update Status", key="btn_update", use_container_width=True):
                update_status_dialog()
        else:
            st.markdown("""
            <div class="feature-card" style="padding: 1.5rem; opacity: 0.5;">
                <h4 style="color: #f8fafc; margin-top: 0; font-size: 1.1rem;">✅ Update Log</h4>
                <p style="color: #94a3b8; font-size: 0.8rem; margin-bottom: 1rem;">Clearance Level Insufficient. Please contact Warehouse.</p>
            </div>
            """, unsafe_allow_html=True)
            st.button("Restricted", key="btn_update_locked", disabled=True, use_container_width=True)
            
    with ac4:
        if user_role == "System Administrator":
            st.markdown("""
            <div class="feature-card" style="padding: 1.5rem;">
                <h4 style="color: #f8fafc; margin-top: 0; font-size: 1.1rem;">🏢 Add Carrier</h4>
                <p style="color: #94a3b8; font-size: 0.8rem; margin-bottom: 1rem;">Register new fleet assets to expand network capacity.</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Register Asset", key="btn_carrier", use_container_width=True):
                add_carrier_dialog()
        else:
            st.markdown("""
            <div class="feature-card" style="padding: 1.5rem; opacity: 0.5;">
                <h4 style="color: #f8fafc; margin-top: 0; font-size: 1.1rem;">🏢 Add Carrier</h4>
                <p style="color: #94a3b8; font-size: 0.8rem; margin-bottom: 1rem;">Clearance Level Insufficient. Admin access required.</p>
            </div>
            """, unsafe_allow_html=True)
            st.button("Restricted", key="btn_carrier_locked", disabled=True, use_container_width=True)