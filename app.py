import streamlit as st
from auth import verify_password
from database import get_db
from streamlit_option_menu import option_menu
import pages.dashboard as dashboard
import pages.shipments as shipments

# ─── 1. PAGE CONFIGURATION ────────────────────────────────────────────
st.set_page_config(page_title="LogiTrack PK Enterprise", page_icon="📦", layout="wide", initial_sidebar_state="collapsed")

if 'user' not in st.session_state:
    st.session_state.user = None

# ─── 2. AUTHENTICATION GATEWAY ────────────────────────────────────────
def login_screen():
    st.markdown(
        """
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
            .stApp { background-color: #020617; color: #f8fafc; font-family: 'Plus Jakarta Sans', sans-serif; }
            [data-testid="stSidebar"], [data-testid="collapsedControl"], #MainMenu, footer, header { display: none !important; }
            
            /* Login Form Styling */
            .hero-title { text-align: center; font-size: 4.5rem; color: #10b981; font-weight: 800; padding-top: 2rem; margin-bottom: 0; letter-spacing: -1px; }
            .hero-subtitle { text-align: center; font-size: 1.1rem; color: #94a3b8; margin-bottom: 3rem; font-weight: 600; letter-spacing: 2px; }
            [data-testid="stForm"] { background: #0f172a !important; border: 1px solid #1e293b !important; border-radius: 16px !important; padding: 2rem !important; box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.5) !important; }
            .stTextInput input { border-radius: 8px !important; border: 1px solid #334155 !important; background-color: #020617 !important; color: white !important; }
            .stTextInput input:focus { border-color: #10b981 !important; box-shadow: 0 0 0 2px rgba(16,185,129,0.2) !important; }
            .stButton > button { border-radius: 8px !important; background: linear-gradient(to right, #059669, #10b981) !important; color: white !important; border: none !important; font-weight: 600 !important; transition: all 0.2s; }
            .stButton > button:hover { transform: translateY(-2px) !important; box-shadow: 0 10px 15px -3px rgba(16, 185, 129, 0.4) !important; }
        </style>
        """, unsafe_allow_html=True)
    
    st.markdown("<h1 class='hero-title'>LogiTrack PK</h1>", unsafe_allow_html=True)
    st.markdown("<p class='hero-subtitle'>ENTERPRISE FREIGHT & LOGISTICS MANAGEMENT</p>", unsafe_allow_html=True)
    
    col_space1, col_login, col_space2 = st.columns([1.5, 2, 1.5])
    with col_login:
        with st.form("login_form"):
            st.markdown("<h3 style='text-align: center; margin-bottom: 1.5rem; color: #f8fafc;'>Secure Access Portal</h3>", unsafe_allow_html=True)
            email = st.text_input("Email Address", placeholder="admin@freight.com")
            password = st.text_input("Password", type="password", placeholder="••••••••")
            st.markdown("<br>", unsafe_allow_html=True)
            submit = st.form_submit_button("Authenticate System", type="primary", use_container_width=True)
            
        if submit:
            conn = get_db()
            cur = conn.cursor()
            cur.execute("SELECT * FROM users WHERE email=%s AND is_active=TRUE", (email,))
            user = cur.fetchone()
            conn.close()
            if user and verify_password(password, user['password_hash']):
                st.session_state.user = {'user_id': user['user_id'], 'full_name': user['full_name'], 'role': user['role']}
                st.rerun()
            else:
                st.error("Authentication failed: Invalid credentials or deactivated account.")

# ─── 3. ENTERPRISE APPLICATION SHELL ──────────────────────────────────
if not st.session_state.user:
    login_screen()
else:
    st.markdown(
        """
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
            .stApp { background-color: #020617; color: #f8fafc; font-family: 'Plus Jakarta Sans', sans-serif; }
            [data-testid="stSidebar"], [data-testid="collapsedControl"], #MainMenu, footer, header { display: none !important; }
            
            /* Flush Left & Smooth Layout */
            .block-container { padding-left: 2rem !important; padding-right: 2rem !important; padding-top: 2rem !important; max-width: 100% !important; }
            
            /* Global Button Styling for Authenticated State */
            .stButton > button { border-radius: 8px !important; border: 1px solid #1e293b !important; color: #f8fafc !important; background-color: #0f172a !important; font-weight: 600 !important; transition: all 0.2s !important; }
            .stButton > button:hover { border-color: #10b981 !important; color: #10b981 !important; transform: translateY(-2px) !important; box-shadow: 0 4px 12px rgba(16, 185, 129, 0.15) !important; }
        </style>
        """, unsafe_allow_html=True)
    
    # HEADER
    header_col1, header_col2 = st.columns([8, 2])
    with header_col1:
        st.markdown("<h2 style='color: #10b981; margin-bottom: 0; font-weight: 800; letter-spacing: -1px;'>LogiTrack PK Enterprise</h2>", unsafe_allow_html=True)
    with header_col2:
        if st.button("🚪 Secure Logout", use_container_width=True):
            st.session_state.user = None
            st.rerun()
    st.markdown("<hr style='border-color: #1e293b; margin-top: 10px; margin-bottom: 2rem;'>", unsafe_allow_html=True)

    # ─── THE HARDCODED GRID LAYOUT ───
    nav_col, workspace_col = st.columns([2, 8], gap="large")
    user_role = st.session_state.user['role']

    # LEFT COLUMN: Premium Rounded Navigation Rail
    with nav_col:
        st.markdown(f"""
            <div style='background: #0f172a; padding: 20px; border-radius: 16px; border: 1px solid #1e293b; margin-bottom: 20px; box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);'>
                <p style='color: #94a3b8; font-size: 0.75rem; margin: 0; text-transform: uppercase; letter-spacing: 1.5px; font-weight: 700;'>Operator</p>
                <h4 style='color: #f8fafc; margin: 0; padding-top: 4px; font-size: 1.1rem;'>{st.session_state.user['full_name']}</h4>
                <span style='background: #022c22; color: #34d399; padding: 4px 10px; border-radius: 8px; font-size: 0.75rem; font-weight: 600; border: 1px solid #065f46; display: inline-block; margin-top: 10px;'>{user_role}</span>
            </div>
        """, unsafe_allow_html=True)

        nav_options = ["Dashboard", "Shipments"]
        nav_icons = ["grid", "truck"]
        if user_role in ["System Administrator", "Dispatcher"]:
            nav_options.append("Fleet")
            nav_icons.append("shield-check")
        nav_options.append("Reports")
        nav_icons.append("graph-up")
        if user_role == "System Administrator":
            nav_options.append("Audit Logs")
            nav_icons.append("clock-history")

        selected_module = option_menu(
            menu_title="MAIN NAVIGATION",
            options=nav_options,
            icons=nav_icons,
            default_index=0,
            styles={
                "container": {"padding": "0!important", "background-color": "transparent"},
                "icon": {"color": "#10b981", "font-size": "1.1rem"}, 
                "nav-link": {"font-size": "0.95rem", "text-align": "left", "margin": "8px 0", "color": "#94a3b8", "font-family": "'Plus Jakarta Sans', sans-serif", "font-weight": "600", "border-radius": "12px", "transition": "all 0.2s"},
                "nav-link-selected": {"background-color": "#022c22", "color": "#10b981", "font-weight": "700", "border": "1px solid #065f46"},
                "menu-title": {"color": "#64748b", "font-size": "0.8rem", "letter-spacing": "1.5px", "padding-left": "15px", "font-family": "'Plus Jakarta Sans', sans-serif", "font-weight": "800", "padding-bottom": "10px"}
            }
        )

    # RIGHT COLUMN: Workspace
    with workspace_col:
        if selected_module == "Dashboard":
            dashboard.render_page()
        elif selected_module == "Shipments":
            shipments.render_page()
        elif selected_module == "Fleet":
            st.title("🏢 Fleet Operations")
            st.info("Fleet Module decoupled and undergoing enterprise rendering...")
        elif selected_module == "Audit Logs":
            st.title("🔐 Immutable Ledger")
            st.info("Audit Logs decoupled and undergoing enterprise rendering...")