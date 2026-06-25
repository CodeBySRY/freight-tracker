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

# ─── 2. ENTERPRISE LOGIN SCREEN (GOFREIGHT AESTHETIC) ─────────────────────────
def login_screen():
    st.markdown("""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
            
            /* Global Background & Font */
            html, body, .stApp { 
                background-color: #020617 !important; 
                background-image: 
                    radial-gradient(circle at 15% 50%, rgba(16, 185, 129, 0.08), transparent 25%),
                    radial-gradient(circle at 85% 30%, rgba(59, 130, 246, 0.08), transparent 25%);
                color: #e2e8f0; 
                font-family: 'Plus Jakarta Sans', sans-serif; 
                overflow-x: hidden;
            }
            
            /* Hide Streamlit Native Nav */
            [data-testid="stSidebar"], [data-testid="collapsedControl"], #MainMenu, footer, header { display: none !important; }
            
            /* 1. Flexbox Centering for the Entire Viewport */
            .block-container {
                padding: 0 !important;
                max-width: 1100px !important;
                height: 100vh;
                display: flex;
                flex-direction: column;
                justify-content: center;
            }

            /* 2. The Glassmorphic Master Card */
            [data-testid="stHorizontalBlock"] {
                background: rgba(15, 23, 42, 0.6);
                backdrop-filter: blur(20px);
                -webkit-backdrop-filter: blur(20px);
                border: 1px solid rgba(255, 255, 255, 0.05);
                border-radius: 24px;
                box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5), inset 0 1px 0 rgba(255, 255, 255, 0.05);
                overflow: hidden;
                margin: 2rem;
                align-items: stretch !important;
            }

            /* 3. Left Pane - Branding */
            [data-testid="column"]:nth-of-type(1) {
                background: linear-gradient(180deg, rgba(16, 185, 129, 0.05) 0%, rgba(2, 6, 23, 0) 100%);
                padding: 4rem 3.5rem !important;
                border-right: 1px solid rgba(255, 255, 255, 0.05);
                display: flex;
                flex-direction: column;
                justify-content: center;
            }

            /* 4. Right Pane - Form */
            [data-testid="column"]:nth-of-type(2) {
                padding: 4.5rem 3.5rem !important;
                display: flex;
                flex-direction: column;
                justify-content: center;
                background: rgba(2, 6, 23, 0.4);
            }

            /* Typography */
            .login-wordmark { 
                font-size: 3.5rem; 
                font-weight: 800; 
                letter-spacing: -2px; 
                margin-bottom: 0.5rem; 
                background: linear-gradient(135deg, #34d399 0%, #10b981 100%); 
                -webkit-background-clip: text; 
                -webkit-text-fill-color: transparent; 
                line-height: 1.1;
            }
            .login-tagline { 
                font-size: 0.85rem; 
                color: #94a3b8; 
                letter-spacing: 3px; 
                font-weight: 700; 
                text-transform: uppercase; 
                margin-bottom: 3rem; 
            }
            .feature-row { 
                display: flex; 
                align-items: center; 
                gap: 1.2rem; 
                margin-bottom: 1.5rem; 
                color: #cbd5e1; 
                font-size: 1rem; 
                font-weight: 500; 
            }
            .feature-icon {
                display: flex;
                align-items: center;
                justify-content: center;
                width: 36px;
                height: 36px;
                background: rgba(16, 185, 129, 0.1);
                border: 1px solid rgba(16, 185, 129, 0.2);
                border-radius: 10px;
                color: #10b981;
                font-size: 1.1rem;
            }

            /* Form Elements Restyling */
            [data-testid="stForm"] {
                background: transparent !important;
                border: none !important;
                padding: 0 !important;
                box-shadow: none !important;
            }
            .stTextInput input { 
                border-radius: 12px !important; 
                border: 1px solid rgba(255,255,255,0.1) !important; 
                background-color: rgba(15, 23, 42, 0.6) !important; 
                color: white !important; 
                font-size: 1rem !important; 
                padding: 0.85rem 1.2rem !important; 
                transition: all 0.2s;
            }
            .stTextInput input:focus { 
                border-color: #10b981 !important; 
                background-color: rgba(15, 23, 42, 0.9) !important;
                box-shadow: 0 0 0 4px rgba(16,185,129,0.1) !important; 
            }
            .stTextInput label { 
                color: #94a3b8 !important; 
                font-size: 0.8rem !important; 
                font-weight: 600 !important; 
                text-transform: uppercase;
                letter-spacing: 0.5px;
                margin-bottom: 0.5rem !important;
            }
            
            /* CTA Button */
            .stButton > button { 
                border-radius: 12px !important; 
                background: linear-gradient(135deg, #059669, #10b981) !important; 
                color: white !important; 
                border: none !important; 
                font-weight: 700 !important; 
                font-size: 1.05rem !important; 
                padding: 0.75rem !important; 
                margin-top: 1rem !important;
                transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important; 
                box-shadow: 0 8px 20px -8px rgba(16,185,129,0.6) !important; 
            }
            .stButton > button:hover { 
                transform: translateY(-2px) !important; 
                box-shadow: 0 12px 25px -8px rgba(16,185,129,0.8) !important; 
            }

            /* Responsive Media Query for Tablets/Mobiles */
            @media (max-width: 850px) {
                [data-testid="stHorizontalBlock"] { flex-direction: column; margin: 1rem; border-radius: 16px; }
                [data-testid="column"]:nth-of-type(1) { border-right: none; border-bottom: 1px solid rgba(255, 255, 255, 0.05); padding: 3rem 2rem !important; }
                [data-testid="column"]:nth-of-type(2) { padding: 3rem 2rem !important; }
                .login-wordmark { font-size: 2.8rem; }
            }
        </style>
    """, unsafe_allow_html=True)

    # ─── Split-Pane UI Rendering ───
    col_brand, col_form = st.columns([1.1, 1])
    
    with col_brand:
        st.markdown("<h1 class='login-wordmark'>LogiTrack PK</h1>", unsafe_allow_html=True)
        st.markdown("<p class='login-tagline'>Enterprise Freight & Logistics</p>", unsafe_allow_html=True)
        
        st.markdown("""
            <div style='margin-top: 2.5rem;'>
                <div class='feature-row'>
                    <div class='feature-icon'>⚡</div>
                    <div>Real-time BI Analytics Engine</div>
                </div>
                <div class='feature-row'>
                    <div class='feature-icon'>🛡️</div>
                    <div>Zero Trust RBAC Architecture</div>
                </div>
                <div class='feature-row'>
                    <div class='feature-icon'>🌐</div>
                    <div>Sub-second Supply Chain Visibility</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

    with col_form:
        st.markdown("<h3 style='color:#f8fafc; font-size:1.5rem; font-weight:800; letter-spacing:-0.5px; margin-bottom:1.5rem;'>Access Portal</h3>", unsafe_allow_html=True)
        with st.form("login_form"):
            email    = st.text_input("Corporate Email", placeholder="admin@logitrack.pk")
            password = st.text_input("Password", type="password", placeholder="••••••••")
            submit   = st.form_submit_button("Authenticate →", type="primary", use_container_width=True)

        if submit:
            conn = get_db()
            cur  = conn.cursor()
            cur.execute("SELECT * FROM users WHERE email=%s AND is_active=TRUE", (email,))
            user = cur.fetchone()
            conn.close()
            if user and verify_password(password, user['password_hash']):
                st.session_state.user = {
                    'user_id':   user['user_id'],
                    'full_name': user['full_name'],
                    'role':      user['role'],
                }
                st.rerun()
            else:
                st.error("Authentication failed. Invalid credentials or deactivated account.")

# ─── 3. ENTERPRISE APP SHELL ──────────────────────────────────────────────────
if not st.session_state.user:
    login_screen()
else:
    # Apply the global enterprise theme
    apply_enterprise_theme()

    # ── Top bar CSS + layout ───────────────────────────────────────────────
    st.markdown("""
        <style>
            [data-testid="stSidebar"], [data-testid="collapsedControl"] { display: none !important; }
            .block-container {
                padding-left: 1.75rem !important;
                padding-right: 1.75rem !important;
                padding-top: 1.5rem !important;
                max-width: 100% !important;
            }

            .stButton > button[kind="primary"] {
                border-radius: 8px !important;
                background: linear-gradient(135deg, #059669, #10b981) !important;
                color: white !important;
                border: none !important;
                font-weight: 700 !important;
                font-family: 'Inter', sans-serif !important;
                transition: all 0.15s !important;
            }
            .stButton > button[kind="primary"]:hover {
                transform: translateY(-1px) !important;
                box-shadow: 0 6px 16px -4px rgba(16,185,129,0.4) !important;
            }
            .stButton > button:not([kind="primary"]) {
                border-radius: 8px !important;
                border: 1px solid #1a2744 !important;
                color: #4a6080 !important;
                background: #0d1526 !important;
                font-weight: 600 !important;
                font-family: 'Inter', sans-serif !important;
                transition: all 0.15s !important;
            }
            .stButton > button:not([kind="primary"]):hover {
                border-color: #10b981 !important;
                color: #10b981 !important;
                transform: translateY(-1px) !important;
            }
            .stButton > button:disabled {
                opacity: 0.3 !important;
                cursor: not-allowed !important;
                transform: none !important;
            }
        </style>
    """, unsafe_allow_html=True)

    # ── Global top-bar ─────────────────────────────────────────────────────
    hdr_left, hdr_right = st.columns([8, 2])
    with hdr_left:
        st.markdown("""
            <div style='display:flex;align-items:center;gap:0.75rem;'>
                <span style='font-size:1.4rem;'>📦</span>
                <span style='color:#10b981;font-weight:800;font-size:1.35rem;letter-spacing:-0.5px;font-family:Inter,sans-serif;'>LogiTrack PK</span>
                <span style='color:#253355;font-size:0.62rem;font-weight:700;letter-spacing:2.5px;text-transform:uppercase;padding:2px 10px;border:1px solid #1a2744;border-radius:20px;font-family:Inter,sans-serif;'>Enterprise</span>
            </div>
        """, unsafe_allow_html=True)
    with hdr_right:
        if st.button("🚪 Logout", use_container_width=True, key="logout_btn"):
            st.session_state.user = None
            st.rerun()

    st.markdown("<hr style='border:none;border-top:1px solid #111d33;margin:0.75rem 0 1.5rem 0;'>", unsafe_allow_html=True)

    # ── Two-column layout: nav + workspace ────────────────────────────────
    nav_col, workspace_col = st.columns([2, 8], gap="large")
    user_role = st.session_state.user['role']

    # ─ LEFT: Navigation rail ──────────────────────────────────────────────
    with nav_col:
        # User identity card
        role_colors = {
            "System Administrator": ("#10b981", "#022c22", "#065f46"),
            "Dispatcher":           ("#60a5fa", "#172554", "#1d4ed8"),
            "Warehouse Manager":    ("#fb923c", "#431407", "#9a3412"),
        }
        accent, bg_c, border_c = role_colors.get(user_role, ("#64748b", "#1a2744", "#253355"))
        initials = "".join([n[0].upper() for n in st.session_state.user['full_name'].split()[:2]])

        st.markdown(f"""
            <div style='background:#0d1526;border:1px solid #1a2744;border-radius:12px;padding:1.1rem 1.2rem;margin-bottom:1.25rem;'>
                <div style='display:flex;align-items:center;gap:0.75rem;'>
                    <div style='width:36px;height:36px;border-radius:50%;background:{bg_c};border:2px solid {accent};display:flex;align-items:center;justify-content:center;font-size:0.8rem;font-weight:800;color:{accent};flex-shrink:0;'>
                        {initials}
                    </div>
                    <div>
                        <div style='color:#e2e8f0;font-weight:700;font-size:0.9rem;line-height:1.2;'>{st.session_state.user['full_name']}</div>
                        <div style='color:#475569;font-size:0.7rem;font-weight:600;'>Logged in</div>
                    </div>
                </div>
                <div style='margin-top:0.75rem;'>
                    <span style='background:{bg_c};color:{accent};border:1px solid {border_c};padding:3px 10px;border-radius:20px;font-size:0.7rem;font-weight:800;letter-spacing:0.3px;'>{user_role}</span>
                </div>
            </div>
        """, unsafe_allow_html=True)

        # Build nav options based on role
        nav_options = ["Dashboard", "Shipments"]
        nav_icons   = ["grid",      "truck"]
        if user_role in ["System Administrator", "Dispatcher"]:
            nav_options.append("Fleet");   nav_icons.append("shield-check")
        nav_options.append("Reports");     nav_icons.append("graph-up")
        if user_role == "System Administrator":
            nav_options.append("Audit Logs"); nav_icons.append("clock-history")

        selected_module = option_menu(
            menu_title="NAVIGATION",
            options=nav_options,
            icons=nav_icons,
            default_index=0,
            styles={
                "container":        {"padding": "0 !important", "background-color": "transparent"},
                "icon":             {"color": "#10b981", "font-size": "1rem"},
                "nav-link":         {
                    "font-size": "0.875rem",
                    "text-align": "left",
                    "margin": "3px 0",
                    "color": "#4a6080",
                    "font-family": "'Inter', system-ui, sans-serif",
                    "font-weight": "600",
                    "border-radius": "8px",
                    "transition": "all 0.15s",
                    "padding": "10px 14px",
                },
                "nav-link-selected": {
                    "background-color": "#022c22",
                    "color": "#10b981",
                    "font-weight": "700",
                    "border": "1px solid #065f4666",
                },
                "menu-title": {
                    "color": "#253355",
                    "font-size": "0.62rem",
                    "letter-spacing": "1.8px",
                    "padding-left": "14px",
                    "font-family": "'Inter', system-ui, sans-serif",
                    "font-weight": "700",
                    "padding-bottom": "8px",
                    "text-transform": "uppercase",
                },
            },
        )

    # ─ RIGHT: Workspace ───────────────────────────────────────────────────
    with workspace_col:
        if selected_module == "Dashboard":
            dashboard.render_page()
        elif selected_module == "Shipments":
            shipments.render_page()
        elif selected_module == "Fleet":
            fleet.render_page()
        elif selected_module == "Reports":
            reports.render_page()
        elif selected_module == "Audit Logs":
            audit_logs.render_page()