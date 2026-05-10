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
            
            /* Scroll Indicator Animation */
            .scroll-indicator {
                text-align: center;
                margin-top: 3rem;
                margin-bottom: 3rem;
                color: #475569;
                animation: bounce 2s infinite;
            }
            @keyframes bounce {
                0%, 20%, 50%, 80%, 100% { transform: translateY(0); }
                40% { transform: translateY(-15px); }
                60% { transform: translateY(-7px); }
            }

            /* Problem Statement Section */
            .problem-section {
                background: linear-gradient(145deg, #0a0e1a, #111827);
                border: 1px solid #1e2d45;
                border-left: 4px solid #00d4ff;
                padding: 2.5rem;
                border-radius: 12px;
                margin-bottom: 3rem;
                text-align: center;
                box-shadow: 0 10px 30px rgba(0,0,0,0.5);
            }
            .problem-title {
                color: #e2e8f0;
                font-size: 1.5rem;
                font-weight: 600;
                margin-bottom: 1rem;
            }
            .problem-text {
                color: #94a3b8;
                font-size: 1.05rem;
                line-height: 1.7;
                max-width: 800px;
                margin: 0 auto;
            }

            /* Feature Cards */
            .feature-card { 
                background: #111827; 
                border: 1px solid #1e2d45; 
                padding: 1.5rem; 
                border-radius: 12px; 
                text-align: center;
                transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
            }
            .feature-card:hover { 
                transform: translateY(-5px); 
                border-color: #00d4ff; 
                box-shadow: 0 10px 20px rgba(0, 212, 255, 0.1);
            }
            .feature-icon { font-size: 2.5rem; margin-bottom: 1rem; }
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

    # ─── SCROLL INDICATOR ───────────────────────────────────────────────
    st.markdown("""
        <div class="scroll-indicator">
            <div style="font-size: 0.9rem; margin-bottom: 8px; letter-spacing: 1px; text-transform: uppercase;">Discover More</div>
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <polyline points="6 9 12 15 18 9"></polyline>
            </svg>
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