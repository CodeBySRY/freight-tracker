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
    page_title="LogiTrack PK | Enterprise Logistics",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="collapsed",
)

if 'user' not in st.session_state:
    st.session_state.user = None

# ─── 2. ENTERPRISE SAAS LANDING & AUTH PORTAL ─────────────────────────────────
def login_screen():
    # ─── GLOBAL LANDING PAGE CSS ───
    st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

/* Core Resets */
html, body, .stApp { 
    background-color: #030712 !important; 
    color: #f8fafc; 
    font-family: 'Plus Jakarta Sans', sans-serif; 
    overflow-x: hidden;
    scroll-behavior: smooth;
}
[data-testid="stSidebar"], [data-testid="collapsedControl"], #MainMenu, footer, header { display: none !important; }
.block-container { padding: 0 !important; max-width: 100% !important; }

/* ── NAVBAR ── */
.lp-navbar {
    position: fixed; top: 0; left: 0; width: 100%; height: 75px;
    background: rgba(3, 7, 18, 0.85); backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px);
    border-bottom: 1px solid rgba(255, 255, 255, 0.05); z-index: 1000;
    display: flex; justify-content: space-between; align-items: center; padding: 0 5%;
}
.nav-logo { font-size: 1.25rem; font-weight: 800; color: #f8fafc; text-decoration: none; display: flex; align-items: center; gap: 0.5rem; }
.nav-links { display: flex; gap: 2.5rem; align-items: center; }
.nav-link { color: #94a3b8; text-decoration: none; font-size: 0.9rem; font-weight: 600; transition: color 0.2s; }
.nav-link:hover { color: #10b981; }

/* ── HERO SECTION (100vh Split) ── */
[data-testid="stHorizontalBlock"]:first-of-type {
    min-height: 100vh;
    padding: 75px 5% 0 5%;
    display: flex;
    align-items: center;
    background: radial-gradient(circle at 80% 20%, rgba(16, 185, 129, 0.04) 0%, transparent 40%),
                radial-gradient(circle at 20% 80%, rgba(59, 130, 246, 0.03) 0%, transparent 40%);
    border-bottom: 1px solid rgba(255,255,255,0.03);
}

/* Left Column: Auth Portal */
[data-testid="column"]:nth-of-type(1) {
    padding: 3rem 4rem !important;
    display: flex;
    flex-direction: column;
    justify-content: center;
}

/* Right Column: Branding */
[data-testid="column"]:nth-of-type(2) {
    padding: 3rem 4rem !important;
    border-left: 1px solid rgba(255, 255, 255, 0.05);
    display: flex;
    flex-direction: column;
    justify-content: center;
    position: relative;
}

/* Auth Form Styling */
.auth-heading { font-size: 2rem; font-weight: 700; letter-spacing: -0.5px; margin-bottom: 0.5rem; }
.auth-sub { color: #94a3b8; font-size: 0.95rem; margin-bottom: 2.5rem; line-height: 1.5; }
[data-testid="stForm"] { background: transparent !important; border: none !important; padding: 0 !important; box-shadow: none !important; }
.stTextInput label { color: #cbd5e1 !important; font-size: 0.8rem !important; font-weight: 600 !important; margin-bottom: 0.5rem !important; text-transform: uppercase; letter-spacing: 1px; }
.stTextInput input { border-radius: 8px !important; border: 1px solid rgba(255,255,255,0.1) !important; background: rgba(255,255,255,0.02) !important; color: white !important; padding: 0.8rem 1rem !important; transition: all 0.2s; }
.stTextInput input:focus { border-color: #10b981 !important; background: rgba(16,185,129,0.05) !important; box-shadow: 0 0 0 3px rgba(16,185,129,0.1) !important; }
.stButton > button { border-radius: 8px !important; background: #f8fafc !important; color: #030712 !important; font-weight: 700 !important; font-size: 0.95rem !important; padding: 0.75rem !important; margin-top: 1rem !important; transition: all 0.2s !important; border: none !important; }
.stButton > button:hover { transform: translateY(-2px) !important; box-shadow: 0 10px 20px -10px rgba(255,255,255,0.3) !important; background: #ffffff !important; }

/* Branding Styling */
.brand-title { font-size: 6rem; font-weight: 800; letter-spacing: -3px; line-height: 1; margin-bottom: 1.5rem; background: linear-gradient(135deg, #f8fafc 0%, #94a3b8 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.brand-desc { font-size: 1.15rem; color: #94a3b8; line-height: 1.7; max-width: 90%; font-weight: 400; }

/* ── LANDING PAGE SECTIONS ── */
.lp-section { padding: 8rem 10%; border-bottom: 1px solid rgba(255,255,255,0.03); scroll-margin-top: 75px; }
.lp-header { font-size: 2.5rem; font-weight: 700; letter-spacing: -1px; margin-bottom: 1rem; color: #f8fafc; text-align: center; }
.lp-sub { font-size: 1.1rem; color: #94a3b8; text-align: center; max-width: 700px; margin: 0 auto 4rem auto; line-height: 1.6; }

/* Grids */
.grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 4rem; align-items: center; }
.grid-3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 2rem; }
.grid-4 { display: grid; grid-template-columns: repeat(4, 1fr); gap: 1.5rem; }

/* Cards */
.lp-card { background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.05); border-radius: 16px; padding: 2.5rem 2rem; transition: all 0.3s ease; }
.lp-card:hover { background: rgba(255,255,255,0.04); transform: translateY(-4px); box-shadow: 0 15px 30px -10px rgba(0,0,0,0.5); border-color: rgba(255,255,255,0.1); }
.card-icon { width: 56px; height: 56px; border-radius: 12px; background: rgba(255,255,255,0.05); display: flex; align-items: center; justify-content: center; font-size: 1.75rem; margin-bottom: 1.5rem; border: 1px solid rgba(255,255,255,0.05); }
.card-title { font-size: 1.25rem; font-weight: 700; color: #f8fafc; margin-bottom: 0.75rem; letter-spacing: -0.5px; }
.card-desc { font-size: 0.95rem; color: #94a3b8; line-height: 1.6; }

/* Target Audience Tags with Hover Animation */
.tag-wrap { display: flex; flex-wrap: wrap; gap: 0.75rem; }
.lp-tag { padding: 0.6rem 1.25rem; border-radius: 24px; background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08); font-size: 0.9rem; color: #cbd5e1; font-weight: 600; cursor: default; transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); }
.lp-tag:hover { transform: translateY(-4px) scale(1.02); background: rgba(16,185,129,0.1); border-color: #10b981; color: #10b981; box-shadow: 0 10px 20px -5px rgba(16,185,129,0.3); }

/* Animated Hub Visualization */
.hub-visual { width: 100%; height: 300px; display: flex; align-items: center; justify-content: center; position: relative; }
.hub-node { width: 24px; height: 24px; background: #10b981; border-radius: 50%; position: relative; box-shadow: 0 0 20px #10b981; z-index: 2; }
.hub-ring { position: absolute; border: 2px solid rgba(16,185,129,0.5); border-radius: 50%; animation: ripple 3s infinite linear; }
.hub-ring:nth-child(2) { animation-delay: 1s; }
.hub-ring:nth-child(3) { animation-delay: 2s; }
@keyframes ripple { 0% { width: 24px; height: 24px; opacity: 1; } 100% { width: 250px; height: 250px; opacity: 0; } }

/* Footer */
.lp-footer { background: #010308; padding: 4rem 10%; border-top: 1px solid rgba(255,255,255,0.05); display: flex; justify-content: space-between; align-items: center; }
.footer-text { color: #64748b; font-size: 0.85rem; }
</style>

<nav class="lp-navbar">
    <a href="#" class="nav-logo">📦 LogiTrack PK</a>
    <div class="nav-links">
        <a href="#overview" class="nav-link">Platform</a>
        <a href="#ecosystem" class="nav-link">Ecosystem</a>
        <a href="#capabilities" class="nav-link">Capabilities</a>
        <a href="#team" class="nav-link">Team</a>
        <a href="#contact" class="nav-link">Support</a>
    </div>
</nav>
""", unsafe_allow_html=True)

    # ─── 2.1 HERO SECTION (Streamlit Columns for Auth Logic) ───
    col_auth, col_brand = st.columns([1, 1.2])
    
    with col_auth:
        st.markdown("<div class='auth-heading'>Operational access</div>", unsafe_allow_html=True)
        st.markdown("<div class='auth-sub'>Authenticate to manage your enterprise logistics and freight workflows.</div>", unsafe_allow_html=True)
        
        with st.form("login_form"):
            email    = st.text_input("Email", placeholder="admin@logitrack.pk")
            password = st.text_input("Password", type="password", placeholder="••••••••")
            submit   = st.form_submit_button("Sign in to workspace →", use_container_width=True)

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

    with col_brand:
        st.markdown("""
<div class='brand-title'>LogiTrack PK</div>
<div class='brand-desc'>A modern freight operations and shipment visibility platform built specifically to streamline Pakistan's complex logistics ecosystem.</div>
""", unsafe_allow_html=True)

    # ─── 2.2 MARKETING & DOCUMENTATION SECTIONS (Raw HTML) ───
    # MUST BE FLUSH LEFT TO PREVENT MARKDOWN INDENTATION BUGS
    st.markdown("""
<section id='overview' class='lp-section'>
<div class='lp-header'>Centralized Freight Operations</div>
<div class='lp-sub'>LogiTrack PK replaces fragmented workflows with a single source of truth. Command your fleet, coordinate dispatch operations, and track deliveries with unprecedented clarity.</div>
<div class='grid-3'>
<div class='lp-card'>
<div class='card-icon'>👁️</div>
<div class='card-title'>Shipment Visibility</div>
<div class='card-desc'>Monitor the exact status of every contract in your network from origin loading to destination sign-off.</div>
</div>
<div class='lp-card'>
<div class='card-icon'>🚚</div>
<div class='card-title'>Carrier Management</div>
<div class='card-desc'>Maintain a live ledger of your fleet's capacity, availability, and active deployment status.</div>
</div>
<div class='lp-card'>
<div class='card-icon'>⚡</div>
<div class='card-title'>Dispatch Coordination</div>
<div class='card-desc'>Seamlessly assign pending orders to available carriers using intelligent, zero-friction workflows.</div>
</div>
</div>
</section>

<section id='ecosystem' class='lp-section' style='background: rgba(255,255,255,0.01);'>
<div class='grid-2'>
<div>
<div class='lp-header' style='text-align: left;'>Tailored for <span style="color:#10b981; font-family:'Plus Jakarta Sans', sans-serif; font-weight:800; text-shadow: 0 0 20px rgba(16,185,129,0.3);">Pakistan's</span> Ecosystem</div>
<div class='lp-sub' style='text-align: left; margin-bottom: 2rem;'>
Designed exclusively for the operational realities of the domestic supply chain. We serve the critical corridors connecting <b>Karachi, Lahore, Islamabad, Faisalabad, Multan, Peshawar, and Quetta.</b>
</div>
<div class='tag-wrap'>
<span class='lp-tag'>Freight Forwarders</span>
<span class='lp-tag'>3PL Providers</span>
<span class='lp-tag'>Fleet Operators</span>
<span class='lp-tag'>Warehouse Managers</span>
<span class='lp-tag'>Dispatch Coordinators</span>
<span class='lp-tag'>Intercity Networks</span>
</div>
</div>
<div style='background: rgba(16,185,129,0.02); border: 1px solid rgba(16,185,129,0.1); border-radius: 24px; padding: 2rem; display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%; overflow: hidden;'>
<div class='hub-visual'>
<div class='hub-node'></div>
<div class='hub-ring'></div>
<div class='hub-ring'></div>
<div class='hub-ring'></div>
</div>
<div style='color: #10b981; font-weight: 800; font-size: 1.2rem; letter-spacing: 4px; text-transform: uppercase; margin-top: 1rem;'>Network Hub</div>
</div>
</div>
</section>

<section id='capabilities' class='lp-section'>
<div class='lp-header'>Core Platform Capabilities</div>
<div class='lp-sub'>Enterprise-grade architecture ensuring security, speed, and analytical depth.</div>
<div class='grid-4'>
<div class='lp-card'><div class='card-title' style='color:#10b981;'>Real-Time Tracking</div><div class='card-desc'>Live status updates for all active freight.</div></div>
<div class='lp-card'><div class='card-title' style='color:#3b82f6;'>Audit Logging</div><div class='card-desc'>Immutable, cryptographic history of all actions.</div></div>
<div class='lp-card'><div class='card-title' style='color:#f59e0b;'>Zero Trust RBAC</div><div class='card-desc'>Strict role-based access to operational modules.</div></div>
<div class='lp-card'><div class='card-title' style='color:#8b5cf6;'>Performance Analytics</div><div class='card-desc'>Live Plotly data grids and network BI.</div></div>
</div>
</section>

<section id='team' class='lp-section' style='background: rgba(255,255,255,0.01);'>
<div class='lp-header'>Platform Engineering</div>
<div class='lp-sub'>Designed, architected, and developed by software engineers committed to modernizing industrial logistics infrastructure.</div>
<div class='grid-3'>
<div class='lp-card' style='text-align: center; padding: 3rem 2rem;'>
<div style='width: 72px; height: 72px; border-radius: 50%; background: rgba(255,255,255,0.05); margin: 0 auto 1.5rem auto; display: flex; align-items: center; justify-content: center; font-size: 1.5rem; border: 1px solid rgba(255,255,255,0.1); font-weight: 700;'>SR</div>
<div class='card-title'>Shayan Rizwan</div>
<div class='card-desc'>Platform Architecture</div>
</div>
<div class='lp-card' style='text-align: center; padding: 3rem 2rem;'>
<div style='width: 72px; height: 72px; border-radius: 50%; background: rgba(255,255,255,0.05); margin: 0 auto 1.5rem auto; display: flex; align-items: center; justify-content: center; font-size: 1.5rem; border: 1px solid rgba(255,255,255,0.1); font-weight: 700;'>AS</div>
<div class='card-title'>Agha Salaat</div>
<div class='card-desc'>Systems Engineering</div>
</div>
<div class='lp-card' style='text-align: center; padding: 3rem 2rem;'>
<div style='width: 72px; height: 72px; border-radius: 50%; background: rgba(255,255,255,0.05); margin: 0 auto 1.5rem auto; display: flex; align-items: center; justify-content: center; font-size: 1.5rem; border: 1px solid rgba(255,255,255,0.1); font-weight: 700;'>AM</div>
<div class='card-title'>Anzar Mubashir</div>
<div class='card-desc'>Backend Infrastructure</div>
</div>
</div>
</section>

<section id='contact' class='lp-section' style='text-align: center;'>
<div class='card-icon' style='margin: 0 auto 1.5rem auto; width: 72px; height: 72px; font-size: 2rem;'>💬</div>
<div class='lp-header'>Operational Support</div>
<div class='lp-sub'>We value user feedback and continuously improve operational reliability. For issue reporting, technical assistance, or feature requests, contact our engineering team.</div>
<a href='mailto:u2024585@giki.edu.pk' style='display: inline-block; background: #f8fafc; color: #030712; padding: 1rem 2.5rem; border-radius: 8px; font-weight: 700; text-decoration: none; font-size: 1rem; transition: transform 0.2s; box-shadow: 0 10px 25px rgba(255,255,255,0.2);'>u2024585@giki.edu.pk</a>
<div style='margin-top: 1.5rem; color: #64748b; font-size: 0.9rem; font-weight: 600;'>Expected Response SLA: Under 24 Hours</div>
</section>

<footer class='lp-footer'>
<div class='footer-text'>
<strong style='color:#f8fafc; font-size: 1.1rem;'>📦 LogiTrack PK</strong><br><br>
© 2026 LogiTrack Systems. All rights reserved.
</div>
<div class='footer-text' style='text-align: right;'>
Version 2.4.0 (Enterprise Build)<br><br>
<span style='opacity: 0.7;'>Protected by Zero Trust Security Architecture.</span>
</div>
</footer>
""", unsafe_allow_html=True)


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
                border-radius: 8px !important; background: linear-gradient(135deg, #059669, #10b981) !important;
                color: white !important; border: none !important; font-weight: 700 !important; transition: all 0.15s !important;
            }
            .stButton > button[kind="primary"]:hover { transform: translateY(-1px) !important; box-shadow: 0 6px 16px -4px rgba(16,185,129,0.4) !important; }
            
            .stButton > button:not([kind="primary"]) {
                border-radius: 8px !important; border: 1px solid rgba(255,255,255,0.1) !important; color: #94a3b8 !important;
                background: transparent !important; font-weight: 600 !important; transition: all 0.15s !important;
            }
            .stButton > button:not([kind="primary"]):hover { border-color: #10b981 !important; color: #10b981 !important; transform: translateY(-1px) !important; background: rgba(16,185,129,0.05) !important;}
            .stButton > button:disabled { opacity: 0.3 !important; cursor: not-allowed !important; transform: none !important; }
        </style>
    """, unsafe_allow_html=True)

    # ── Global top-bar ─────────────────────────────────────────────────────
    hdr_left, hdr_right = st.columns([8, 2])
    with hdr_left:
        st.markdown("""
            <div style='display:flex;align-items:center;gap:0.75rem;'>
                <span style='font-size:1.4rem;'>📦</span>
                <span style='color:#10b981;font-weight:800;font-size:1.35rem;letter-spacing:-0.5px;'>LogiTrack PK</span>
                <span style='color:#94a3b8;font-size:0.62rem;font-weight:700;letter-spacing:2.5px;text-transform:uppercase;padding:2px 10px;border:1px solid rgba(255,255,255,0.1);border-radius:20px;'>Enterprise</span>
            </div>
        """, unsafe_allow_html=True)
    with hdr_right:
        if st.button("🚪 Logout", use_container_width=True, key="logout_btn"):
            st.session_state.user = None
            st.rerun()

    st.markdown("<hr style='border:none;border-top:1px solid rgba(255,255,255,0.05);margin:0.75rem 0 1.5rem 0;'>", unsafe_allow_html=True)

    # ── Two-column layout: nav + workspace ────────────────────────────────
    nav_col, workspace_col = st.columns([2, 8], gap="large")
    user_role = st.session_state.user['role']

    # ─ LEFT: Navigation rail ──────────────────────────────────────────────
    with nav_col:
        role_colors = {
            "System Administrator": ("#10b981", "rgba(16,185,129,0.1)", "rgba(16,185,129,0.2)"),
            "Dispatcher":           ("#60a5fa", "rgba(59,130,246,0.1)", "rgba(59,130,246,0.2)"),
            "Warehouse Manager":    ("#fb923c", "rgba(245,158,11,0.1)", "rgba(245,158,11,0.2)"),
        }
        accent, bg_c, border_c = role_colors.get(user_role, ("#64748b", "rgba(255,255,255,0.05)", "rgba(255,255,255,0.1)"))
        initials = "".join([n[0].upper() for n in st.session_state.user['full_name'].split()[:2]])

        st.markdown(f"""
            <div style='background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.05);border-radius:12px;padding:1.1rem 1.2rem;margin-bottom:1.25rem;'>
                <div style='display:flex;align-items:center;gap:0.75rem;'>
                    <div style='width:36px;height:36px;border-radius:50%;background:{bg_c};border:1px solid {border_c};display:flex;align-items:center;justify-content:center;font-size:0.8rem;font-weight:800;color:{accent};flex-shrink:0;'>
                        {initials}
                    </div>
                    <div>
                        <div style='color:#e2e8f0;font-weight:700;font-size:0.9rem;line-height:1.2;'>{st.session_state.user['full_name']}</div>
                        <div style='color:#64748b;font-size:0.7rem;font-weight:600;'>Logged in</div>
                    </div>
                </div>
                <div style='margin-top:0.75rem;'>
                    <span style='background:{bg_c};color:{accent};border:1px solid {border_c};padding:3px 10px;border-radius:20px;font-size:0.7rem;font-weight:800;letter-spacing:0.3px;'>{user_role}</span>
                </div>
            </div>
        """, unsafe_allow_html=True)

        nav_options = ["Dashboard", "Shipments"]
        nav_icons   = ["grid",      "truck"]
        if user_role in ["System Administrator", "Dispatcher"]:
            nav_options.append("Fleet");   nav_icons.append("shield-check")
        nav_options.append("Reports");     nav_icons.append("graph-up")
        if user_role == "System Administrator":
            nav_options.append("Audit Logs"); nav_icons.append("clock-history")

        selected_module = option_menu(
            menu_title="NAVIGATION", options=nav_options, icons=nav_icons, default_index=0,
            styles={
                "container":        {"padding": "0 !important", "background-color": "transparent"},
                "icon":             {"color": "#10b981", "font-size": "1rem"},
                "nav-link":         {"font-size": "0.875rem", "text-align": "left", "margin": "3px 0", "color": "#94a3b8", "font-weight": "600", "border-radius": "8px", "transition": "all 0.15s", "padding": "10px 14px"},
                "nav-link-selected": {"background-color": "rgba(16,185,129,0.1)", "color": "#10b981", "font-weight": "700", "border": "1px solid rgba(16,185,129,0.2)"},
                "menu-title":       {"color": "#64748b", "font-size": "0.62rem", "letter-spacing": "1.8px", "padding-left": "14px", "font-weight": "700", "padding-bottom": "8px", "text-transform": "uppercase"},
            },
        )

    # ─ RIGHT: Workspace ───────────────────────────────────────────────────
    with workspace_col:
        if selected_module == "Dashboard": dashboard.render_page()
        elif selected_module == "Shipments": shipments.render_page()
        elif selected_module == "Fleet": fleet.render_page()
        elif selected_module == "Reports": reports.render_page()
        elif selected_module == "Audit Logs": audit_logs.render_page()