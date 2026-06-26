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

# ─── 1. PAGE CONFIGURATION & STATE INIT ───────────────────────────────────────
st.set_page_config(
    page_title="LogiTrack PK | Enterprise Logistics",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="collapsed",
)

if 'user' not in st.session_state:
    st.session_state.user = None
if 'theme' not in st.session_state:
    st.session_state.theme = 'dark'

def toggle_theme():
    st.session_state.theme = 'light' if st.session_state.theme == 'dark' else 'dark'


# ─── LANDING PAGE ASSET CACHING ───────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def get_cached_login_css(theme: str) -> str:
    if theme == 'light':
        css_vars = "--bg-main: #f8fafc; --text-main: #0f172a; --text-sub: #475569; --text-muted: #64748b; --border-light: rgba(0,0,0,0.05); --border-mid: rgba(0,0,0,0.1); --border-heavy: rgba(0,0,0,0.2); --nav-bg: rgba(248, 250, 252, 0.9); --card-bg: #ffffff; --card-hover: #f1f5f9; --btn-bg: #0f172a; --btn-text: #ffffff; --footer-bg: #f1f5f9; --title-grad: linear-gradient(135deg, #0f172a 0%, #475569 100%);"
    else:
        css_vars = "--bg-main: #030712; --text-main: #f8fafc; --text-sub: #94a3b8; --text-muted: #64748b; --border-light: rgba(255,255,255,0.03); --border-mid: rgba(255,255,255,0.05); --border-heavy: rgba(255,255,255,0.1); --nav-bg: rgba(3, 7, 18, 0.85); --card-bg: rgba(255,255,255,0.015); --card-hover: rgba(255,255,255,0.03); --btn-bg: #f8fafc; --btn-text: #030712; --footer-bg: #010206; --title-grad: linear-gradient(135deg, #f8fafc 0%, #94a3b8 100%);"
    
    return f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    :root {{ {css_vars} }}
    html, body, .stApp {{ background-color: var(--bg-main) !important; color: var(--text-main) !important; font-family: 'Plus Jakarta Sans', sans-serif; overflow-x: hidden; scroll-behavior: smooth; transition: background-color 0.3s ease, color 0.3s ease; }}
    .stApp {{ background-image: radial-gradient(circle at 15% 50%, rgba(16, 185, 129, 0.04), transparent 45%), linear-gradient(var(--border-light) 1px, transparent 1px), linear-gradient(90deg, var(--border-light) 1px, transparent 1px) !important; background-size: 100% 100%, 80px 80px, 80px 80px !important; background-position: center center !important; background-attachment: fixed !important; }}
    [data-testid="stSidebar"], [data-testid="collapsedControl"], #MainMenu, footer, header[data-testid="stHeader"] {{ display: none !important; }}
    .block-container {{ padding-top: 140px !important; padding-bottom: 0 !important; max-width: 1350px !important; }}
    .enterprise-navbar {{ position: fixed !important; top: 0 !important; left: 0 !important; width: 100vw !important; height: 75px !important; background: var(--nav-bg) !important; backdrop-filter: blur(20px) !important; -webkit-backdrop-filter: blur(20px) !important; border-bottom: 1px solid var(--border-heavy) !important; z-index: 999999 !important; display: flex !important; align-items: center !important; justify-content: space-between !important; padding: 0 4rem !important; box-shadow: 0 4px 20px rgba(0,0,0,0.05) !important; transition: background 0.3s ease !important; }}
    .nav-left {{ flex: 1; display: flex; align-items: center; gap: 0.75rem; text-decoration: none !important; cursor: pointer; }}
    .nav-center {{ display: flex; justify-content: center; align-items: center; gap: 3rem; }}
    .nav-right {{ flex: 1; display: flex; justify-content: flex-end; align-items: center; gap: 1.25rem; }}
    .nav-logo {{ font-size: 1.3rem; font-weight: 800; color: var(--text-main); display: flex; align-items: center; gap: 0.5rem; letter-spacing: -0.5px; transition: color 0.2s; }}
    .nav-left:hover .nav-logo {{ color: #10b981; }}
    .nav-divider {{ width: 1px; height: 24px; background: var(--border-heavy); margin: 0 0.25rem; }}
    .nav-subtitle {{ font-size: 0.8rem; font-weight: 600; color: var(--text-sub); text-transform: uppercase; letter-spacing: 1.5px; white-space: nowrap; margin-top: 2px; }}
    .nav-link {{ color: var(--text-sub) !important; text-decoration: none !important; font-size: 0.95rem; font-weight: 600; transition: color 0.3s ease; position: relative; padding: 0.5rem 0; }}
    .nav-link:hover {{ color: var(--text-main) !important; }}
    .nav-link::after {{ content: ''; position: absolute; left: 50%; bottom: 0; width: 0%; height: 2px; background-color: #10b981; transition: all 0.3s ease; transform: translateX(-50%); border-radius: 2px; }}
    .nav-link:hover::after {{ width: 100%; }}
    .theme-toggle-btn {{ cursor: pointer; font-size: 1.25rem; display: flex; align-items: center; justify-content: center; width: 44px; height: 44px; border-radius: 50%; color: var(--text-main); transition: all 0.2s ease; user-select: none; border: 1px solid transparent; }}
    .theme-toggle-btn:hover {{ background: var(--card-bg); border-color: var(--border-heavy); transform: rotate(15deg); }}
    .nav-cta {{ display: inline-flex; align-items: center; justify-content: center; background: var(--btn-bg); color: var(--btn-text) !important; text-decoration: none !important; padding: 0 1.75rem; height: 44px; border-radius: 8px; font-size: 0.9rem; font-weight: 700; transition: all 0.2s ease; white-space: nowrap; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
    .nav-cta:hover {{ transform: translateY(-2px); box-shadow: 0 8px 15px rgba(0,0,0,0.15); }}
    [data-testid="stVerticalBlock"] > [data-testid="stHorizontalBlock"]:nth-of-type(1) {{ align-items: center; padding-bottom: 4rem; border-bottom: 1px solid var(--border-light); }}
    [data-testid="stVerticalBlock"] > [data-testid="stHorizontalBlock"]:nth-of-type(1) > [data-testid="column"]:nth-of-type(1) {{ padding-right: 4rem !important; }}
    .hero-super {{ color: #10b981; font-size: 0.9rem; font-weight: 700; letter-spacing: 2px; text-transform: uppercase; margin-bottom: 1.5rem; display: block; }}
    .hero-title {{ font-size: 3.4rem; font-weight: 800; letter-spacing: -1px; line-height: 1.25; margin-bottom: 2rem; background: var(--title-grad); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
    .hero-desc {{ font-size: 1.1rem; color: var(--text-sub); line-height: 1.7; max-width: 95%; font-weight: 400; margin-bottom: 3.5rem; }}
    .corridor-map {{ position: relative; height: 50px; display: flex; align-items: center; margin-top: 2rem; width: 90%; opacity: 0.9; }}
    .corridor-line {{ position: absolute; width: 100%; height: 2px; background: var(--border-heavy); top: 50%; transform: translateY(-50%); }}
    .corridor-flow {{ position: absolute; width: 30%; height: 2px; background: linear-gradient(90deg, transparent, #10b981, transparent); top: 50%; transform: translateY(-50%); animation: freightFlow 3s infinite linear; }}
    .corridor-node {{ position: absolute; display: flex; flex-direction: column; align-items: center; gap: 8px; top: 50%; transform: translate(-50%, -12px); }}
    .node-dot {{ width: 12px; height: 12px; background: var(--bg-main); border: 2px solid #3b82f6; border-radius: 50%; z-index: 2; transition: all 0.3s; }}
    .corridor-node:hover .node-dot {{ background: #10b981; border-color: #10b981; box-shadow: 0 0 15px rgba(16,185,129,0.5); transform: scale(1.3); }}
    .node-label {{ font-size: 0.7rem; font-weight: 700; color: var(--text-muted); letter-spacing: 1px; transition: color 0.3s; }}
    .corridor-node:hover .node-label {{ color: var(--text-main); }}
    @keyframes freightFlow {{ 0% {{ left: -30%; }} 100% {{ left: 100%; }} }}
    [data-testid="stForm"] {{ background: var(--card-bg) !important; backdrop-filter: blur(20px) !important; -webkit-backdrop-filter: blur(20px) !important; border: 1px solid var(--border-heavy) !important; border-radius: 12px !important; padding: 3rem 2.5rem !important; box-shadow: 0 15px 35px -10px rgba(0,0,0,0.2) !important; position: relative !important; overflow: hidden !important; }}
    [data-testid="stForm"]::before {{ content: ''; position: absolute; top: 0; left: 0; width: 100%; height: 4px; background: linear-gradient(90deg, #10b981, #3b82f6); }}
    .auth-heading {{ font-size: 1.4rem; font-weight: 700; letter-spacing: -0.5px; margin-bottom: 0.5rem; color: var(--text-main); }}
    .auth-sub {{ color: var(--text-sub); font-size: 0.95rem; margin-bottom: 2rem; font-weight: 400; line-height: 1.5; }}
    .stTextInput label {{ color: var(--text-sub) !important; font-size: 0.75rem !important; font-weight: 700 !important; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 0.5rem !important; }}
    .stTextInput input {{ border-radius: 6px !important; border: 1px solid var(--border-heavy) !important; background: var(--bg-main) !important; color: var(--text-main) !important; padding: 0.75rem 1rem !important; font-size: 0.95rem !important; transition: all 0.2s; }}
    .stTextInput input:focus {{ border-color: #10b981 !important; box-shadow: 0 0 0 3px rgba(16,185,129,0.15) !important; }}
    [data-testid="stFormSubmitButton"] > button {{ border-radius: 6px !important; background: var(--btn-bg) !important; border: none !important; padding: 0.75rem !important; margin-top: 1.5rem !important; transition: all 0.2s ease !important; box-shadow: 0 4px 6px rgba(0,0,0,0.1) !important; }}
    [data-testid="stFormSubmitButton"] > button:hover {{ transform: translateY(-1px) !important; box-shadow: 0 8px 15px rgba(0,0,0,0.15) !important; }}
    [data-testid="stFormSubmitButton"] > button *, [data-testid="stFormSubmitButton"] > button p {{ color: var(--btn-text) !important; font-weight: 700 !important; font-size: 0.95rem !important; }}
    .lp-section {{ padding: 6rem 8%; border-bottom: 1px solid var(--border-light); scroll-margin-top: 90px; }}
    .lp-header {{ font-size: 2.2rem; font-weight: 700; letter-spacing: -0.5px; margin-bottom: 1rem; color: var(--text-main); text-align: center; }}
    .lp-sub {{ font-size: 1.1rem; color: var(--text-sub); text-align: center; max-width: 750px; margin: 0 auto 3.5rem auto; line-height: 1.6; font-weight: 400; }}
    .grid-2 {{ display: grid; grid-template-columns: 1fr 1fr; gap: 4rem; align-items: center; }}
    .grid-3 {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 2.5rem; }}
    .grid-4 {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 2rem; }}
    .lp-card {{ background: var(--card-bg); border: 1px solid var(--border-mid); border-radius: 12px; padding: 2.5rem 2rem; transition: all 0.3s ease; }}
    .lp-card:hover {{ background: var(--card-hover); transform: translateY(-4px); box-shadow: 0 15px 30px -10px rgba(0,0,0,0.15); border-color: var(--border-heavy); }}
    .card-icon {{ width: 52px; height: 52px; border-radius: 10px; background: var(--border-mid); display: flex; align-items: center; justify-content: center; font-size: 1.6rem; margin-bottom: 1.5rem; border: 1px solid var(--border-heavy); }}
    .card-title {{ font-size: 1.15rem; font-weight: 700; color: var(--text-main); margin-bottom: 0.75rem; letter-spacing: -0.5px; }}
    .card-desc {{ font-size: 0.95rem; color: var(--text-sub); line-height: 1.6; }}
    .tag-wrap {{ display: flex; flex-wrap: wrap; gap: 0.75rem; }}
    .lp-tag {{ padding: 0.5rem 1rem; border-radius: 100px; background: var(--card-bg); border: 1px solid var(--border-heavy); font-size: 0.85rem; color: var(--text-sub); font-weight: 600; transition: all 0.2s; cursor: default; }}
    .lp-tag:hover {{ background: rgba(16,185,129,0.05); border-color: rgba(16,185,129,0.3); color: #10b981; box-shadow: 0 4px 12px rgba(16,185,129,0.1); }}
    .lp-footer {{ background: var(--footer-bg); padding: 4rem 8%; display: flex; justify-content: space-between; align-items: center; }}
    .footer-text {{ color: var(--text-muted); font-size: 0.9rem; line-height: 1.5; }}
    @media (max-width: 1024px) {{ .nav-center {{ display: none; }} .enterprise-navbar {{ padding: 0 2rem !important; }} }}
    </style>
    """

@st.cache_data(show_spinner=False)
def get_cached_navbar_html(theme: str) -> str:
    toggle_icon = "🌞" if theme == 'light' else "🌓"
    html = """<div id="top-anchor" style="position: absolute; top: 0; left: 0; width: 1px; height: 1px;"></div><nav class="enterprise-navbar"><a href="#top-anchor" class="nav-left" onclick="window.scrollTo({top:0, behavior:'smooth'});"><div class="nav-logo">📦 LogiTrack PK</div><div class="nav-divider"></div><span class="nav-subtitle">Freight OS</span></a><div class="nav-center"><a href="#network" class="nav-link">Operations</a><a href="#ecosystem" class="nav-link">Freight Network</a><a href="#capabilities" class="nav-link">Platform Modules</a><a href="#team" class="nav-link">Engineering</a></div><div class="nav-right"><div class="theme-toggle-btn" onclick="window.toggleTheme && window.toggleTheme();" title="Toggle Theme">TOGGLE_ICON_PLACEHOLDER</div><a href="#auth-portal" class="nav-cta">System Access</a></div></nav><img src="data:image/gif;base64,R0lGODlhAQABAIAAAP///wAAACH5BAEAAAAALAAAAAABAAEAAAICRAEAOw==" style="display:none;" onload="if(!window.navScriptLoaded){window.navScriptLoaded=true;setInterval(function(){var b=window.parent.document.querySelectorAll('button');for(var i=0;i<b.length;i++){if(b[i].innerText.includes('Toggle Mode')){var c=b[i].closest('div[data-testid=\\'stButton\\']');if(c)c.style.display='none';}}},50);window.toggleTheme=function(){var bs=window.parent.document.querySelectorAll('button');for(var j=0;j<bs.length;j++){if(bs[j].innerText.includes('Toggle Mode')){bs[j].click();break;}}};}">"""
    return html.replace('TOGGLE_ICON_PLACEHOLDER', toggle_icon)

@st.cache_data(show_spinner=False)
def get_cached_hero_brand_html() -> str:
    return "<span class='hero-super'>Enterprise Logistics OS</span><div class='hero-title'>Logistics visibility,<br>engineered for scale.</div><div class='hero-desc'>The centralized operating system for Pakistan's freight network. Command your fleet, track shipments, and coordinate dispatch operations with unprecedented clarity.</div><div class='corridor-map'><div class='corridor-line'></div><div class='corridor-flow'></div><div class='corridor-node' style='left: 0%;'><div class='node-dot'></div><span class='node-label'>KHI</span></div><div class='corridor-node' style='left: 33%;'><div class='node-dot'></div><span class='node-label'>LHE</span></div><div class='corridor-node' style='left: 66%;'><div class='node-dot'></div><span class='node-label'>ISB</span></div><div class='corridor-node' style='left: 100%;'><div class='node-dot'></div><span class='node-label'>PEW</span></div></div>"

@st.cache_data(show_spinner=False)
def get_cached_marketing_sections_html() -> str:
    return """
    <section id='network' class='lp-section'>
        <div class='lp-header'>Centralized Operations</div>
        <div class='lp-sub'>LogiTrack PK replaces fragmented workflows with a single source of truth. Command your fleet, coordinate dispatch operations, and track deliveries with unparalleled operational visibility.</div>
        <div class='grid-3'>
            <div class='lp-card'><div class='card-icon'>👁️</div><div class='card-title'>Shipment Telematics</div><div class='card-desc'>Monitor the exact status of every contract in your network from origin loading dock to destination sign-off.</div></div>
            <div class='lp-card'><div class='card-icon'>🚚</div><div class='card-title'>Carrier Ledgers</div><div class='card-desc'>Maintain a live, centralized registry of your fleet's capacity, availability, and active deployment status.</div></div>
            <div class='lp-card'><div class='card-icon'>⚡</div><div class='card-title'>Dispatch Protocols</div><div class='card-desc'>Seamlessly assign pending orders to available carriers using intelligent, zero-friction workflows.</div></div>
        </div>
    </section>
    <section id='ecosystem' class='lp-section' style='background: var(--card-bg);'>
        <div class='grid-2'>
            <div>
                <div class='lp-header' style='text-align: left;'>Architected for <span style="color:#10b981; font-weight:800; text-shadow: 0 0 20px rgba(16,185,129,0.2);">Pakistan's</span> Ecosystem</div>
                <div class='lp-sub' style='text-align: left; margin-bottom: 2rem;'>Designed exclusively for the operational realities of the domestic supply chain. We serve the critical transport corridors connecting <b>Karachi, Lahore, Islamabad, Faisalabad, Multan, Peshawar, and Quetta.</b></div>
                <div class='tag-wrap'>
                    <span class='lp-tag'>Freight Forwarders</span><span class='lp-tag'>3PL Providers</span><span class='lp-tag'>Fleet Operators</span>
                    <span class='lp-tag'>Warehouse Managers</span><span class='lp-tag'>Dispatch Coordinators</span><span class='lp-tag'>Intercity Networks</span>
                </div>
            </div>
            <div style='background: rgba(16,185,129,0.03); border: 1px solid rgba(16,185,129,0.1); border-radius: 16px; padding: 3rem; display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%; position: relative; overflow: hidden;'>
                <div style='width: 120px; height: 120px; border-radius: 50%; border: 1px solid rgba(16,185,129,0.3); display: flex; align-items: center; justify-content: center; position: relative;'>
                    <div style='width: 70px; height: 70px; border-radius: 50%; background: rgba(16,185,129,0.1); display: flex; align-items: center; justify-content: center;'>
                        <div style='width: 24px; height: 24px; border-radius: 50%; background: #10b981; box-shadow: 0 0 20px #10b981;'></div>
                    </div>
                    <div style='position: absolute; width: 100%; height: 100%; border-radius: 50%; border: 2px solid #10b981; border-top-color: transparent; animation: spin 4s linear infinite;'></div>
                </div>
                <div style='color: #10b981; font-weight: 700; font-size: 0.9rem; letter-spacing: 4px; text-transform: uppercase; margin-top: 1.5rem;'>Central Hub Active</div>
                <style>@keyframes spin { 100% { transform: rotate(360deg); } }</style>
            </div>
        </div>
    </section>
    <section id='capabilities' class='lp-section'>
        <div class='lp-header'>Platform Modules</div>
        <div class='lp-sub'>Enterprise-grade architecture ensuring high-availability, cryptographic security, and analytical depth.</div>
        <div class='grid-4'>
            <div class='lp-card' style='padding: 2rem 1.5rem;'><div class='card-title' style='color:#10b981;'>Real-Time Tracking</div><div class='card-desc'>Live status updates for all active freight.</div></div>
            <div class='lp-card' style='padding: 2rem 1.5rem;'><div class='card-title' style='color:#3b82f6;'>Audit Logging</div><div class='card-desc'>Immutable, cryptographic history of all actions.</div></div>
            <div class='lp-card' style='padding: 2rem 1.5rem;'><div class='card-title' style='color:#f59e0b;'>Zero Trust RBAC</div><div class='card-desc'>Strict role-based access to operational modules.</div></div>
            <div class='lp-card' style='padding: 2rem 1.5rem;'><div class='card-title' style='color:#8b5cf6;'>BI Analytics</div><div class='card-desc'>Live Plotly data grids and network intelligence.</div></div>
        </div>
    </section>
    <section id='team' class='lp-section' style='background: var(--card-bg);'>
        <div class='lp-header'>Platform Engineering</div>
        <div class='lp-sub'>Designed, architected, and developed by software engineers committed to modernizing industrial logistics infrastructure.</div>
        <div class='grid-3'>
            <div class='lp-card' style='text-align: center; padding: 3rem 2rem;'>
                <div style='width: 64px; height: 64px; border-radius: 50%; background: var(--border-mid); margin: 0 auto 1.5rem auto; display: flex; align-items: center; justify-content: center; font-size: 1.2rem; border: 1px solid var(--border-heavy); font-weight: 700; color: var(--text-main);'>SR</div>
                <div class='card-title'>Shayan Rizwan</div><div class='card-desc'>Platform Architecture</div>
            </div>
            <div class='lp-card' style='text-align: center; padding: 3rem 2rem;'>
                <div style='width: 64px; height: 64px; border-radius: 50%; background: var(--border-mid); margin: 0 auto 1.5rem auto; display: flex; align-items: center; justify-content: center; font-size: 1.2rem; border: 1px solid var(--border-heavy); font-weight: 700; color: var(--text-main);'>AS</div>
                <div class='card-title'>Agha Salaat</div><div class='card-desc'>Systems Engineering</div>
            </div>
            <div class='lp-card' style='text-align: center; padding: 3rem 2rem;'>
                <div style='width: 64px; height: 64px; border-radius: 50%; background: var(--border-mid); margin: 0 auto 1.5rem auto; display: flex; align-items: center; justify-content: center; font-size: 1.2rem; border: 1px solid var(--border-heavy); font-weight: 700; color: var(--text-main);'>AM</div>
                <div class='card-title'>Anzar Mubashir</div><div class='card-desc'>Backend Infrastructure</div>
            </div>
        </div>
    </section>
    <section id='contact' class='lp-section' style='text-align: center;'>
        <div class='card-icon' style='margin: 0 auto 1.5rem auto; width: 64px; height: 64px; font-size: 1.5rem;'>💬</div>
        <div class='lp-header'>Operational Support</div>
        <div class='lp-sub'>We value user feedback and continuously improve operational reliability. For issue reporting, technical assistance, or feature requests, contact our engineering team.</div>
        <a href='mailto:u2024585@giki.edu.pk' style='display: inline-block; background: var(--btn-bg); color: var(--btn-text) !important; padding: 0.85rem 2.5rem; border-radius: 6px; font-weight: 700; text-decoration: none !important; font-size: 0.95rem; transition: all 0.2s; box-shadow: 0 4px 15px rgba(0,0,0,0.1);'>u2024585@giki.edu.pk</a>
        <div style='margin-top: 1.5rem; color: var(--text-muted); font-size: 0.85rem; font-weight: 600;'>Expected Response SLA: Under 24 Hours</div>
    </section>
    <footer class='lp-footer'>
        <div class='footer-text'><strong style='color:var(--text-main); font-size: 1.05rem;'>📦 LogiTrack PK</strong><br><br>© 2026 LogiTrack Systems. All rights reserved.</div>
        <div class='footer-text' style='text-align: right;'>Version 2.4.0 (Enterprise Build)<br><br><span style='opacity: 0.7;'>Protected by Zero Trust Security Architecture.</span></div>
    </footer>
    """

# ─── ENTERPRISE SHELL CSS CACHING ─────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def get_cached_shell_css(theme: str) -> str:
    # Use strict variable mapping to guarantee contrast in the enterprise shell
    if theme == 'light':
        shell_vars = "--bg-main: #f8fafc; --card-bg: #ffffff; --text-main: #0f172a; --text-muted: #64748b; --border-color: rgba(0,0,0,0.08);"
    else:
        shell_vars = "--bg-main: #030712; --card-bg: #0f172a; --text-main: #f8fafc; --text-muted: #94a3b8; --border-color: rgba(255,255,255,0.08);"
        
    return f"""
    <style>
        :root {{ {shell_vars} }}
        html, body, .stApp {{ background-color: var(--bg-main) !important; }}
        [data-testid="stSidebar"], [data-testid="collapsedControl"], header[data-testid="stHeader"] {{ display: none !important; }}
        
        /* Rigid constraints for the workspace to prevent ultrawide stretching */
        .block-container {{ padding: 90px 2rem 2rem 2rem !important; max-width: 1440px !important; margin: 0 auto; }}
        
        /* ── ENTERPRISE COMMAND BAR (Native Top Header) ── */
        .command-bar-wrapper {{
            position: fixed; top: 0; left: 0; width: 100vw; height: 64px;
            background: var(--bg-main); border-bottom: 1px solid var(--border-color);
            z-index: 9999; display: flex; align-items: center; justify-content: space-between;
            padding: 0 2rem; box-shadow: 0 2px 10px rgba(0,0,0,0.02);
        }}
        .cmd-left {{ display: flex; align-items: center; gap: 0.75rem; }}
        .cmd-logo {{ font-size: 1.15rem; font-weight: 800; color: var(--text-main); letter-spacing: -0.5px; }}
        .cmd-sub {{ font-size: 0.75rem; font-weight: 600; color: var(--text-muted); text-transform: uppercase; letter-spacing: 1px; padding-left: 0.75rem; border-left: 1px solid var(--border-color); }}
        .cmd-center {{ font-size: 0.9rem; font-weight: 600; color: var(--text-main); background: var(--card-bg); padding: 0.4rem 1rem; border-radius: 6px; border: 1px solid var(--border-color); }}
        .cmd-right {{ display: flex; align-items: center; gap: 1rem; }}
        
        /* ── NAVIGATION RAIL (Sidebar Refinement) ── */
        .nav-profile-card {{
            background: var(--card-bg); border: 1px solid var(--border-color); border-radius: 8px;
            padding: 1rem; margin-bottom: 1.5rem; display: flex; align-items: center; gap: 0.75rem;
        }}
        .profile-initials {{ width: 36px; height: 36px; border-radius: 6px; display: flex; align-items: center; justify-content: center; font-size: 0.8rem; font-weight: 800; }}
        .profile-meta {{ display: flex; flex-direction: column; }}
        .profile-name {{ font-size: 0.85rem; font-weight: 700; color: var(--text-main); }}
        .profile-status {{ font-size: 0.65rem; color: #10b981; font-weight: 600; display: flex; align-items: center; gap: 4px; margin-top: 2px; }}
        .status-dot {{ width: 6px; height: 6px; background: #10b981; border-radius: 50%; box-shadow: 0 0 5px #10b981; }}
        
        /* Streamlit Button Overrides */
        .stButton > button[kind="primary"] {{ border-radius: 6px !important; background: linear-gradient(135deg, #059669, #10b981) !important; color: white !important; border: none !important; font-weight: 700 !important; transition: all 0.15s !important; height: 36px; }}
        .stButton > button[kind="primary"]:hover {{ transform: translateY(-1px) !important; box-shadow: 0 4px 12px rgba(16,185,129,0.3) !important; }}
        .stButton > button:not([kind="primary"]) {{ border-radius: 6px !important; border: 1px solid var(--border-color) !important; color: var(--text-muted) !important; background: var(--card-bg) !important; font-weight: 600 !important; transition: all 0.15s !important; height: 36px; font-size: 0.85rem !important; }}
        .stButton > button:not([kind="primary"]):hover {{ border-color: #10b981 !important; color: #10b981 !important; background: rgba(16,185,129,0.05) !important; }}
    </style>
    """

# ─── 2. ENTERPRISE SAAS LANDING & AUTH PORTAL ─────────────────────────────────
def login_screen():
    st.markdown(get_cached_login_css(st.session_state.theme), unsafe_allow_html=True)
    st.markdown(get_cached_navbar_html(st.session_state.theme), unsafe_allow_html=True)
    st.markdown("<div id='auth-portal' style='position:absolute; top:-40px;'></div>", unsafe_allow_html=True)
    st.button("Toggle Mode", on_click=toggle_theme)

    col_brand, col_auth = st.columns([1.2, 1], gap="large")
    with col_brand:
        st.markdown(get_cached_hero_brand_html(), unsafe_allow_html=True)
    with col_auth:
        st.markdown("<div class='auth-heading'>Authentication</div>", unsafe_allow_html=True)
        st.markdown("<div class='auth-sub'>Secure terminal for authorized personnel.</div>", unsafe_allow_html=True)
        with st.form("login_form"):
            email    = st.text_input("Email", placeholder="admin@logitrack.pk")
            password = st.text_input("Password", type="password", placeholder="••••••••")
            submit   = st.form_submit_button("System Access", use_container_width=True)

        if submit:
            conn = get_db()
            cur  = conn.cursor()
            cur.execute("SELECT * FROM users WHERE email=%s AND is_active=TRUE", (email,))
            user = cur.fetchone()
            conn.close()
            if user and verify_password(password, user['password_hash']):
                st.session_state.user = {'user_id': user['user_id'], 'full_name': user['full_name'], 'role': user['role']}
                st.session_state.theme = 'dark' # Default enterprise shell to dark mode
                st.rerun()
            else:
                st.error("Authentication failed. Invalid credentials.")

    st.markdown(get_cached_marketing_sections_html(), unsafe_allow_html=True)

# ─── 3. ENTERPRISE APP SHELL (AUTHENTICATED) ──────────────────────────────────
if not st.session_state.user:
    login_screen()
else:
    # Inject Shell CSS
    st.markdown(get_cached_shell_css(st.session_state.theme), unsafe_allow_html=True)
    apply_enterprise_theme()

    user_role = st.session_state.user['role']
    initials = "".join([n[0].upper() for n in st.session_state.user['full_name'].split()[:2]])

    # ── Enterprise Command Bar (Fixed Header) ──
    # Rendered using purely native Streamlit columns enclosed in a raw HTML wrapper
    # The header utilizes st.columns to allow native interaction with Logout and Theme buttons
    st.markdown("""
        <div class="command-bar-wrapper">
            <div class="cmd-left">
                <span class="cmd-logo">📦 LogiTrack PK</span>
                <span class="cmd-sub">Pakistan Freight Operations Platform</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # We position the native Streamlit buttons physically over the CSS command bar using negative margins
    header_cols = st.columns([7, 1, 1, 1])
    with header_cols[1]:
        st.markdown("<div style='margin-top: -60px; z-index: 10000; position: relative;'>", unsafe_allow_html=True)
        toggle_icon = "🌞" if st.session_state.theme == 'light' else "🌓"
        st.button(toggle_icon, key="shell_theme", on_click=toggle_theme, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    with header_cols[2]:
        st.markdown(f"<div style='margin-top: -60px; z-index: 10000; position: relative; height: 36px; display: flex; align-items: center; justify-content: center; background: rgba(16,185,129,0.1); border: 1px solid rgba(16,185,129,0.2); border-radius: 6px; color: #10b981; font-weight: 700; font-size: 0.85rem;'>{initials}</div>", unsafe_allow_html=True)
    with header_cols[3]:
        st.markdown("<div style='margin-top: -60px; z-index: 10000; position: relative;'>", unsafe_allow_html=True)
        if st.button("Logout", key="shell_logout", use_container_width=True):
            st.session_state.user = None
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)


    # ── Workspace Layout ──
    nav_col, workspace_col = st.columns([2, 8], gap="large")

    # ─ Navigation Rail ─
    with nav_col:
        # Determine specific colors for user roles to add contextual polish
        role_colors = {
            "System Administrator": ("#10b981", "rgba(16,185,129,0.1)", "rgba(16,185,129,0.2)"),
            "Dispatcher":           ("#3b82f6", "rgba(59,130,246,0.1)", "rgba(59,130,246,0.2)"),
            "Warehouse Manager":    ("#f59e0b", "rgba(245,158,11,0.1)", "rgba(245,158,11,0.2)"),
        }
        accent, bg_c, border_c = role_colors.get(user_role, ("#64748b", "rgba(255,255,255,0.05)", "rgba(255,255,255,0.1)"))

        # Compact User Profile Section
        st.markdown(f"""
            <div class='nav-profile-card'>
                <div class='profile-initials' style='background:{bg_c}; color:{accent}; border: 1px solid {border_c};'>
                    {initials}
                </div>
                <div class='profile-meta'>
                    <span class='profile-name'>{st.session_state.user['full_name']}</span>
                    <span class='profile-status'><div class='status-dot'></div> Active Session</span>
                </div>
            </div>
        """, unsafe_allow_html=True)

        # Logic for menu items based on role
        nav_options = ["Dashboard", "Shipments"]
        nav_icons   = ["grid-1x2", "box-seam"]
        
        if user_role in ["System Administrator", "Dispatcher"]:
            nav_options.append("Fleet")
            nav_icons.append("truck")
            
        nav_options.append("Reports")
        nav_icons.append("bar-chart")
        
        if user_role == "System Administrator":
            nav_options.append("Audit Logs")
            nav_icons.append("shield-lock")

        # Refined Option Menu featuring Left Accent Indicator
        selected_module = option_menu(
            menu_title="OPERATIONAL MODULES", 
            options=nav_options, 
            icons=nav_icons, 
            default_index=0,
            styles={
                "container": {"padding": "0", "background-color": "transparent"},
                "icon": {"color": "var(--text-muted)", "font-size": "1.05rem"},
                "nav-link": {
                    "font-size": "0.85rem", "text-align": "left", "margin": "0.25rem 0",
                    "color": "var(--text-muted)", "font-weight": "600", "border-radius": "6px",
                    "padding": "0.6rem 1rem", "transition": "all 0.2s ease"
                },
                "nav-link-selected": {
                    "background-color": "var(--card-bg)", "color": "var(--text-main)",
                    "font-weight": "700", "border-left": "4px solid #10b981",
                    "border-radius": "4px" # Sharper radius when selected to emphasize the left border
                },
                "menu-title": {
                    "color": "var(--text-muted)", "font-size": "0.65rem", "letter-spacing": "1.5px",
                    "padding-left": "1rem", "font-weight": "700", "padding-bottom": "0.5rem"
                },
            },
        )

    # ─ Right Workspace Injection ─
    # The selected module string is dynamically passed to the dashboard files to act as context
    with workspace_col:
        # Pass the selected_module down to act as a breadcrumb
        if selected_module == "Dashboard": 
            dashboard.render_page(module_name=selected_module)
        elif selected_module == "Shipments": 
            shipments.render_page()
        elif selected_module == "Fleet": 
            fleet.render_page()
        elif selected_module == "Reports": 
            reports.render_page()
        elif selected_module == "Audit Logs": 
            audit_logs.render_page()