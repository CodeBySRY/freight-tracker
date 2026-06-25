import streamlit as st
from auth import verify_password
from database import get_db
from styles.theme import apply_enterprise_theme
from streamlit_option_menu import option_menu
import pages.dashboard  as dashboard
import pages.shipments  as shipments
import pages.fleet      as fleet
import pages.reports    as reports
import pages.audit_logs as audit_logs

# ─── 1. PAGE CONFIGURATION ────────────────────────────────────────────────────
st.set_page_config(
    page_title="LogiTrack PK Enterprise",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="collapsed",
)

if 'user' not in st.session_state:
    st.session_state.user = None

# ─── 2. SPLIT-PANE ENTERPRISE LOGIN SCREEN ────────────────────────────────────
def login_screen():
    st.markdown("""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
            html, body, .stApp { background-color: #040914 !important; color: #e2e8f0; font-family: 'Plus Jakarta Sans', sans-serif; overflow: hidden; }
            [data-testid="stSidebar"], [data-testid="collapsedControl"], #MainMenu, footer, header { display: none !important; }
            
            /* Remove Streamlit padding for full-bleed split pane */
            .block-container { padding: 0 !important; max-width: 100% !important; }
            [data-testid="stVerticalBlock"] { gap: 0 !important; }
            
            /* Left Pane: Branding */
            [data-testid="column"]:nth-of-type(1) {
                background: radial-gradient(circle at 20% 30%, #0f172a 0%, #020617 100%);
                height: 100vh;
                display: flex;
                flex-direction: column;
                justify-content: center;
                padding: 0 8% !important;
                border-right: 1px solid rgba(255,255,255,0.05);
                position: relative;
            }
            /* Right Pane: Auth Form */
            [data-testid="column"]:nth-of-type(2) {
                background-color: #040914;
                height: 100vh;
                display: flex;
                flex-direction: column;
                justify-content: center;
                padding: 0 10% !important;
            }

            .login-wordmark { font-size: 4.5rem; font-weight: 800; letter-spacing: -2px; margin-bottom: 0; background: linear-gradient(135deg, #10b981 0%, #34d399 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
            .login-tagline { font-size: 0.85rem; color: #64748b; letter-spacing: 4px; font-weight: 700; text-transform: uppercase; margin-bottom: 2rem; }
            .login-feature { display: flex; align-items: center; gap: 1rem; margin-bottom: 1.5rem; color: #94a3b8; font-size: 0.95rem; font-weight: 500; }
            
            /* Glassmorphic Form */
            [data-testid="stForm"] {
                background: rgba(255, 255, 255, 0.02) !important;
                backdrop-filter: blur(16px) !important;
                border: 1px solid rgba(255, 255, 255, 0.05) !important;
                border-radius: 24px !important;
                padding: 3rem !important;
                box-shadow: 0 25px 50px -12px rgba(0,0,0,0.5) !important;
            }
            .stTextInput input { border-radius: 12px !important; border: 1px solid rgba(255,255,255,0.08) !important; background-color: rgba(0,0,0,0.2) !important; color: white !important; font-size: 0.95rem !important; padding: 0.75rem 1rem !important; }
            .stTextInput input:focus { border-color: #10b981 !important; box-shadow: 0 0 0 3px rgba(16,185,129,0.15) !important; }
            .stTextInput label { color: #64748b !important; font-size: 0.8rem !important; font-weight: 600 !important; text-transform: uppercase; letter-spacing: 1px; }
            .stButton > button { border-radius: 12px !important; background: linear-gradient(135deg, #059669, #10b981) !important; color: white !important; border: none !important; font-weight: 700 !important; font-size: 1rem !important; padding: 0.5rem !important; transition: all 0.2s ease !important; box-shadow: 0 10px 20px -10px rgba(16,185,129,0.5) !important; }
            .stButton > button:hover { transform: translateY(-2px) !important; box-shadow: 0 15px 25px -10px rgba(16,185,129,0.6) !important; }
        </style>
    """, unsafe_allow_html=True)

    col_brand, col_form = st.columns([1.2, 1])
    
    with col_brand:
        st.markdown("<h1 class='login-wordmark'>LogiTrack PK</h1>", unsafe_allow_html=True)
        st.markdown("<p class='login-tagline'>Enterprise Freight & Logistics</p>", unsafe_allow_html=True)
        st.markdown("""
            <div class='login-feature'><span style='color:#10b981;font-size:1.2rem;'>⚡</span> Sub-second latency data grids</div>
            <div class='login-feature'><span style='color:#10b981;font-size:1.2rem;'>🔒</span> Zero Trust RBAC Architecture</div>
            <div class='login-feature'><span style='color:#10b981;font-size:1.2rem;'>📊</span> Real-time BI Analytics Engine</div>
        """, unsafe_allow_html=True)

    with col_form:
        with st.form("login_form"):
            st.markdown("<h3 style='text-align:center;margin-bottom:2rem;color:#f8fafc;font-size:1.5rem;font-weight:800;letter-spacing:-0.5px;'>Access Portal</h3>", unsafe_allow_html=True)
            email    = st.text_input("Email Address", placeholder="admin@logitrack.pk")
            password = st.text_input("Password", type="password", placeholder="••••••••")
            st.markdown("<br>", unsafe_allow_html=True)
            submit   = st.form_submit_button("Authenticate System →", type="primary", use_container_width=True)

        if submit:
            conn = get_db()
            cur  = conn.cursor()
            cur.execute("SELECT * FROM users WHERE email=%s AND is_active=TRUE", (email,))
            user = cur.fetchone()
            conn.close()
            if user and verify_password(password, user['password_hash']):
                st.session_state.user = {'user_id': user['user_id'], 'full_name': user['full_name'], 'role': user['role']}
                st.rerun()
            else:
                st.error("Authentication failed. Invalid credentials or deactivated account.")

# ─── 3. ENTERPRISE APP SHELL ──────────────────────────────────────────────────
if not st.session_state.user:
    login_screen()
else:
    apply_enterprise_theme()

    st.markdown("""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
            html, body, .stApp { background-color: #040914 !important; color: #e2e8f0; font-family: 'Plus Jakarta Sans', sans-serif; }
            [data-testid="stSidebar"], [data-testid="collapsedControl"] { display: none !important; }
            .block-container { padding: 1.5rem 3rem !important; max-width: 100% !important; }
            
            /* Global Button Aesthetics */
            .stButton > button[kind="primary"] { border-radius: 10px !important; background: linear-gradient(135deg, #059669, #10b981) !important; border: none !important; font-weight: 700 !important; transition: all 0.2s !important; box-shadow: 0 8px 16px -4px rgba(16,185,129,0.3) !important; }
            .stButton > button[kind="primary"]:hover { transform: translateY(-2px) !important; box-shadow: 0 12px 20px -4px rgba(16,185,129,0.5) !important; }
            .stButton > button:not([kind="primary"]) { border-radius: 10px !important; border: 1px solid rgba(255,255,255,0.1) !important; color: #94a3b8 !important; background: rgba(255,255,255,0.02) !important; font-weight: 600 !important; transition: all 0.2s !important; }
            .stButton > button:not([kind="primary"]):hover { border-color: #10b981 !important; color: #10b981 !important; transform: translateY(-2px) !important; background: rgba(16,185,129,0.05) !important; }
        </style>
    """, unsafe_allow_html=True)

    # Global top-bar
    hdr_left, hdr_right = st.columns([8, 2])
    with hdr_left:
        st.markdown("""
            <div style='display:flex;align-items:center;gap:0.75rem;'>
                <span style='font-size:1.6rem;'>📦</span>
                <span style='color:#10b981;font-weight:800;font-size:1.5rem;letter-spacing:-0.5px;'>LogiTrack PK</span>
                <span style='color:#64748b;font-size:0.65rem;font-weight:800;letter-spacing:2px;text-transform:uppercase;padding:4px 12px;background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.05);border-radius:20px;'>Enterprise</span>
            </div>
        """, unsafe_allow_html=True)
    with hdr_right:
        if st.button("🚪 Secure Logout", use_container_width=True, key="logout_btn"):
            st.session_state.user = None
            st.rerun()

    st.markdown("<hr style='border:none;border-top:1px solid rgba(255,255,255,0.05);margin:1rem 0 2rem 0;'>", unsafe_allow_html=True)

    nav_col, workspace_col = st.columns([2, 8], gap="large")
    user_role = st.session_state.user['role']

    with nav_col:
        role_colors = {"System Administrator": ("#10b981", "rgba(16,185,129,0.1)"), "Dispatcher": ("#3b82f6", "rgba(59,130,246,0.1)"), "Warehouse Manager": ("#f59e0b", "rgba(245,158,11,0.1)")}
        accent, bg_c = role_colors.get(user_role, ("#64748b", "rgba(255,255,255,0.05)"))
        initials = "".join([n[0].upper() for n in st.session_state.user['full_name'].split()[:2]])

        st.markdown(f"""
            <div style='background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.05);border-radius:16px;padding:1.5rem;margin-bottom:1.5rem;box-shadow:0 10px 30px -10px rgba(0,0,0,0.5);'>
                <div style='display:flex;align-items:center;gap:1rem;'>
                    <div style='width:45px;height:45px;border-radius:12px;background:{bg_c};border:1px solid {accent}44;display:flex;align-items:center;justify-content:center;font-size:1rem;font-weight:800;color:{accent};flex-shrink:0;'>{initials}</div>
                    <div>
                        <div style='color:#f8fafc;font-weight:700;font-size:1rem;line-height:1.2;'>{st.session_state.user['full_name']}</div>
                        <div style='color:#64748b;font-size:0.75rem;font-weight:600;'>Authenticated</div>
                    </div>
                </div>
                <div style='margin-top:1rem;'><span style='background:{bg_c};color:{accent};padding:4px 12px;border-radius:8px;font-size:0.75rem;font-weight:700;letter-spacing:0.5px;'>{user_role}</span></div>
            </div>
        """, unsafe_allow_html=True)

        nav_options = ["Dashboard", "Shipments"]
        nav_icons   = ["grid", "truck"]
        if user_role in ["System Administrator", "Dispatcher"]:
            nav_options.append("Fleet"); nav_icons.append("shield-check")
        nav_options.append("Reports"); nav_icons.append("graph-up")
        if user_role == "System Administrator":
            nav_options.append("Audit Logs"); nav_icons.append("clock-history")

        selected_module = option_menu(
            menu_title="NAVIGATION", options=nav_options, icons=nav_icons, default_index=0,
            styles={
                "container": {"padding": "0 !important", "background-color": "transparent"},
                "icon": {"color": "#10b981", "font-size": "1.1rem"},
                "nav-link": {"font-size": "0.95rem", "text-align": "left", "margin": "4px 0", "color": "#94a3b8", "font-family": "'Plus Jakarta Sans', sans-serif", "font-weight": "600", "border-radius": "10px", "transition": "all 0.2s", "padding": "12px 16px"},
                "nav-link-selected": {"background-color": "rgba(16,185,129,0.1)", "color": "#10b981", "font-weight": "800", "border": "1px solid rgba(16,185,129,0.2)"},
                "menu-title": {"color": "#64748b", "font-size": "0.7rem", "letter-spacing": "2px", "padding-left": "16px", "font-weight": "800", "padding-bottom": "12px", "text-transform": "uppercase"},
            }
        )

    with workspace_col:
        if selected_module == "Dashboard": dashboard.render_page()
        elif selected_module == "Shipments": shipments.render_page()
        elif selected_module == "Fleet": fleet.render_page()
        elif selected_module == "Reports": reports.render_page()
        elif selected_module == "Audit Logs": audit_logs.render_page()