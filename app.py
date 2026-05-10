import streamlit as st
from database import get_db
from auth import verify_password

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
            .hero-title { text-align: center; font-size: 4rem; color: #00d4ff; font-weight: 800; padding-top: 2rem; margin-bottom: 0;}
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
            .feature-card p { color: #a7f3d0 !important; font-size: 0.9rem; } /* Sage green subtext */

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
                <p style="color: #64748b; font-size: 0.9rem;">Bank-grade transactional security ensuring database integrity during high-volume fleet assignments.</p>
            </div>
            """, unsafe_allow_html=True)
            
        with f2:
            st.markdown("""
            <div class="feature-card">
                <div class="feature-icon">📊</div>
                <h3>Real-Time Analytics</h3>
                <p style="color: #64748b; font-size: 0.9rem;">Live PostgreSQL aggregations delivering immediate business intelligence and KPI tracking.</p>
            </div>
            """, unsafe_allow_html=True)
            
        with f3:
            st.markdown("""
            <div class="feature-card">
                <div class="feature-icon">🔐</div>
                <h3>RBAC Architecture</h3>
                <p style="color: #64748b; font-size: 0.9rem;">Strict Role-Based Access Control partitioning Warehouse, Dispatch, and Administrative workflows.</p>
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
    # If logged in, restore the sidebar visibility using CSS
    st.markdown(
        """
        <style>
            [data-testid="stSidebar"] { display: block !important; }
            [data-testid="collapsedControl"] { display: block !important; }
        </style>
        """,
        unsafe_allow_html=True,
    )
    
    st.sidebar.title("LogiTrack PK")
    st.sidebar.write(f"**{st.session_state.user['full_name']}**")
    st.sidebar.caption(f"Clearance Level: {st.session_state.user['role']}")
    
    st.sidebar.divider()
    
    if st.sidebar.button("Log Out", use_container_width=True):
        st.session_state.user = None
        st.rerun()
        
    st.info("👈 Authentication successful. Please select a module from the sidebar navigation.")