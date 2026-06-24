import streamlit as st
from auth import verify_password
from database import get_db
from streamlit_option_menu import option_menu
from styles.theme import apply_enterprise_theme
import pages.dashboard as dashboard
import pages.shipments as shipments

# ─── 1. PAGE CONFIGURATION & THEME ────────────────────────────────────
st.set_page_config(page_title="LogiTrack PK Enterprise", page_icon="📦", layout="wide", initial_sidebar_state="collapsed")

if 'user' not in st.session_state:
    st.session_state.user = None

apply_enterprise_theme()

# ─── 2. AUTHENTICATION GATEWAY ────────────────────────────────────────
def login_screen():
    # Hide the native sidebar completely
    st.markdown('<style>[data-testid="stSidebar"] { display: none !important; } [data-testid="collapsedControl"] { display: none !important; }</style>', unsafe_allow_html=True)
    
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
                st.session_state.user = {
                    'user_id': user['user_id'],
                    'full_name': user['full_name'],
                    'role': user['role']
                }
                st.rerun()
            else:
                st.error("Authentication failed: Invalid credentials or deactivated account.")

# ─── 3. ENTERPRISE APPLICATION SHELL (HARDCODED LAYOUT) ───────────────
if not st.session_state.user:
    login_screen()
else:
    # ─── FLUSH LEFT OVERRIDE ───
    st.markdown(
        """
        <style>
            /* Permanently kill Streamlit's native sidebar and fluff */
            [data-testid="stSidebar"] { display: none !important; }
            [data-testid="collapsedControl"] { display: none !important; }
            
            /* Eliminate the default Streamlit padding to make the nav flush left */
            .block-container {
                padding-left: 0rem !important;
                padding-right: 2rem !important;
                padding-top: 1.5rem !important;
                max-width: 100% !important;
            }
            
            /* Remove padding from the left-most column specifically */
            [data-testid="column"]:nth-of-type(1) {
                padding-left: 0 !important;
            }
        </style>
        """, 
        unsafe_allow_html=True
    )
    
    # TOP HEADER (Padded slightly to not hit the absolute edge)
    header_col1, header_col2, header_col3 = st.columns([0.2, 7.8, 2])
    with header_col2:
        st.markdown("<h2 style='color: #10b981; margin-bottom: 0; font-weight: 800; letter-spacing: -1px;'>LogiTrack PK Enterprise</h2>", unsafe_allow_html=True)
    with header_col3:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🚪 Secure Logout", use_container_width=True):
            st.session_state.user = None
            st.rerun()
    st.markdown("<hr style='border-color: #1e293b; margin-top: 0; margin-bottom: 2rem;'>", unsafe_allow_html=True)

    # ─── THE HARDCODED GRID LAYOUT ───
    # Split the screen: 20% for Navigation, 80% for the Main Workspace
    nav_col, workspace_col = st.columns([2, 8], gap="large")
    
    user_role = st.session_state.user['role']

    # LEFT COLUMN: Permanent Navigation Rail
    with nav_col:
        st.markdown(f"""
            <div style='background: #0f172a; padding: 15px; border-radius: 0 12px 12px 0; border: 1px solid #1e293b; border-left: none; margin-bottom: 20px;'>
                <p style='color: #94a3b8; font-size: 0.8rem; margin: 0; text-transform: uppercase; letter-spacing: 1px;'>Operator</p>
                <h4 style='color: #f8fafc; margin: 0;'>{st.session_state.user['full_name']}</h4>
                <span style='background: #022c22; color: #34d399; padding: 2px 8px; border-radius: 12px; font-size: 0.75rem; border: 1px solid #065f46; display: inline-block; margin-top: 5px;'>{user_role}</span>
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
                "icon": {"color": "#10b981", "font-size": "1.2rem"}, 
                "nav-link": {"font-size": "0.95rem", "text-align": "left", "margin": "4px 0", "color": "#94a3b8", "font-family": "'Inter', sans-serif", "font-weight": "500", "border-radius": "0 8px 8px 0"},
                "nav-link-selected": {"background-color": "#065f46", "color": "#10b981", "font-weight": "700"},
                "menu-title": {"color": "#f8fafc", "font-size": "0.85rem", "letter-spacing": "2px", "padding-left": "15px", "font-family": "'Inter', sans-serif", "font-weight": "800"}
            }
        )

    # RIGHT COLUMN: The Dynamic Workspace
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