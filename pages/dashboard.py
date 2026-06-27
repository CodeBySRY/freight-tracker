import streamlit as st
import plotly.express as px
from database import get_db
from services.reporting_service import (
    fetch_executive_overview,
    fetch_activity_feed,
    fetch_shipment_status_distribution,
)

# ─── THEME ────────────────────────────────────────────────────────────────────
_PLOTLY_BASE = dict(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(color='#94a3b8', family='Plus Jakarta Sans', size=12),
    margin=dict(t=10, b=10, l=0, r=0)
)
STATUS_COLORS = {
    'Delivered': '#10b981', 'In Transit': '#3b82f6',
    'Delayed': '#f59e0b', 'Cancelled': '#ef4444', 'Pending': '#64748b'
}
_DOT_COLOR = {
    'In Transit': '#3b82f6', 'Delivered': '#10b981',
    'Delayed': '#f59e0b', 'Cancelled': '#ef4444', 'Pending': '#64748b'
}

# ─── DIALOGS (unchanged) ──────────────────────────────────────────────────────
@st.dialog("📦 Draft Comprehensive Freight Order")
def draft_order_dialog():
    st.markdown("<p style='color:#94a3b8;font-size:0.9rem;margin-top:-10px;'>Create a new contract. All fields marked * are required.</p>", unsafe_allow_html=True)
    customer = st.text_input("Customer Name *", placeholder="e.g., Giga Group")
    col1, col2 = st.columns(2)
    with col1: origin = st.text_input("Origin City *", placeholder="e.g., Karachi")
    with col2: dest   = st.text_input("Destination City *", placeholder="e.g., Islamabad")
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
            conn = get_db(); cur = conn.cursor()
            try:
                cur.execute("INSERT INTO orders (customer_name,origin_city,destination_city,cargo_description,cargo_type,cargo_weight_kg,priority,special_instructions,expected_delivery_date,created_by) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                    (customer, origin, dest, desc, c_type, weight, priority, instructions, exp_date, st.session_state.user['user_id']))
                conn.commit()
                st.success(f"Order validated and saved for {customer}!")
                st.rerun()
            except Exception as e:
                conn.rollback(); st.error(f"Database error: {e}")
            finally:
                conn.close()
        else:
            st.error("Customer, Origin, and Destination are mandatory fields.")

@st.dialog("🚚 Dispatch Fleet")
def dispatch_fleet_dialog():
    if st.session_state.user['role'] not in ["System Administrator", "Dispatcher"]:
        st.error("SECURITY VIOLATION: Unauthorized clearance level."); st.stop()
    st.markdown("<p style='color:#94a3b8;font-size:0.9rem;margin-top:-10px;'>Assign a pending order to an available carrier.</p>", unsafe_allow_html=True)
    conn = get_db(); cur = conn.cursor()
    cur.execute("SELECT order_id,origin_city,destination_city FROM orders WHERE order_id NOT IN (SELECT order_id FROM shipments)")
    pending_orders = cur.fetchall()
    cur.execute("SELECT carrier_id,company_name FROM carriers WHERE is_available=TRUE")
    available_carriers = cur.fetchall()
    conn.close()

    if not pending_orders:
        st.info("No pending orders available to dispatch.")
    elif not available_carriers:
        st.warning("No carriers available. Please wait for an active delivery to complete, or register a new carrier.")
    else:
        order_opts   = {f"Order #{o['order_id']} ({o['origin_city']} ➔ {o['destination_city']})": o['order_id'] for o in pending_orders}
        carrier_opts = {c['company_name']: c['carrier_id'] for c in available_carriers}
        sel_order   = st.selectbox("Select Pending Order", options=list(order_opts.keys()))
        sel_carrier = st.selectbox("Assign to Carrier",   options=list(carrier_opts.keys()))
        if st.button("Initiate Dispatch", type="primary", use_container_width=True):
            o_id = order_opts[sel_order]; c_id = carrier_opts[sel_carrier]
            conn = get_db(); cur = conn.cursor()
            try:
                cur.execute("INSERT INTO shipments (order_id,carrier_id,status) VALUES (%s,%s,'In Transit') RETURNING shipment_id", (o_id, c_id))
                new_ship_id = cur.fetchone()['shipment_id']
                cur.execute("INSERT INTO status_log (shipment_id,old_status,new_status,changed_by) VALUES (%s,'Pending','In Transit',%s)", (new_ship_id, st.session_state.user['user_id']))
                cur.execute("UPDATE carriers SET is_available=FALSE WHERE carrier_id=%s", (c_id,))
                conn.commit()
                st.success("Fleet dispatched securely. Carrier locked.")
                st.rerun()
            except Exception as e:
                conn.rollback(); st.error(f"Transaction failed. Error: {e}")
            finally:
                conn.close()

@st.dialog("✅ Update Delivery Status")
def update_status_dialog():
    if st.session_state.user['role'] not in ["System Administrator", "Warehouse Manager"]:
        st.error("SECURITY VIOLATION: Unauthorized clearance level."); st.stop()
    st.markdown("<p style='color:#94a3b8;font-size:0.9rem;margin-top:-10px;'>Record delivery progress or mark delays.</p>", unsafe_allow_html=True)
    conn = get_db(); cur = conn.cursor()
    cur.execute("SELECT s.shipment_id, o.order_id, o.destination_city, c.company_name FROM shipments s JOIN orders o ON s.order_id=o.order_id JOIN carriers c ON s.carrier_id=c.carrier_id WHERE s.status IN ('In Transit','Delayed')")
    active_ships = cur.fetchall()
    conn.close()

    if not active_ships:
        st.info("No active shipments awaiting delivery updates.")
    else:
        ship_opts  = {f"Ship #{s['shipment_id']} (Order #{s['order_id']} ➔ {s['destination_city']} via {s['company_name']})": s['shipment_id'] for s in active_ships}
        sel_ship   = st.selectbox("Select Active Shipment", options=list(ship_opts.keys()))
        new_status = st.selectbox("New Status", ["Delivered", "Delayed", "Cancelled"])
        notes      = st.text_input("Receiving Notes", placeholder="e.g., Signed by receiver at Dock 4.")
        if st.button("Confirm Status Update", type="primary", use_container_width=True):
            s_id = ship_opts[sel_ship]
            conn = get_db(); cur = conn.cursor()
            try:
                cur.execute("SELECT status,carrier_id FROM shipments WHERE shipment_id=%s", (s_id,))
                ship_data = cur.fetchone()
                old_status, c_id = ship_data['status'], ship_data['carrier_id']
                if new_status == 'Delivered':
                    cur.execute("UPDATE shipments SET status=%s,actual_delivery_date=CURRENT_DATE,delivered_at=CURRENT_TIMESTAMP WHERE shipment_id=%s", (new_status, s_id))
                else:
                    cur.execute("UPDATE shipments SET status=%s WHERE shipment_id=%s", (new_status, s_id))
                cur.execute("INSERT INTO status_log (shipment_id,old_status,new_status,notes,changed_by) VALUES (%s,%s,%s,%s,%s)", (s_id, old_status, new_status, notes, st.session_state.user['user_id']))
                if new_status in ['Delivered', 'Cancelled']:
                    cur.execute("UPDATE carriers SET is_available=TRUE WHERE carrier_id=%s", (c_id,))
                conn.commit()
                st.success(f"Shipment #{s_id} marked as {new_status}. Fleet status updated.")
                st.rerun()
            except Exception as e:
                conn.rollback(); st.error(f"Transaction failed. Error: {e}")
            finally:
                conn.close()

@st.dialog("🏢 Register Fleet Carrier")
def add_carrier_dialog():
    if st.session_state.user['role'] != "System Administrator":
        st.error("SECURITY VIOLATION: Unauthorized clearance level."); st.stop()
    st.markdown("<p style='color:#94a3b8;font-size:0.9rem;margin-top:-10px;'>Add a new vehicle to the logistics network.</p>", unsafe_allow_html=True)
    col_c1, col_c2 = st.columns(2)
    with col_c1: company = st.text_input("Carrier Company Name *", placeholder="e.g., TCS Logistics")
    with col_c2: phone   = st.text_input("Dispatch Contact Phone *", placeholder="+92 300 1234567")
    v_type = st.selectbox("Vehicle Classification *", ["Select...", "Flatbed", "Box Truck", "Reefer (Refrigerated)", "LTL Van", "All Vehicle Types"])
    if st.button("Add to Fleet", type="primary", use_container_width=True):
        if not company or not phone or v_type == "Select...":
            st.error("Please fill all mandatory fields.")
        else:
            conn = get_db(); cur = conn.cursor()
            try:
                cur.execute("INSERT INTO carriers (company_name,contact_phone,vehicle_type,is_available) VALUES (%s,%s,%s,TRUE)", (company, phone, v_type))
                conn.commit()
                st.success(f"{company} registered safely into the dispatch network.")
                st.rerun()
            except Exception as e:
                conn.rollback(); st.error(f"Transaction failed. Error: {e}")
            finally:
                conn.close()

# ─── SHARED CSS (injected once per render) ────────────────────────────────────
_DASHBOARD_CSS = """
<style>
.lt-kpi {
    background: linear-gradient(145deg, rgba(255,255,255,0.03), rgba(255,255,255,0.01));
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 16px;
    padding: 1.4rem 1.5rem;
    width: 100%;
    transition: transform 0.25s ease, box-shadow 0.25s ease, background 0.25s ease;
    cursor: default;
}
.lt-kpi:hover {
    transform: translateY(-5px);
    background: linear-gradient(145deg, rgba(255,255,255,0.05), rgba(255,255,255,0.02));
}
.lt-action {
    background: linear-gradient(145deg, rgba(255,255,255,0.03), rgba(255,255,255,0.01));
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 16px;
    padding: 1.6rem 1.5rem 1.2rem;
    width: 100%;
    min-height: 148px;
    transition: transform 0.25s ease, box-shadow 0.25s ease, border-color 0.25s ease, background 0.25s ease;
}
.lt-action:hover {
    transform: translateY(-5px);
    box-shadow: 0 20px 40px -12px rgba(16,185,129,0.25);
    border-color: rgba(16,185,129,0.3);
    background: linear-gradient(145deg, rgba(16,185,129,0.05), rgba(255,255,255,0.02));
}
.lt-action.locked {
    opacity: 0.4;
    filter: grayscale(0.5);
    pointer-events: none;
}
.lt-feed-item {
    display: flex;
    gap: 1rem;
    align-items: flex-start;
    padding: 1rem 1.1rem;
    margin-bottom: 0.6rem;
    background: rgba(255,255,255,0.02);
    border: 1px solid rgba(255,255,255,0.05);
    border-radius: 14px;
    transition: background 0.2s, border-color 0.2s;
}
.lt-feed-item:hover {
    background: rgba(255,255,255,0.045);
    border-color: rgba(255,255,255,0.1);
}
</style>
"""

# ─── HELPERS ──────────────────────────────────────────────────────────────────
def _kpi(icon, title, value, sub, accent):
    return f"""
    <div class="lt-kpi" style="border-top: 2px solid {accent};">
        <div style="width:42px;height:42px;border-radius:12px;
                    background:linear-gradient(135deg,{accent}33,{accent}11);
                    border:1px solid {accent}44;color:{accent};
                    display:flex;align-items:center;justify-content:center;
                    font-size:1.25rem;margin-bottom:1.1rem;">{icon}</div>
        <div style="color:#64748b;font-size:0.72rem;font-weight:700;
                    text-transform:uppercase;letter-spacing:1.2px;margin-bottom:0.3rem;">{title}</div>
        <div style="color:#f8fafc;font-size:2.1rem;font-weight:800;
                    line-height:1;letter-spacing:-1px;">{value}</div>
        <div style="color:#475569;font-size:0.75rem;margin-top:0.5rem;font-weight:600;
                    white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{sub}</div>
    </div>
    """

def _action_card(icon, title, desc, locked=False):
    cls = "lt-action locked" if locked else "lt-action"
    return f"""
    <div class="{cls}">
        <div style="width:44px;height:44px;border-radius:12px;
                    background:linear-gradient(135deg,rgba(16,185,129,0.2),rgba(16,185,129,0.05));
                    border:1px solid rgba(16,185,129,0.2);
                    display:flex;align-items:center;justify-content:center;
                    font-size:1.5rem;margin-bottom:0.85rem;">{icon}</div>
        <h4 style="color:#f8fafc;margin:0 0 0.4rem 0;font-size:1.05rem;
                   font-weight:800;letter-spacing:-0.3px;">{title}</h4>
        <p style="color:#64748b;font-size:0.82rem;margin:0;line-height:1.55;">{desc}</p>
    </div>
    """

def _render_activity_feed(events):
    if not events:
        st.markdown("""
        <div style='background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.05);
                    border-radius:16px;padding:3rem;text-align:center;'>
            <div style='font-size:2rem;margin-bottom:0.75rem;'>📭</div>
            <div style='color:#475569;font-size:0.85rem;font-weight:600;'>No activity recorded yet.</div>
        </div>
        """, unsafe_allow_html=True)
        return

    items_html = ""
    for e in events:
        dot   = _DOT_COLOR.get(e['new_status'], '#64748b')
        ts    = e['changed_at'].strftime("%b %d, %H:%M") if e['changed_at'] else ""
        route = f"{e['origin_city']} → {e['destination_city']}"
        badge = f"<span style='color:{dot};font-weight:700;background:{dot}22;padding:2px 9px;border-radius:20px;font-size:0.7rem;text-transform:uppercase;letter-spacing:0.5px;border:1px solid {dot}44;'>{e['new_status']}</span>"
        items_html += f"""
        <div class="lt-feed-item">
            <div style="flex-shrink:0;margin-top:4px;">
                <div style="width:10px;height:10px;border-radius:50%;background:{dot};
                            box-shadow:0 0 10px {dot}99,0 0 20px {dot}44;"></div>
            </div>
            <div style="flex:1;min-width:0;">
                <div style="margin-bottom:0.3rem;line-height:1.45;">
                    <strong style="color:#e2e8f0;font-size:0.9rem;">Ship #{e['shipment_id']}</strong>
                    <span style="color:#334155;margin:0 0.4rem;">·</span>
                    <span style="color:#94a3b8;font-size:0.85rem;">{e['customer_name']}</span>
                    <span style="color:#334155;margin:0 0.4rem;">·</span>
                    <span style="color:#64748b;font-size:0.82rem;">{route}</span>
                </div>
                <div style="display:flex;align-items:center;gap:0.6rem;">
                    {badge}
                    <span style="color:#334155;font-size:0.7rem;">·</span>
                    <span style="font-size:0.72rem;color:#475569;font-weight:600;">{ts}</span>
                    <span style="color:#334155;font-size:0.7rem;">·</span>
                    <span style="font-size:0.72rem;color:#475569;">by {e['operator']}</span>
                </div>
            </div>
        </div>"""

    st.markdown(f"<div style='width:100%;'>{items_html}</div>", unsafe_allow_html=True)

# ─── SECTION HEADER HELPER ────────────────────────────────────────────────────
def _section_header(title, subtitle=None):
    sub_html = f"<p style='color:#475569;font-size:0.82rem;margin:2px 0 0 0;font-weight:500;'>{subtitle}</p>" if subtitle else ""
    st.markdown(f"""
    <div style='margin-bottom:1.25rem;'>
        <h3 style='color:#f8fafc;font-size:1.1rem;font-weight:800;margin:0;letter-spacing:-0.3px;'>{title}</h3>
        {sub_html}
    </div>
    """, unsafe_allow_html=True)

def _divider():
    st.markdown("<hr style='border:none;border-top:1px solid rgba(255,255,255,0.05);margin:2.25rem 0;'>", unsafe_allow_html=True)

# ─── MAIN RENDER ──────────────────────────────────────────────────────────────
def render_page(module_name="Dashboard"):

    # Inject shared hover CSS (no inline JS needed)
    st.markdown(_DASHBOARD_CSS, unsafe_allow_html=True)

    # ── Page header
    st.markdown(f"""
    <div style='margin-bottom:2rem;'>
        <div style='color:#10b981;font-size:0.7rem;font-weight:800;letter-spacing:2.5px;
                    text-transform:uppercase;margin-bottom:6px;'>
            Workspace &nbsp;/&nbsp; {module_name}
        </div>
        <h2 style='color:#f8fafc;font-weight:800;font-size:2rem;margin:0;letter-spacing:-0.5px;'>
            Command Center
        </h2>
        <p style='color:#475569;font-size:0.9rem;margin:5px 0 0 0;font-weight:500;'>
            Live operational overview across your enterprise freight network.
        </p>
    </div>
    """, unsafe_allow_html=True)

    metrics   = fetch_executive_overview()
    events    = fetch_activity_feed(limit=5)          # ← capped at 5
    df_status = fetch_shipment_status_distribution()
    user_role = st.session_state.user['role']

    # ── 1. KPI STRIP ──────────────────────────────────────────────────────────
    fleet_pct = (round(metrics['available_carriers'] / metrics['total_carriers'] * 100)
                 if metrics['total_carriers'] > 0 else 0)

    k1, k2, k3, k4, k5, k6 = st.columns(6, gap="small")
    with k1: st.markdown(_kpi("📋", "Total Orders",  metrics['total_orders'],        "All time",             "#3b82f6"), unsafe_allow_html=True)
    with k2: st.markdown(_kpi("🚚", "In Transit",    metrics['active_shipments'],    "Currently active",     "#10b981"), unsafe_allow_html=True)
    with k3: st.markdown(_kpi("⚠️", "Delayed",       metrics['delayed_shipments'],   "Needs attention",      "#f59e0b"), unsafe_allow_html=True)
    with k4: st.markdown(_kpi("🏢", "Fleet Ready",   metrics['available_carriers'],  f"{fleet_pct}% avail.", "#8b5cf6"), unsafe_allow_html=True)
    with k5: st.markdown(_kpi("📅", "Due Today",     metrics['orders_today'],        "Expected deliveries",  "#06b6d4"), unsafe_allow_html=True)
    with k6: st.markdown(_kpi("✅", "Delivered",     metrics['delivered_today'],     "Completed runs",       "#34d399"), unsafe_allow_html=True)

    _divider()

    # ── 2. OPERATIONAL WORKFLOWS ──────────────────────────────────────────────
    _section_header("Operational Workflows", "Role-gated actions for freight operations management.")

    ac1, ac2, ac3, ac4 = st.columns(4, gap="medium")

    with ac1:
        st.markdown(_action_card("📦", "Draft Order", "Create and validate a new freight contract into the pending queue."), unsafe_allow_html=True)
        if st.button("Initiate Draft", key="btn_draft", use_container_width=True):
            draft_order_dialog()

    with ac2:
        can_dispatch = user_role in ["System Administrator", "Dispatcher"]
        st.markdown(_action_card("🚚", "Dispatch Fleet", "Assign pending orders to available carriers and deploy trucks.", locked=not can_dispatch), unsafe_allow_html=True)
        if can_dispatch:
            if st.button("Open Dispatch UI", key="btn_dispatch", use_container_width=True): dispatch_fleet_dialog()
        else:
            st.button("Restricted", key="btn_dispatch_locked", disabled=True, use_container_width=True)

    with ac3:
        can_update = user_role in ["System Administrator", "Warehouse Manager"]
        st.markdown(_action_card("✅", "Update Log", "Record delivery progress, mark delays, or close out shipments.", locked=not can_update), unsafe_allow_html=True)
        if can_update:
            if st.button("Update Status", key="btn_update", use_container_width=True): update_status_dialog()
        else:
            st.button("Restricted", key="btn_update_locked", disabled=True, use_container_width=True)

    with ac4:
        can_add = user_role == "System Administrator"
        st.markdown(_action_card("🏢", "Add Carrier", "Register new fleet assets to expand network capacity.", locked=not can_add), unsafe_allow_html=True)
        if can_add:
            if st.button("Register Asset", key="btn_carrier", use_container_width=True): add_carrier_dialog()
        else:
            st.button("Restricted", key="btn_carrier_locked", disabled=True, use_container_width=True)

    _divider()

    # ── 3. ANALYTICS + ACTIVITY FEED ─────────────────────────────────────────
    chart_col, feed_col = st.columns([1.2, 1], gap="large")

    with chart_col:
        _section_header("Shipment Status Distribution", "Breakdown of all shipments by current state.")
        if not df_status.empty:
            fig = px.pie(
                df_status, values='n', names='status', hole=0.65,
                color='status', color_discrete_map=STATUS_COLORS
            )
            fig.update_layout(
                **_PLOTLY_BASE,
                showlegend=True,
                legend=dict(
                    orientation="h", x=0.5, xanchor="center", y=-0.1,
                    font=dict(color='#94a3b8', size=11)
                ),
                height=340
            )
            fig.update_traces(
                textposition='outside',
                textinfo='percent+label',
                textfont=dict(color='#cbd5e1', size=11),
                marker=dict(line=dict(color='#040914', width=3)),
                hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Share: %{percent}<extra></extra>'
            )
            total_shipments = int(df_status['n'].sum())
            fig.add_annotation(
                text=f"<b>{total_shipments}</b><br><span style='font-size:10px'>TOTAL</span>",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=22, color='#f8fafc', family='Plus Jakarta Sans')
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.markdown("""
            <div style='background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.05);
                        border-radius:16px;padding:3rem;text-align:center;color:#64748b;font-weight:600;'>
                No shipment data available yet.
            </div>
            """, unsafe_allow_html=True)

    with feed_col:
        _section_header("Live Activity Feed", "Latest 5 status events across the network.")
        _render_activity_feed(events)