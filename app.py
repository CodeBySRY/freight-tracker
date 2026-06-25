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
    # ─── GLOBAL LANDING PAGE CSS & DYNAMIC THEME ENGINE ───
    st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

/* Dynamic Theme Variables */
body {
    --bg-main: #030712;
    --text-main: #f8fafc;
    --text-sub: #94a3b8;
    --text-muted: #64748b;
    --border-light: rgba(255,255,255,0.03);
    --border-mid: rgba(255,255,255,0.05);
    --border-heavy: rgba(255,255,255,0.1);
    --nav-bg: rgba(3, 7, 18, 0.75);
    --card-bg: rgba(255,255,255,0.015);
    --card-hover: rgba(255,255,255,0.03);
    --btn-bg: #f8fafc;
    --btn-text: #030712;
    --footer-bg: #010206;
    --title-grad: linear-gradient(135deg, #f8fafc 0%, #94a3b8 100%);
}

body.light-theme {
    --bg-main: #f8fafc;
    --text-main: #0f172a;
    --text-sub: #475569;
    --text-muted: #64748b;
    --border-light: rgba(0,0,0,0.05);
    --border-mid: rgba(0,0,0,0.1);
    --border-heavy: rgba(0,0,0,0.2);
    --nav-bg: rgba(248, 250, 252, 0.85);
    --card-bg: #ffffff;
    --card-hover: #f1f5f9;
    --btn-bg: #0f172a;
    --btn-text: #ffffff;
    --footer-bg: #f1f5f9;
    --title-grad: linear-gradient(135deg, #0f172a 0%, #475569 100%);
}

/* Core Resets & Application Override */
html, body, .stApp { 
    background-color: var(--bg-main) !important; 
    color: var(--text-main) !important; 
    font-family: 'Plus Jakarta Sans', sans-serif; 
    overflow-x: hidden;
    scroll-behavior: smooth;
    transition: background-color 0.3s ease, color 0.3s ease;
}
[data-testid="stSidebar"], [data-testid="collapsedControl"], #MainMenu, footer, header { display: none !important; }
.block-container { padding: 0 !important; max-width: 100% !important; }

/* ── PREMIUM FLOATING NAVBAR ── */
.floating-nav {
    position: fixed; top: 1.5rem; left: 50%; transform: translateX(-50%);
    width: 90%; max-width: 1200px; height: 64px;
    background: var(--nav-bg); backdrop-filter: blur(24px); -webkit-backdrop-filter: blur(24px);
    border: 1px solid var(--border-heavy); border-radius: 100px;
    display: flex; justify-content: space-between; align-items: center; padding: 0 1.5rem 0 2rem;
    z-index: 1000; box-shadow: 0 20px 40px -15px rgba(0,0,0,0.5);
    transition: all 0.3s ease;
}
@media (max-width: 1024px) { .floating-nav { width: 95%; border-radius: 24px; } .nav-links { display: none !important; } }

.nav-brand-group { display: flex; align-items: center; gap: 1rem; }
.nav-logo { font-size: 1.25rem; font-weight: 800; color: var(--text-main) !important; text-decoration: none !important; display: flex; align-items: center; gap: 0.5rem; letter-spacing: -0.5px; }
.nav-divider { width: 1px; height: 24px; background: var(--border-heavy); }
.nav-subtitle { font-size: 0.75rem; font-weight: 600; color: var(--text-sub); text-transform: uppercase; letter-spacing: 1.5px; }

.nav-links { display: flex; gap: 2rem; align-items: center; }
.nav-link { color: var(--text-sub) !important; text-decoration: none !important; font-size: 0.85rem; font-weight: 600; transition: all 0.2s ease; position: relative; }
.nav-link:hover { color: #10b981 !important; }
.nav-link::after { content: ''; position: absolute; width: 0; height: 2px; bottom: -4px; left: 0; background: #10b981; transition: width 0.2s ease; border-radius: 2px; }
.nav-link:hover::after { width: 100%; }

.nav-controls { display: flex; align-items: center; gap: 1rem; }
.theme-toggle { cursor: pointer; font-size: 1.2rem; user-select: none; transition: transform 0.2s; }
.theme-toggle:hover { transform: scale(1.15) rotate(15deg); }
.nav-cta { 
    background: var(--card-bg); border: 1px solid var(--border-heavy); color: var(--text-main) !important; text-decoration: none !important;
    padding: 0.5rem 1.25rem; border-radius: 100px; font-size: 0.85rem; font-weight: 700; transition: all 0.3s ease;
}
.nav-cta:hover { background: var(--text-main); color: var(--bg-main) !important; box-shadow: 0 0 20px rgba(16,185,129,0.2); }

/* ── HERO SECTION & BRAND HIERARCHY ── */
[data-testid="stHorizontalBlock"]:first-of-type {
    min-height: 100vh; padding: 120px 8% 40px 8%; align-items: center;
    background-image: radial-gradient(circle at 15% 50%, rgba(16, 185, 129, 0.05), transparent 40%), linear-gradient(var(--border-light) 1px, transparent 1px), linear-gradient(90deg, var(--border-light) 1px, transparent 1px);
    background-size: 100% 100%, 60px 60px, 60px 60px; background-position: center center;
    border-bottom: 1px solid var(--border-light);
}

[data-testid="column"]:nth-of-type(1) { padding-right: 4rem !important; }
.hero-super { color: #10b981; font-size: 0.85rem; font-weight: 700; letter-spacing: 2px; text-transform: uppercase; margin-bottom: 1.5rem; display: block; }
.brand-title { font-size: 5rem; font-weight: 800; letter-spacing: -2px; line-height: 1.05; margin-bottom: 1.5rem; background: var(--title-grad); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.brand-desc { font-size: 1.15rem; color: var(--text-sub); line-height: 1.6; max-width: 90%; font-weight: 500; margin-bottom: 3rem; }

/* Corridor Visualization */
.corridor-map { position: relative; height: 60px; display: flex; align-items: center; margin-top: 2rem; width: 90%; }
.corridor-line { position: absolute; width: 100%; height: 2px; background: var(--border-heavy); top: 50%; transform: translateY(-50%); }
.corridor-flow { position: absolute; width: 30%; height: 2px; background: linear-gradient(90deg, transparent, #10b981, transparent); top: 50%; transform: translateY(-50%); animation: freightFlow 3s infinite linear; }
.corridor-node { position: absolute; display: flex; flex-direction: column; align-items: center; gap: 8px; top: 50%; transform: translate(-50%, -15px); }
.node-dot { width: 12px; height: 12px; background: var(--bg-main); border: 2px solid #3b82f6; border-radius: 50%; z-index: 2; transition: all 0.3s; }
.corridor-node:hover .node-dot { background: #10b981; border-color: #10b981; box-shadow: 0 0 15px rgba(16,185,129,0.5); transform: scale(1.2); }
.node-label { font-size: 0.7rem; font-weight: 700; color: var(--text-muted); letter-spacing: 1px; transition: color 0.3s; }
.corridor-node:hover .node-label { color: var(--text-main); }
@keyframes freightFlow { 0% { left: -30%; } 100% { left: 100%; } }

/* ── AUTH PORTAL ── */
[data-testid="column"]:nth-of-type(2) {
    background: var(--card-bg); backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px);
    border: 1px solid var(--border-heavy); border-radius: 24px; padding: 3.5rem 3rem !important;
    box-shadow: 0 25px 50px -12px rgba(0,0,0,0.3); position: relative; overflow: hidden;
}
[data-testid="column"]:nth-of-type(2)::before { content: ''; position: absolute; top: 0; left: 0; width: 100%; height: 4px; background: linear-gradient(90deg, #10b981, #3b82f6); }

.auth-heading { font-size: 1.5rem; font-weight: 700; letter-spacing: -0.5px; margin-bottom: 0.5rem; color: var(--text-main); }
.auth-sub { color: var(--text-sub); font-size: 0.9rem; margin-bottom: 2rem; font-weight: 500; }
[data-testid="stForm"] { background: transparent !important; border: none !important; padding: 0 !important; box-shadow: none !important; }
.stTextInput label { color: var(--text-sub) !important; font-size: 0.75rem !important; font-weight: 700 !important; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 0.5rem !important; }
.stTextInput input { border-radius: 10px !important; border: 1px solid var(--border-heavy) !important; background: var(--bg-main) !important; color: var(--text-main) !important; padding: 0.8rem 1rem !important; font-size: 0.95rem !important; transition: all 0.2s; }
.stTextInput input:focus { border-color: #10b981 !important; box-shadow: 0 0 0 3px rgba(16,185,129,0.15) !important; }
.stButton > button { border-radius: 10px !important; background: var(--btn-bg) !important; color: var(--btn-text) !important; font-weight: 800 !important; font-size: 0.95rem !important; padding: 0.8rem !important; margin-top: 1.5rem !important; border: none !important; transition: all 0.3s !important; }
.stButton > button:hover { transform: translateY(-2px) !important; box-shadow: 0 15px 30px -10px rgba(16,185,129,0.4) !important; }

/* ── DOCUMENTATION SECTIONS ── */
.lp-section { padding: 8rem 10%; border-bottom: 1px solid var(--border-light); scroll-margin-top: 80px; }
.lp-header { font-size: 2.5rem; font-weight: 700; letter-spacing: -1px; margin-bottom: 1rem; color: var(--text-main); text-align: center; }
.lp-sub { font-size: 1.1rem; color: var(--text-sub); text-align: center; max-width: 700px; margin: 0 auto 4rem auto; line-height: 1.6; }

.grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 4rem; align-items: center; }
.grid-3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 2rem; }
.grid-4 { display: grid; grid-template-columns: repeat(4, 1fr); gap: 1.5rem; }

.lp-card { background: var(--card-bg); border: 1px solid var(--border-mid); border-radius: 20px; padding: 2.5rem 2rem; transition: all 0.3s; }
.lp-card:hover { background: var(--card-hover); transform: translateY(-4px); box-shadow: 0 20px 40px -10px rgba(0,0,0,0.1); border-color: var(--border-heavy); }
.card-icon { width: 48px; height: 48px; border-radius: 12px; background: var(--border-mid); display: flex; align-items: center; justify-content: center; font-size: 1.5rem; margin-bottom: 1.5rem; border: 1px solid var(--border-heavy); }
.card-title { font-size: 1.2rem; font-weight: 700; color: var(--text-main); margin-bottom: 0.75rem; letter-spacing: -0.5px; }
.card-desc { font-size: 0.95rem; color: var(--text-sub); line-height: 1.6; }

.tag-wrap { display: flex; flex-wrap: wrap; gap: 0.75rem; }
.lp-tag { padding: 0.6rem 1.25rem; border-radius: 24px; background: var(--card-bg); border: 1px solid var(--border-heavy); font-size: 0.9rem; color: var(--text-sub); font-weight: 600; transition: all 0.3s; cursor: default; }
.lp-tag:hover { transform: translateY(-3px) scale(1.02); background: rgba(16,185,129,0.08); border-color: rgba(16,185,129,0.3); color: #10b981; box-shadow: 0 10px 20px -5px rgba(16,185,129,0.2); }

.lp-footer { background: var(--footer-bg); padding: 4rem 10%; border-top: 1px solid var(--border-mid); display: flex; justify-content: space-between; align-items: center; }
.footer-text { color: var(--text-muted); font-size: 0.85rem; }
</style>

<div id="auth-portal" style="position: absolute; top: 0;"></div>

<nav class="floating-nav">
    <div class="nav-brand-group">
        <a href="#auth-portal" class="nav-logo">
            <span id="easter-egg-btn" style="cursor:pointer;" title="Honk!">📦</span>
            LogiTrack
        </a>
        <div class="nav-divider"></div>
        <span class="nav-subtitle">Enterprise OS</span>
    </div>
    <div class="nav-links">
        <a href="#network" class="nav-link">Network Maps</a>
        <a href="#ecosystem" class="nav-link">Pakistan Corridors</a>
        <a href="#capabilities" class="nav-link">Platform Capabilities</a>
        <a href="#team" class="nav-link">Engineering</a>
    </div>
    <div class="nav-controls">
        <div class="theme-toggle" id="theme-toggle-btn" title="Toggle Light/Dark Mode">🌓</div>
        <a href="#auth-portal" class="nav-cta">System Access</a>
    </div>
</nav>

<img src="dummy" style="display:none;" onerror="if(!window.lLoaded){window.lLoaded=true;var t=document.getElementById('theme-toggle-btn');if(t){t.addEventListener('click',function(){document.body.classList.toggle('light-theme');});}var e=document.getElementById('easter-egg-btn');if(e){var c=0;e.addEventListener('click',function(ev){ev.preventDefault();c++;if(c===3){c=0;var tr=document.createElement('div');tr.innerHTML='🚚💨';tr.style.cssText='position:fixed;top:90px;left:-100px;font-size:60px;z-index:9999;transition:left 2.5s cubic-bezier(0.25, 1, 0.5, 1);';document.body.appendChild(tr);setTimeout(function(){tr.style.left='120vw';},50);setTimeout(function(){tr.remove();},2600);}});}}">
""", unsafe_allow_html=True)

    # ─── 2.1 HERO SECTION (Streamlit Columns) ───
    col_brand, col_auth = st.columns([1.4, 1], gap="large")
    
    with col_brand:
        st.markdown("""
<span class='hero-super'>Freight Intelligence Network</span>
<div class='brand-title'>Logistics visibility,<br>engineered for scale.</div>
<div class='brand-desc'>The centralized operating system for Pakistan's freight network. Command your fleet, track shipments, and coordinate dispatch operations with unprecedented clarity.</div>

<div class='corridor-map'>
    <div class='corridor-line'></div>
    <div class='corridor-flow'></div>
    <div class='corridor-node' style='left: 0%;'><div class='node-dot'></div><span class='node-label'>KHI</span></div>
    <div class='corridor-node' style='left: 33%;'><div class='node-dot'></div><span class='node-label'>LHE</span></div>
    <div class='corridor-node' style='left: 66%;'><div class='node-dot'></div><span class='node-label'>ISB</span></div>
    <div class='corridor-node' style='left: 100%;'><div class='node-dot'></div><span class='node-label'>PEW</span></div>
</div>
""", unsafe_allow_html=True)

    with col_auth:
        st.markdown("<div class='auth-heading'>Authentication</div>", unsafe_allow_html=True)
        st.markdown("<div class='auth-sub'>Secure terminal for authorized personnel.</div>", unsafe_allow_html=True)
        
        with st.form("login_form"):
            email    = st.text_input("Email", placeholder="admin@logitrack.pk")
            password = st.text_input("Password", type="password", placeholder="••••••••")
            submit   = st.form_submit_button("Enter Workspace →", use_container_width=True)

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

    # ─── 2.2 MARKETING & DOCUMENTATION SECTIONS (Flush HTML) ───
    st.markdown("""
<section id='network' class='lp-section'>
<div class='lp-header'>Centralized Operations</div>
<div class='lp-sub'>LogiTrack PK replaces fragmented workflows with a single source of truth. Command your fleet, coordinate dispatch operations, and track deliveries with unparalleled operational visibility.</div>
<div class='grid-3'>
<div class='lp-card'>
<div class='card-icon'>👁️</div>
<div class='card-title'>Shipment Telematics</div>
<div class='card-desc'>Monitor the exact status of every contract in your network from origin loading dock to destination sign-off.</div>
</div>
<div class='lp-card'>
<div class='card-icon'>🚚</div>
<div class='card-title'>Carrier Ledgers</div>
<div class='card-desc'>Maintain a live, centralized registry of your fleet's capacity, availability, and active deployment status.</div>
</div>
<div class='lp-card'>
<div class='card-icon'>⚡</div>
<div class='card-title'>Dispatch Protocols</div>
<div class='card-desc'>Seamlessly assign pending orders to available carriers using intelligent, zero-friction workflows.</div>
</div>
</div>
</section>

<section id='ecosystem' class='lp-section' style='background: var(--card-bg);'>
<div class='grid-2'>
<div>
<div class='lp-header' style='text-align: left;'>Architected for <span style="color:#10b981; font-family:'Plus Jakarta Sans', sans-serif; font-weight:800; text-shadow: 0 0 20px rgba(16,185,129,0.2);">Pakistan's</span> Ecosystem</div>
<div class='lp-sub' style='text-align: left; margin-bottom: 2rem;'>
Designed exclusively for the operational realities of the domestic supply chain. We serve the critical transport corridors connecting <b>Karachi, Lahore, Islamabad, Faisalabad, Multan, Peshawar, and Quetta.</b>
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
<div style='background: rgba(16,185,129,0.03); border: 1px solid rgba(16,185,129,0.1); border-radius: 24px; padding: 3rem; display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%; position: relative; overflow: hidden;'>
<div style='width: 100px; height: 100px; border-radius: 50%; border: 1px solid rgba(16,185,129,0.3); display: flex; align-items: center; justify-content: center; position: relative;'>
    <div style='width: 60px; height: 60px; border-radius: 50%; background: rgba(16,185,129,0.1); display: flex; align-items: center; justify-content: center;'>
        <div style='width: 20px; height: 20px; border-radius: 50%; background: #10b981; box-shadow: 0 0 20px #10b981;'></div>
    </div>
    <div style='position: absolute; width: 100%; height: 100%; border-radius: 50%; border: 2px solid #10b981; border-top-color: transparent; animation: spin 4s linear infinite;'></div>
</div>
<div style='color: #10b981; font-weight: 700; font-size: 0.85rem; letter-spacing: 4px; text-transform: uppercase; margin-top: 1.5rem;'>Central Hub Active</div>
<style>@keyframes spin { 100% { transform: rotate(360deg); } }</style>
</div>
</div>
</section>

<section id='capabilities' class='lp-section'>
<div class='lp-header'>Core Platform Capabilities</div>
<div class='lp-sub'>Enterprise-grade architecture ensuring high-availability, cryptographic security, and analytical depth.</div>
<div class='grid-4'>
<div class='lp-card' style='padding: 2rem 1.5rem;'><div class='card-title' style='color:#10b981; font-size:1.1rem;'>Real-Time Tracking</div><div class='card-desc' style='font-size:0.85rem;'>Live status updates for all active freight.</div></div>
<div class='lp-card' style='padding: 2rem 1.5rem;'><div class='card-title' style='color:#3b82f6; font-size:1.1rem;'>Audit Logging</div><div class='card-desc' style='font-size:0.85rem;'>Immutable, cryptographic history of all actions.</div></div>
<div class='lp-card' style='padding: 2rem 1.5rem;'><div class='card-title' style='color:#f59e0b; font-size:1.1rem;'>Zero Trust RBAC</div><div class='card-desc' style='font-size:0.85rem;'>Strict role-based access to operational modules.</div></div>
<div class='lp-card' style='padding: 2rem 1.5rem;'><div class='card-title' style='color:#8b5cf6; font-size:1.1rem;'>BI Analytics</div><div class='card-desc' style='font-size:0.85rem;'>Live Plotly data grids and network intelligence.</div></div>
</div>
</section>

<section id='team' class='lp-section' style='background: var(--card-bg);'>
<div class='lp-header'>Platform Engineering</div>
<div class='lp-sub'>Designed, architected, and developed by software engineers committed to modernizing industrial logistics infrastructure.</div>
<div class='grid-3'>
<div class='lp-card' style='text-align: center; padding: 3rem 2rem;'>
<div style='width: 56px; height: 56px; border-radius: 50%; background: var(--border-mid); margin: 0 auto 1.2rem auto; display: flex; align-items: center; justify-content: center; font-size: 1.1rem; border: 1px solid var(--border-heavy); font-weight: 700; color: var(--text-main);'>SR</div>
<div class='card-title' style='font-size:1.1rem;'>Shayan Rizwan</div>
<div class='card-desc' style='font-size:0.85rem;'>Platform Architecture</div>
</div>
<div class='lp-card' style='text-align: center; padding: 3rem 2rem;'>
<div style='width: 56px; height: 56px; border-radius: 50%; background: var(--border-mid); margin: 0 auto 1.2rem auto; display: flex; align-items: center; justify-content: center; font-size: 1.1rem; border: 1px solid var(--border-heavy); font-weight: 700; color: var(--text-main);'>AS</div>
<div class='card-title' style='font-size:1.1rem;'>Agha Salaat</div>
<div class='card-desc' style='font-size:0.85rem;'>Systems Engineering</div>
</div>
<div class='lp-card' style='text-align: center; padding: 3rem 2rem;'>
<div style='width: 56px; height: 56px; border-radius: 50%; background: var(--border-mid); margin: 0 auto 1.2rem auto; display: flex; align-items: center; justify-content: center; font-size: 1.1rem; border: 1px solid var(--border-heavy); font-weight: 700; color: var(--text-main);'>AM</div>
<div class='card-title' style='font-size:1.1rem;'>Anzar Mubashir</div>
<div class='card-desc' style='font-size:0.85rem;'>Backend Infrastructure</div>
</div>
</div>
</section>

<section id='contact' class='lp-section' style='text-align: center;'>
<div class='card-icon' style='margin: 0 auto 1.5rem auto; width: 64px; height: 64px; font-size: 1.5rem;'>💬</div>
<div class='lp-header'>Operational Support</div>
<div class='lp-sub'>We value user feedback and continuously improve operational reliability. For issue reporting, technical assistance, or feature requests, contact our engineering team.</div>
<a href='mailto:u2024585@giki.edu.pk' style='display: inline-block; background: var(--btn-bg); color: var(--btn-text) !important; padding: 0.9rem 2.5rem; border-radius: 8px; font-weight: 700; text-decoration: none !important; font-size: 0.95rem; transition: all 0.3s; box-shadow: 0 10px 25px var(--border-heavy);'>u2024585@giki.edu.pk</a>
<div style='margin-top: 1.5rem; color: var(--text-muted); font-size: 0.85rem; font-weight: 600;'>Expected Response SLA: Under 24 Hours</div>
</section>

<footer class='lp-footer'>
<div class='footer-text'>
<strong style='color:var(--text-main); font-size: 1rem;'>📦 LogiTrack PK</strong><br><br>
© 2026 LogiTrack Systems. All rights reserved.
</div>
<div class='footer-text' style='text-align: right;'>
Version 2.4.0 (Enterprise Build)<br><br>
<span style='opacity: 0.7;'>Protected by Zero Trust Security Architecture.</span>
</div>
</footer>
""", unsafe_allow_html=True)


# ─── 3. ENTERPRISE APP SHELL (AUTHENTICATED) ──────────────────────────────────
if not st.session_state.user:
    login_screen()
else:
    # SAFETY SCRIPT: Force removing light-theme class to protect Dashboard Dark Mode UI
    st.markdown("<img src='dummy' style='display:none;' onerror=\"document.body.classList.remove('light-theme');\">", unsafe_allow_html=True)
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