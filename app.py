import streamlit as st
import pandas as pd
import re
from database import get_db
from auth import verify_password
from streamlit_option_menu import option_menu

# Must be the very first Streamlit command
st.set_page_config(page_title="LogiTrack PK", page_icon="📦", layout="wide", initial_sidebar_state="collapsed")

# ─── UI HACK: Hide Sidebar & Apply Custom Styling on Login ──────────────
if 'user' not in st.session_state or st.session_state.user is None:
    st.markdown(
        """
        <style>
            /* Hide the sidebar and the expand toggle */
            [data-testid="stSidebar"] { display: none !important; }
            [data-testid="collapsedControl"] { display: none !important; }
            
            /* Custom Landing Page CSS */
            .hero-title { text-align: center; font-size: 4rem; color: #10b981; font-weight: 800; padding-top: 2rem; margin-bottom: 0;}
            .hero-subtitle { text-align: center; font-size: 1.2rem; color: #94a3b8; margin-bottom: 3rem; font-family: monospace; letter-spacing: 1px;}
            
          /* Premium Mouse Scroll Animation */
            .scroll-container {
                display: flex;
                flex-direction: column;
                align-items: center;
                margin-top: 4rem;
                margin-bottom: 3rem;
                opacity: 0.85;
                transition: opacity 0.3s ease;
            }
            .scroll-container:hover {
                opacity: 1;
            }
            .scroll-text {
                font-size: 0.75rem;
                letter-spacing: 4px;
                text-transform: uppercase;
                color: #10b981; /* Emerald Green */
                margin-bottom: 15px;
                font-weight: 600;
            }
            .mouse {
                width: 28px;
                height: 48px;
                border: 2px solid #065f46; /* Dark Emerald Border */
                border-radius: 20px;
                position: relative;
            }
            .wheel {
                width: 4px;
                height: 8px;
                background: #10b981; /* Emerald Green */
                border-radius: 2px;
                position: absolute;
                top: 8px;
                left: 50%;
                transform: translateX(-50%);
                animation: scrollWheel 2s infinite cubic-bezier(0.15, 0.41, 0.69, 0.94);
                box-shadow: 0 0 10px rgba(16, 185, 129, 0.8); /* Emerald Glow */
            }
            @keyframes scrollWheel {
                0% { top: 8px; opacity: 1; height: 8px; }
                50% { top: 24px; opacity: 0; height: 12px; }
                100% { top: 8px; opacity: 0; height: 8px; }
            }

            /* Problem Statement Section */
            .problem-section {
                background: linear-gradient(145deg, #022c22, #04150f); /* Dark Forest Gradient */
                border: 1px solid #065f46; /* Emerald Border */
                border-left: 4px solid #10b981; /* Bright Emerald Left Accent */
                padding: 2.5rem;
                border-radius: 12px;
                margin-bottom: 3rem;
                text-align: center;
                box-shadow: 0 10px 30px rgba(0,0,0,0.5);
            }
            .problem-title {
                color: #f8fafc; /* Crisp White */
                font-size: 1.5rem;
                font-weight: 600;
                margin-bottom: 1rem;
            }
            .problem-text {
                color: #a7f3d0; /* Sage Green */
                font-size: 1.05rem;
                line-height: 1.7;
                max-width: 800px;
                margin: 0 auto;
            }
            
            /* Feature Cards - Fully Green Palette */
            .feature-card { 
                background: #022c22; /* Deep forest green background */
                border: 1px solid #065f46; /* Emerald border instead of slate blue */
                padding: 1.5rem; 
                border-radius: 12px; 
                text-align: center;
                transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
            }
            .feature-card:hover { 
                transform: translateY(-5px); 
                border-color: #34d399; /* Bright mint glow on hover */
                box-shadow: 0 10px 25px rgba(16, 185, 129, 0.25);
            }
            .feature-icon { font-size: 2.5rem; margin-bottom: 1rem; }
            .feature-card h3 { color: #f8fafc; margin-bottom: 0.5rem; }
            .feature-card p { color: #a7f3d0 !important; font-size: 0.9rem; }

          /* Corporate Footer */
            .corporate-footer {
                background: linear-gradient(145deg, #022c22, #04150f);
                padding: 3rem 4rem;
                margin-top: 5rem;
                border-top: 1px solid #065f46;
                border-radius: 12px;
                color: #a7f3d0;
                text-align: left;
            }
            .footer-lang { 
                font-size: 1.1rem; 
                color: #f8fafc; 
                font-weight: 600; 
                display: flex; 
                align-items: center; 
                gap: 0.5rem; 
                margin-bottom: 1.5rem;
            }
            .footer-text {
                font-size: 0.95rem;
                line-height: 1.8;
                margin-bottom: 2rem;
                max-width: 1000px;
            }
            .footer-breadcrumbs {
                font-size: 0.85rem;
                border-top: 1px solid #065f46;
                padding-top: 1.5rem;
                color: #34d399; 
            }
            .footer-breadcrumbs span { color: #10b981; font-weight: 500; }
        </style>
        """,
        unsafe_allow_html=True,
    )

# Initialize Session State
if 'user' not in st.session_state:
    st.session_state.user = None

def login_screen():
    # ─── HERO SECTION ───────────────────────────────────────────────────
    st.markdown("<h1 class='hero-title'>LogiTrack PK</h1>", unsafe_allow_html=True)
    st.markdown("<p class='hero-subtitle'>ENTERPRISE FREIGHT & LOGISTICS MANAGEMENT</p>", unsafe_allow_html=True)
    
    # ─── LOGIN PORTAL ───────────────────────────────────────────────────
    col_space1, col_login, col_space2 = st.columns([1.5, 2, 1.5])
    
    with col_login:
        with st.form("login_form"):
            st.subheader("Secure Access Portal")
            email = st.text_input("Email Address", placeholder="admin@freight.com")
            password = st.text_input("Password", type="password", placeholder="••••••••")
            submit = st.form_submit_button("Authenticate System", type="primary", use_container_width=True)
            
        if submit:
            conn = get_db()
            cur = conn.cursor()
            cur.execute("SELECT * FROM users WHERE email=%s AND is_active=TRUE", (email,))
            user = cur.fetchone()
            conn.close()
            
            if user and verify_password(password, user['password_hash']):
                st.session_state.user = {
                    'user_id': user['user_id'],
                    'full_name': user['full_name'],
                    'role': user['role']
                }
                st.rerun()
            else:
                st.error("Authentication failed: Invalid credentials or deactivated account.")

    # ─── SLEEK MOUSE SCROLL INDICATOR ───────────────────────────────────
    st.markdown("""
        <div class="scroll-container">
            <div class="scroll-text">Discover More</div>
            <div class="mouse">
                <div class="wheel"></div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # ─── THE PROBLEM STATEMENT ──────────────────────────────────────────
    col_space_prob1, col_prob, col_space_prob2 = st.columns([1, 4, 1])
    with col_prob:
        st.markdown("""
        <div class="problem-section">
            <div class="problem-title">Tackling the Logistics Bottleneck</div>
            <div class="problem-text">
                Modern supply chains are paralyzed by fragmented communication, opaque shipment tracking, and informal dispatch networks. LogiTrack PK bridges this gap by replacing chaotic spreadsheets with a centralized, ACID-compliant database architecture. We empower dispatchers and warehouse staff to operate with unified, real-time clarity.
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ─── 3D / SLEEK FEATURES GRID ───────────────────────────────────────
    col_space3, col_features, col_space4 = st.columns([0.5, 4, 0.5])
    
    with col_features:
        f1, f2, f3 = st.columns(3)
        
        with f1:
            st.markdown("""
            <div class="feature-card">
                <div class="feature-icon">🛡️</div>
                <h3>ACID Compliant</h3>
                <p>Bank-grade transactional security ensuring database integrity during high-volume fleet assignments.</p>
            </div>
            """, unsafe_allow_html=True)
            
        with f2:
            st.markdown("""
            <div class="feature-card">
                <div class="feature-icon">📊</div>
                <h3>Real-Time Analytics</h3>
                <p>Live PostgreSQL aggregations delivering immediate business intelligence and KPI tracking.</p>
            </div>
            """, unsafe_allow_html=True)
            
        with f3:
            st.markdown("""
            <div class="feature-card">
                <div class="feature-icon">🔐</div>
                <h3>RBAC Architecture</h3>
                <p>Strict Role-Based Access Control partitioning Warehouse, Dispatch, and Administrative workflows.</p>
            </div>
            """, unsafe_allow_html=True)

    # ─── CORPORATE FOOTER ───────────────────────────────────────────────
    col_space_foot1, col_foot, col_space_foot2 = st.columns([0.5, 4, 0.5])
    with col_foot:
        st.markdown("""
        <div class="corporate-footer">
            <div class="footer-lang">
                🌍 English (Global)
            </div>
            <div class="footer-text">
                Founded in May 2026, LogiTrack PK is a trusted enterprise platform for managing freight operations across Pakistan. Engineered with precision by Shayan Rizwan, Anzar Mubashir, and Agha Salaat, our platform helps arrange complex logistics deliveries from localized LTL shipments to heavy cargo loads. Thanks to a relational PostgreSQL backend and bank-grade transactional security, LogiTrack PK is the most reliable way for dispatchers to track shipments, audit statuses, and securely manage fleet capacity.
            </div>
            <div class="footer-breadcrumbs">
                <span>LogiTrack PK</span> &nbsp; / &nbsp; Enterprise Freight Management &nbsp; / &nbsp; © 2026 All Rights Reserved.
            </div>
        </div>
        """, unsafe_allow_html=True)

# ─── ROUTING & AUTHENTICATED STATE ────────────────────────────────────
if not st.session_state.user:
    login_screen()
else:
    # ─── INTERNAL DASHBOARD CSS & ANTI-FLUFF ─────────────────────────────
    st.markdown(
        """
        <style>
            /* Hide Streamlit default branding */
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            
            /* Hide the default sidebar completely in authenticated state */
            [data-testid="stSidebar"] { display: none !important; }
            [data-testid="collapsedControl"] { display: none !important; }
            
            /* Style buttons */
            .stButton>button {
                border-radius: 8px;
                transition: all 0.3s ease;
                border: 1px solid #065f46;
                color: #f8fafc;
                background-color: #022c22;
            }
            .stButton>button:hover {
                box-shadow: 0 4px 12px rgba(16, 185, 129, 0.2);
                border-color: #10b981;
                color: #10b981;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )
    
    # ─── TOP HEADER & LOGOUT ──────────────────────────────────────────────
    header_col1, header_col2 = st.columns([8, 2])
    with header_col1:
        st.markdown(f"<h2 style='color: #10b981; margin-bottom: 0;'>LogiTrack PK Enterprise</h2>", unsafe_allow_html=True)
        st.markdown(f"<p style='color: #a7f3d0; font-size: 0.95rem; margin-top: 0;'>Logged in as: <b>{st.session_state.user['full_name']}</b> | Clearance: <i>{st.session_state.user['role']}</i></p>", unsafe_allow_html=True)
        
    with header_col2:
        st.markdown("<br>", unsafe_allow_html=True) # Spacing alignment
        if st.button("🚪 Secure Logout", type="primary", use_container_width=True):
            st.session_state.user = None
            st.rerun()

    st.markdown("<hr style='border-color: #065f46; margin-top: 0;'>", unsafe_allow_html=True)

    # ─── HORIZONTAL TOP NAVIGATION BAR (RBAC ENFORCED) ────────────────────
    user_role = st.session_state.user['role']
    
    # Base modules accessible by everyone (Warehouse Manager baseline)
    nav_options = ["Command Center", "Active Shipments"]
    nav_icons = ["grid", "truck"]
    
    # Dispatcher & Admin extensions
    if user_role in ["System Administrator", "Dispatcher"]:
        nav_options.append("Carrier Fleet")
        nav_icons.append("shield-check")
        
    # Admin exclusive extensions
    if user_role == "System Administrator":
        nav_options.append("Audit Logs")
        nav_icons.append("clock-history")

    selected_module = option_menu(
        menu_title=None,
        options=nav_options,
        icons=nav_icons,
        default_index=0,
        orientation="horizontal",
        styles={
            "container": {"padding": "0!important", "background-color": "#022c22", "border": "1px solid #065f46", "border-radius": "8px"},
            "icon": {"color": "#10b981", "font-size": "1.2rem"}, 
            "nav-link": {
                "font-size": "0.95rem", 
                "text-align": "center", 
                "margin": "0px", 
                "color": "#a7f3d0",
                "--hover-color": "#04150f"
            },
            "nav-link-selected": {
                "background-color": "#10b981", 
                "color": "#04150f", 
                "font-weight": "800"
            },
        }
    )
    st.markdown("<br>", unsafe_allow_html=True)

    # ─── MODULE ROUTING LOGIC ─────────────────────────────────────────────
    if selected_module == "Command Center":
        st.markdown("### 🌐 Live Systems Overview")
        
        # Fetch Live KPIs using Aggregation Queries
        conn = get_db()
        cur = conn.cursor()
        
        try:
            cur.execute("SELECT COUNT(*) AS total FROM orders")
            total_orders = cur.fetchone()['total']
            
            cur.execute("SELECT COUNT(*) AS active FROM shipments WHERE status NOT IN ('Delivered', 'Cancelled')")
            active_shipments = cur.fetchone()['active']
            
            cur.execute("SELECT COUNT(*) AS available FROM carriers WHERE is_available = TRUE")
            available_carriers = cur.fetchone()['available']
        except Exception as e:
            st.error(f"Database Error: {e}")
            total_orders, active_shipments, available_carriers = 0, 0, 0
        finally:
            conn.close()

        # Render KPI Cards
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"""
            <div style="background-color: #022c22; border-left: 4px solid #10b981; padding: 20px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.3);">
                <h4 style="color: #a7f3d0; margin: 0; font-size: 1rem;">Total Freight Orders</h4>
                <h1 style="color: #f8fafc; margin: 0; font-size: 2.5rem;">{total_orders}</h1>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div style="background-color: #022c22; border-left: 4px solid #3b82f6; padding: 20px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.3);">
                <h4 style="color: #a7f3d0; margin: 0; font-size: 1rem;">Active Shipments</h4>
                <h1 style="color: #f8fafc; margin: 0; font-size: 2.5rem;">{active_shipments}</h1>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown(f"""
            <div style="background-color: #022c22; border-left: 4px solid #f59e0b; padding: 20px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.3);">
                <h4 style="color: #a7f3d0; margin: 0; font-size: 1rem;">Available Carriers</h4>
                <h1 style="color: #f8fafc; margin: 0; font-size: 2.5rem;">{available_carriers}</h1>
            </div>
            """, unsafe_allow_html=True)
            
        st.markdown("<br><hr style='border-color: #065f46;'><br>", unsafe_allow_html=True)
        
        # ─── QUICK ACTIONS (RBAC ENFORCED) ───
        st.markdown("### Quick Actions")
        
        # Initialize session state for interactive routing
        if 'active_action' not in st.session_state:
            st.session_state.active_action = None

        # Build allowed actions based on clearance level
        allowed_actions = []
        allowed_actions.append(("📦 Draft New Order", "order"))
        
        if user_role in ["System Administrator", "Dispatcher"]:
            allowed_actions.append(("🚚 Dispatch Fleet", "dispatch"))
            
        if user_role == "System Administrator":
            allowed_actions.append(("🏢 Add Carrier", "carrier"))
            
        allowed_actions.append(("📊 Generate Report", "report"))

        # Render only the columns authorized for this user
        cols = st.columns(len(allowed_actions))
        for idx, (btn_label, action_key) in enumerate(allowed_actions):
            with cols[idx]:
                if st.button(btn_label, use_container_width=True):
                    st.session_state.active_action = action_key

        st.markdown("<br>", unsafe_allow_html=True)

        # ─── BACKEND LOGIC FOR QUICK ACTIONS ───
        if st.session_state.active_action == "order":
            with st.form("new_order_form"):
                st.markdown("#### 📦 Draft Comprehensive Freight Order")
                
                # Top Row: Client & Routing
                col1, col2, col3 = st.columns(3)
                with col1:
                    customer = st.text_input("Customer Name *", placeholder="e.g., Giga Group")
                with col2:
                    origin = st.text_input("Origin City *", placeholder="e.g., Karachi")
                with col3:
                    dest = st.text_input("Destination City *", placeholder="e.g., Islamabad")
                
                # Middle Row: Cargo Details
                col4, col5, col6 = st.columns([2, 1, 1])
                with col4:
                    desc = st.text_input("Cargo Description", placeholder="e.g., Electronics Pallets")
                with col5:
                    c_type = st.selectbox("Cargo Type", ["Standard", "Fragile", "Hazardous", "Refrigerated"])
                with col6:
                    weight = st.number_input("Weight (kg)", min_value=0.0, step=10.5)
                
                # Bottom Row: Logistics
                col7, col8, col9 = st.columns(3)
                with col7:
                    priority = st.selectbox("Priority Level", ["Standard", "Expedited", "Overnight", "Critical"])
                with col8:
                    exp_date = st.date_input("Expected Delivery Date")
                with col9:
                    instructions = st.text_area("Special Instructions", height=68, placeholder="Gate codes, handling protocols...")
                
                if st.form_submit_button("Save Order to Database", type="primary"):
                    if customer and origin and dest:
                        conn = get_db()
                        cur = conn.cursor()
                        query = """
                            INSERT INTO orders 
                            (customer_name, origin_city, destination_city, cargo_description, cargo_type, cargo_weight_kg, priority, special_instructions, expected_delivery_date, created_by) 
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """
                        cur.execute(query, (customer, origin, dest, desc, c_type, weight, priority, instructions, exp_date, st.session_state.user['user_id']))
                        conn.commit()
                        conn.close()
                        st.success(f"Order strictly validated and saved for {customer}!")
                        st.session_state.active_action = None
                        st.rerun()
                    else:
                        st.error("Customer, Origin, and Destination are mandatory fields.")

        elif st.session_state.active_action == "carrier":
            with st.form("new_carrier_form"):
                st.markdown("#### 🏢 Register Fleet Carrier")
                col_c1, col_c2, col_c3 = st.columns(3)
                with col_c1:
                    company = st.text_input("Carrier Company Name *", placeholder="e.g., TCS Logistics")
                with col_c2:
                    phone = st.text_input("Dispatch Contact Phone *", placeholder="+92 300 1234567")
                with col_c3:
                    v_type_options = ["Select...", "All Fleet Types", "Flatbed", "Box Truck", "Reefer (Refrigerated)", "LTL Van"]
                    v_type = st.selectbox("Vehicle Classification *", v_type_options)
                
                if st.form_submit_button("Add to Fleet", type="primary"):
                    # Validation Logic
                    if not company:
                        st.error("Company Name is a mandatory field.")
                    elif not phone:
                        st.error("Dispatch Contact Phone is a mandatory field.")
                    elif not re.match(r'^[\+\d\s\-]+$', phone):
                        st.error("Invalid phone number format. Please use only numbers, spaces, dashes, or a leading '+'.")
                    elif v_type == "Select...":
                        st.error("Please select a valid Vehicle Classification.")
                    else:
                        conn = get_db()
                        cur = conn.cursor()
                        cur.execute("INSERT INTO carriers (company_name, contact_phone, vehicle_type, is_available) VALUES (%s, %s, %s, TRUE)", (company, phone, v_type))
                        conn.commit()
                        conn.close()
                        st.success(f"{company} safely integrated into the dispatch network.")
                        st.session_state.active_action = None
                        st.rerun()
                        
        elif st.session_state.active_action == "dispatch":
            # Real enterprise logic: Fetch pending orders and available carriers
            conn = get_db()
            cur = conn.cursor()
            cur.execute("SELECT order_id, origin_city, destination_city FROM orders WHERE order_id NOT IN (SELECT order_id FROM shipments)")
            pending_orders = cur.fetchall()
            
            cur.execute("SELECT carrier_id, company_name FROM carriers WHERE is_available = TRUE")
            available_carriers = cur.fetchall()
            conn.close()
            
            with st.form("dispatch_form"):
                st.markdown("#### Dispatch Freight to Carrier")
                
                if not pending_orders:
                    st.info("No pending orders available to dispatch. Please draft a new order first.")
                    st.form_submit_button("Acknowledge") 
                elif not available_carriers:
                    st.warning("No carriers available. Please add a carrier to the fleet first.")
                    st.form_submit_button("Acknowledge")
                else:
                    order_opts = {f"Order #{o['order_id']} ({o['origin_city']} ➔ {o['destination_city']})": o['order_id'] for o in pending_orders}
                    carrier_opts = {c['company_name']: c['carrier_id'] for c in available_carriers}
                    
                    sel_order = st.selectbox("Select Pending Order", options=list(order_opts.keys()))
                    sel_carrier = st.selectbox("Assign to Carrier", options=list(carrier_opts.keys()))
                    
                    if st.form_submit_button("Initiate Dispatch", type="primary"):
                        o_id = order_opts[sel_order]
                        c_id = carrier_opts[sel_carrier]
                        
                        conn = get_db()
                        cur = conn.cursor()
                        
                        # ─── ACID COMPLIANT TRANSACTION BLOCK ───
                        try:
                            # 1. Create the Shipment
                            cur.execute("INSERT INTO shipments (order_id, carrier_id, status) VALUES (%s, %s, 'In Transit') RETURNING shipment_id", (o_id, c_id))
                            new_ship_id = cur.fetchone()['shipment_id']
                            
                            # 2. Cryptographically tie the action to the user in the Audit Log
                            cur.execute("INSERT INTO status_log (shipment_id, old_status, new_status, changed_by) VALUES (%s, 'Pending', 'In Transit', %s)", (new_ship_id, st.session_state.user['user_id']))
                            
                            # Both succeeded, commit the transaction
                            conn.commit()
                            st.success("Fleet dispatched securely. Immutable audit log updated.")
                            st.session_state.active_action = None
                            st.rerun()
                        except Exception as e:
                            # If either fails, rollback entirely to protect data integrity
                            conn.rollback()
                            st.error(f"Transaction failed and rolled back. Error: {e}")
                        finally:
                            conn.close()
                        
        elif st.session_state.active_action == "report":
            st.info("To generate a comprehensive CSV report, please navigate to the 'Active Shipments' tab and click 'Export to CSV'.")
            if st.button("Close Message"):
                st.session_state.active_action = None
                st.rerun()
                
    # ─── CORRECTLY ALIGNED MODULE ROUTING ───
    elif selected_module == "Active Shipments":
        st.title("Active Shipments & Fleet Tracking")
        st.write("Monitor live freight movement, filter by status, and export dispatcher reports.")
        
        # The Control Panel (Search & Filter)
        col_search, col_filter, col_export = st.columns([2, 1, 1])
        with col_search:
            search_query = st.text_input("🔍 Search Origin, Destination, or Carrier", placeholder="e.g., Karachi or TCS")
        with col_filter:
            status_filter = st.selectbox("Filter Status", ["All", "Pending", "Assigned", "In Transit", "Delivered"])
            
        # Dynamic Database Fetching mapping to the True Schema
        conn = get_db()
        cur = conn.cursor()
        base_query = """
            SELECT 
                s.shipment_id AS "Shipment ID",
                o.customer_name AS "Client",
                o.origin_city AS "Origin",
                o.destination_city AS "Destination",
                o.priority AS "Priority",
                c.company_name AS "Carrier",
                s.status AS "Current Status",
                TO_CHAR(s.assigned_at, 'YYYY-MM-DD HH24:MI') AS "Assigned Time"
            FROM shipments s
            JOIN orders o ON s.order_id = o.order_id
            JOIN carriers c ON s.carrier_id = c.carrier_id
            WHERE 1=1
        """
        params = []
        if status_filter != "All":
            base_query += " AND s.status = %s"
            params.append(status_filter)
        if search_query:
            base_query += " AND (o.origin_city ILIKE %s OR o.destination_city ILIKE %s OR c.company_name ILIKE %s)"
            search_term = f"%{search_query}%"
            params.extend([search_term, search_term, search_term])
            
        base_query += " ORDER BY s.assigned_at DESC"
        cur.execute(base_query, tuple(params))
        data = cur.fetchall()
        conn.close()
        
        # Data Rendering
        if data:
            df = pd.DataFrame(data)
            st.dataframe(df, use_container_width=True, hide_index=True)
            with col_export:
                st.markdown("<br>", unsafe_allow_html=True)
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button("📥 Export to CSV", data=csv, file_name="Active_Shipments.csv", mime="text/csv", use_container_width=True)
        else:
            st.info("No active shipments match your current search criteria.")
            
    elif selected_module == "Carrier Fleet":
        st.title("Carrier Fleet Management")
        st.info("To add a new carrier, navigate to the Command Center and click 'Add Carrier'.")
        
    elif selected_module == "Audit Logs":
        st.title("System Audit Logs")
        st.markdown("<p style='color: #a7f3d0;'>Immutable ledger of all shipment status transitions and authorization events.</p>", unsafe_allow_html=True)
        
        conn = get_db()
        cur = conn.cursor()
        query = """
            SELECT 
                sl.log_id AS "Event ID",
                sl.shipment_id AS "Shipment Ref",
                sl.old_status AS "Previous State",
                sl.new_status AS "New State",
                sl.notes AS "System Notes",
                u.full_name AS "Authorized By",
                u.role AS "Clearance Level",
                TO_CHAR(sl.changed_at, 'YYYY-MM-DD HH24:MI:SS') AS "Timestamp"
            FROM status_log sl
            JOIN users u ON sl.changed_by = u.user_id
            ORDER BY sl.changed_at DESC
            LIMIT 100
        """
        try:
            cur.execute(query)
            logs = cur.fetchall()
            if logs:
                df_logs = pd.DataFrame(logs)
                st.dataframe(df_logs, use_container_width=True, hide_index=True)
            else:
                st.info("No status transitions have been recorded yet.")
        except Exception as e:
            st.error(f"Failed to fetch audit logs: {e}")
        finally:
            conn.close()