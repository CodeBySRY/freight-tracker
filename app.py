import streamlit as st
import time
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

# ─── CALLBACKS (NATIVE STREAMLIT STATE MANAGEMENT) ────────────────────────────
def toggle_theme():
    st.session_state.theme = 'light' if st.session_state.theme == 'dark' else 'dark'


# ─── ASSET CACHING (MASSIVE BACKEND PERFORMANCE OPTIMIZATION) ─────────────────
@st.cache_data(show_spinner=False)
def get_cached_login_css(theme: str) -> str:
    # Define color palettes based on active theme
    if theme == 'light':
        css_vars = """
        --bg-main: #f8fafc; --text-main: #0f172a; --text-sub: #475569; --text-muted: #64748b;
        --border-light: rgba(0,0,0,0.05); --border-mid: rgba(0,0,0,0.1); --border-heavy: rgba(0,0,0,0.2);
        --nav-bg: rgba(248, 250, 252, 0.9); --card-bg: #ffffff; --card-hover: #f1f5f9;
        --btn-bg: #0f172a; --btn-text: #ffffff; --footer-bg: #f1f5f9; --title-grad: linear-gradient(135deg, #0f172a 0%, #475569 100%);
        """
    else:
        css_vars = """
        --bg-main: #030712; --text-main: #f8fafc; --text-sub: #94a3b8; --text-muted: #64748b;
        --border-light: rgba(255,255,255,0.03); --border-mid: rgba(255,255,255,0.05); --border-heavy: rgba(255,255,255,0.1);
        --nav-bg: rgba(3, 7, 18, 0.85); --card-bg: rgba(255,255,255,0.015); --card-hover: rgba(255,255,255,0.03);
        --btn-bg: #f8fafc; --btn-text: #030712; --footer-bg: #010206; --title-grad: linear-gradient(135deg, #f8fafc 0%, #94a3b8 100%);
        """
    
    return f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    
    :root {{ {css_vars} }}
    
    /* ── BASE HTML/BODY OVERRIDES ── */
    html, body, .stApp {{ 
        background-color: var(--bg-main) !important; color: var(--text-main) !important; 
        font-family: 'Plus Jakarta Sans', sans-serif; overflow-x: hidden; scroll-behavior: smooth; 
        transition: background-color 0.3s ease, color 0.3s ease; 
    }}
    
    /* Engineering Grid Background */
    .stApp {{ 
        background-image: radial-gradient(circle at 15% 50%, rgba(16, 185, 129, 0.04), transparent 45%), 
                          linear-gradient(var(--border-light) 1px, transparent 1px), 
                          linear-gradient(90deg, var(--border-light) 1px, transparent 1px) !important; 
        background-size: 100% 100%, 80px 80px, 80px 80px !important; 
        background-position: center center !important; 
        background-attachment: fixed !important; 
    }}
    
    [data-testid="stSidebar"], [data-testid="collapsedControl"], #MainMenu, footer, header {{ display: none !important; }}
    
    /* Offset container to account for fixed full-width navbar */
    .block-container {{ padding-top: 140px !important; padding-bottom: 0 !important; max-width: 1350px !important; }}

    /* ── UNIFIED ENTERPRISE NAVBAR ── */
    .enterprise-navbar {{
        position: fixed; top: 0; left: 0; width: 100vw; height: 75px;
        background: var(--nav-bg); backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px);
        border-bottom: 1px solid var(--border-heavy); z-index: 999999;
        display: flex; align-items: center; justify-content: space-between;
        padding: 0 4rem; transition: background 0.3s ease;
    }}
    
    /* Navbar Flex Groups */
    .nav-left {{ flex: 1; display: flex; align-items: center; gap: 1rem; text-decoration: none; cursor: pointer; }}
    .nav-center {{ display: flex; justify-content: center; align-items: center; gap: 3rem; }}
    .nav-right {{ flex: 1; display: flex; justify-content: flex-end; align-items: center; gap: 1.5rem; }}

    /* Branding */
    .nav-logo {{ font-size: 1.3rem; font-weight: 800; color: var(--text-main); display: flex; align-items: center; gap: 0.5rem; letter-spacing: -0.5px; transition: color 0.2s; }}
    .nav-left:hover .nav-logo {{ color: #10b981; }}
    .nav-divider {{ width: 1px; height: 24px; background: var(--border-heavy); }}
    .nav-subtitle {{ font-size: 0.8rem; font-weight: 600; color: var(--text-sub); text-transform: uppercase; letter-spacing: 1px; white-space: nowrap; margin-top: 2px; }}

    /* Navigation Links */
    .nav-link {{ color: var(--text-sub); text-decoration: none; font-size: 0.95rem; font-weight: 600; transition: color 0.3s ease; position: relative; padding: 0.5rem 0; }}
    .nav-link:hover {{ color: var(--text-main); }}
    .nav-link::after {{ content: ''; position: absolute; left: 50%; bottom: 0; width: 0%; height: 2px; background-color: #10b981; transition: all 0.3s ease; transform: translateX(-50%); border-radius: 2px; }}
    .nav-link:hover::after {{ width: 100%; }}

    /* Controls (Toggle & CTA) */
    .theme-toggle-btn {{ cursor: pointer; font-size: 1.25rem; display: flex; align-items: center; justify-content: center; width: 44px; height: 44px; border-radius: 50%; color: var(--text-main); transition: all 0.2s ease; user-select: none; border: 1px solid transparent; }}
    .theme-toggle-btn:hover {{ background: var(--card-bg); border-color: var(--border-heavy); }}
    
    .nav-cta {{ display: inline-flex; align-items: center; justify-content: center; background: var(--btn-bg); color: var(--btn-text) !important; text-decoration: none; padding: 0 1.75rem; height: 44px; border-radius: 8px; font-size: 0.9rem; font-weight: 700; transition: all 0.2s ease; white-space: nowrap; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
    .nav-cta:hover {{ transform: translateY(-2px); box-shadow: 0 8px 15px rgba(0,0,0,0.15); }}

    /* ── HERO SECTION TYPOGRAPHY & LAYOUT ── */
    [data-testid="stVerticalBlock"] > [data-testid="stHorizontalBlock"]:nth-of-type(1) {{ align-items: center; padding-bottom: 4rem; border-bottom: 1px solid var(--border-light); }}
    [data-testid="stVerticalBlock"] > [data-testid="stHorizontalBlock"]:nth-of-type(1) > [data-testid="column"]:nth-of-type(1) {{ padding-right: 4rem !important; }}
    
    .hero-super {{ color: #10b981; font-size: 0.9rem; font-weight: 700; letter-spacing: 2px; text-transform: uppercase; margin-bottom: 1.5rem; display: block; }}
    .hero-title {{ font-size: 3.4rem; font-weight: 800; letter-spacing: -1px; line-height: 1.25; margin-bottom: 2rem; background: var(--title-grad); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
    .hero-desc {{ font-size: 1.1rem; color: var(--text-sub); line-height: 1.7; max-width: 95%; font-weight: 400; margin-bottom: 3.5rem; }}

    /* Corridor Visualization */
    .corridor-map {{ position: relative; height: 50px; display: flex; align-items: center; margin-top: 2rem; width: 90%; opacity: 0.9; }}
    .corridor-line {{ position: absolute; width: 100%; height: 2px; background: var(--border-heavy); top: 50%; transform: translateY(-50%); }}
    .corridor-flow {{ position: absolute; width: 30%; height: 2px; background: linear-gradient(90deg, transparent, #10b981, transparent); top: 50%; transform: translateY(-50%); animation: freightFlow 3s infinite linear; }}
    .corridor-node {{ position: absolute; display: flex; flex-direction: column; align-items: center; gap: 8px; top: 50%; transform: translate(-50%, -12px); }}
    .node-dot {{ width: 12px; height: 12px; background: var(--bg-main); border: 2px solid #3b82f6; border-radius: 50%; z-index: 2; transition: all 0.3s; }}
    .corridor-node:hover .node-dot {{ background: #10b981; border-color: #10b981; box-shadow: 0 0 15px rgba(16,185,129,0.5); transform: scale(1.3); }}
    .node-label {{ font-size: 0.7rem; font-weight: 700; color: var(--text-muted); letter-spacing: 1px; transition: color 0.3s; }}
    .corridor-node:hover .node-label {{ color: var(--text-main); }}
    @keyframes freightFlow {{ 0% {{ left: -30%; }} 100% {{ left: 100%; }} }}

    /* ── AUTHENTICATION PORTAL ── */
    [data-testid="stForm"] {{ background: var(--card-bg) !important; backdrop-filter: blur(20px) !important; -webkit-backdrop-filter: blur(20px) !important; border: 1px solid var(--border-heavy) !important; border-radius: 12px !important; padding: 3rem 2.5rem !important; box-shadow: 0 15px 35px -10px rgba(0,0,0,0.2) !important; position: relative !important; overflow: hidden !important; }}
    [data-testid="stForm"]::before {{ content: ''; position: absolute; top: 0; left: 0; width: 100%; height: 4px; background: linear-gradient(90deg, #10b981, #3b82f6); }}
    .auth-heading {{ font-size: 1.4rem; font-weight: 700; letter-spacing: -0.5px; margin-bottom: 0.5rem; color: var(--text-main); }}
    .auth-sub {{ color: var(--text-sub); font-size: 0.95rem; margin-bottom: 2rem; font-weight: 400; line-height: 1.5; }}
    .stTextInput label {{ color: var(--text-sub) !important; font-size: 0.75rem !important; font-weight: 700 !important; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 0.5rem !important; }}
    .stTextInput input {{ border-radius: 6px !important; border: 1px solid var(--border-heavy) !important; background: var(--bg-main) !important; color: var(--text-main) !important; padding: 0.75rem 1rem !important; font-size: 0.95rem !important; transition: all 0.2s; }}
    .stTextInput input:focus {{ border-color: #10b981 !important; box-shadow: 0 0 0 3px rgba(16,185,129,0.15) !important; }}
    [data-testid="stFormSubmitButton"] > button {{ border-radius: 6px !important; background: var(--btn-bg) !important; border: none !important; padding: 0.75rem !important; margin-top: 1.5rem !important; transition: all 0.2s ease !important; box-shadow: 0 4px 6px rgba(0,0,0,0.1) !important; }}
    [data-testid="stFormSubmitButton"] > button:hover {{ transform: translateY(-2px) !important; box-shadow: 0 8px 15px rgba(0,0,0,0.15) !important; }}
    [data-testid="stFormSubmitButton"] > button p {{ color: var(--btn-text) !important; font-weight: 700 !important; font-size: 0.95rem !important; }}

    /* ── REUSABLE COMPONENT CLASSES ── */
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
    
    /* Responsive Adjustments */
    @media (max-width: 1024px) {{ .nav-center {{ display: none; }} .enterprise-navbar {{ padding: 0 2rem; }} }}
    </style>
    """

@st.cache_data(show_spinner=False)
def get_cached_navbar_html(theme: str) -> str:
    toggle_icon = "🌞" if theme == 'light' else "🌓"
    
    html = """
    <div id="top-anchor" style="position: absolute; top: 0; left: 0; width: 1px; height: 1px;"></div>
    
    <header class="enterprise-navbar">
        <a href="#top-anchor" class="nav-left" onclick="window.scrollTo({top:0, behavior:'smooth'});">
            <div class="nav-logo">📦 LogiTrack PK</div>
            <div class="nav-divider"></div>
            <span class="nav-subtitle">Freight OS</span>
        </a>
        
        <nav class="nav-center">
            <a href="#network" class="nav-link">Operations</a>
            <a href="#ecosystem" class="nav-link">Freight Network</a>
            <a href="#capabilities" class="nav-link">Platform Modules</a>
            <a href="#team" class="nav-link">Engineering</a>
        </nav>
        
        <div class="nav-right">
            <div class="theme-toggle-btn" onclick="window.toggleTheme && window.toggleTheme();" title="Toggle Theme">TOGGLE_ICON_PLACEHOLDER</div>
            <a href="#auth-portal" class="nav-cta">System Access</a>
        </div>
    </header>
    
    <img src="data:image/gif;base64,R0lGODlhAQABAIAAAP///wAAACH5BAEAAAAALAAAAAABAAEAAAICRAEAOw==" style="display:none;" onload="if(!window.navScriptLoaded){window.navScriptLoaded=true;setInterval(function(){var b=window.parent.document.querySelectorAll('button');for(var i=0;i<b.length;i++){if(b[i].innerText.includes('HiddenThemeBtn')){var c=b[i].closest('div[data-testid=\\'stButton\\']');if(c)c.style.display='none';}}},50);window.toggleTheme=function(){var bs=window.parent.document.querySelectorAll('button');for(var j=0;j<bs.length;j++){if(bs[j].innerText.includes('HiddenThemeBtn')){bs[j].click();break;}}};}">
    """
    return html.replace('TOGGLE_ICON_PLACEHOLDER', toggle_icon)

@st.cache_data(show_spinner=False)
def get_cached_hero_brand_html() -> str:
    return """
    <span class='hero-super'>Enterprise Logistics OS</span>
    <div class='hero-title'>Logistics visibility,<br>engineered for scale.</div>
    <div class='hero-desc'>The centralized operating system for Pakistan's freight network. Command your fleet, track shipments, and coordinate dispatch operations with unprecedented clarity.</div>
    
    <div class='corridor-map'>
        <div class='corridor-line'></div>
        <div class='corridor-flow'></div>
        <div class='corridor-node' style='left: 0%;'><div class='node-dot'></div><span class='node-label'>KHI</span></div>
        <div class='corridor-node' style='left: 33%;'><div class='node-dot'></div><span class='node-label'>LHE</span></div>
        <div class='corridor-node' style='left: 66%;'><div class='node-dot'></div><span class='node-label'>ISB</span></div>
        <div class='corridor-node' style='left: 100%;'><div class='node-dot'></div><span class='node-label'>PEW</span></div>
    </div>
    """

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
                <div class='card-title'>Shayan Rizwan</div>
                <div class='card-desc'>Platform Architecture</div>
            </div>
            <div class='lp-card' style='text-align: center; padding: 3rem 2rem;'>
                <div style='width: 64px; height: 64px; border-radius: 50%; background: var(--border-mid); margin: 0 auto 1.5rem auto; display: flex; align-items: center; justify-content: center; font-size: 1.2rem; border: 1px solid var(--border-heavy); font-weight: 700; color: var(--text-main);'>AS</div>
                <div class='card-title'>Agha Salaat</div>
                <div class='card-desc'>Systems Engineering</div>
            </div>
            <div class='lp-card' style='text-align: center; padding: 3rem 2rem;'>
                <div style='width: 64px; height: 64px; border-radius: 50%; background: var(--border-mid); margin: 0 auto 1.5rem auto; display: flex; align-items: center; justify-content: center; font-size: 1.2rem; border: 1px solid var(--border-heavy); font-weight: 700; color: var(--text-main);'>AM</div>
                <div class='card-title'>Anzar Mubashir</div>
                <div class='card-desc'>Backend Infrastructure</div>
            </div>
        </div>
    </section>

    <footer class='lp-footer'>
        <div class='footer-text'><strong style='color:var(--text-main); font-size: 1.05rem;'>📦 LogiTrack PK</strong><br><br>© 2026 LogiTrack Systems. All rights reserved.</div>
        <div class='footer-text' style='text-align: right;'>Version 2.4.0 (Enterprise Build)<br><br><span style='opacity: 0.7;'>Protected by Zero Trust Security Architecture.</span></div>
    </footer>
    """

@st.cache_data(show_spinner=False)
def get_cached_shell_css() -> str:
    return """
    <style>
        [data-testid="stSidebar"], [data-testid="collapsedControl"] { display: none !important; }
        .block-container { padding-left: 1.75rem !important; padding-right: 1.75rem !important; padding-top: 1.5rem !important; max-width: 100% !important; }
        .stButton > button[kind="primary"] { border-radius: 6px !important; background: linear-gradient(135deg, #059669, #10b981) !important; color: white !important; border: none !important; font-weight: 700 !important; transition: all 0.15s !important; }
        .stButton > button[kind="primary"]:hover { transform: translateY(-1px) !important; box-shadow: 0 6px 16px -4px rgba(16,185,129,0.4) !important; }
        .stButton > button:not([kind="primary"]) { border-radius: 6px !important; border: 1px solid rgba(255,255,255,0.1) !important; color: #94a3b8 !important; background: transparent !important; font-weight: 600 !important; transition: all 0.15s !important; }
        .stButton > button:not([kind="primary"]):hover { border-color: #10b981 !important; color: #10b981 !important; transform: translateY(-1px) !important; background: rgba(16,185,129,0.05) !important;}
        .stButton > button:disabled { opacity: 0.3 !important; cursor: not-allowed !important; transform: none !important; }
    </style>
    """

# ─── 2. ENTERPRISE SAAS LANDING & AUTH PORTAL ─────────────────────────────────
def login_screen():
    
    # Render globally cached CSS
    st.markdown(get_cached_login_css(st.session_state.theme), unsafe_allow_html=True)
    
    # Render Unified Floating Navbar
    st.markdown(get_cached_navbar_html(st.session_state.theme), unsafe_allow_html=True)

    # Invisible anchor for authentication scrolling
    st.markdown("<div id='auth-portal' style='position:absolute; top:-20px;'></div>", unsafe_allow_html=True)

    # Hidden Streamlit Bridge Button
    st.button("HiddenThemeBtn", on_click=toggle_theme)

    # ─── 2.1 HERO SECTION (Streamlit Columns) ───
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
                st.session_state.theme = 'dark' # Prevent UI flash entering Dashboard
                st.rerun()
            else:
                st.error("Authentication failed. Invalid credentials or deactivated account.")

    # ─── 2.2 MARKETING & DOCUMENTATION SECTIONS ───
    st.markdown(get_cached_marketing_sections_html(), unsafe_allow_html=True)


# ─── 3. ENTERPRISE APP SHELL (AUTHENTICATED) ──────────────────────────────────
if not st.session_state.user:
    login_screen()
else:
    # Protect Dashboard Dark Mode UI
    st.markdown("<img src='dummy' style='display:none;' onerror=\"document.body.classList.remove('light-theme');\">", unsafe_allow_html=True)
    apply_enterprise_theme()

    # ── Top bar CSS + layout ──
    st.markdown(get_cached_shell_css(), unsafe_allow_html=True)

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

    nav_col, workspace_col = st.columns([2, 8], gap="large")
    user_role = st.session_state.user['role']

    # ─ LEFT: Navigation rail ─
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

    # ─ RIGHT: Workspace ─
    with workspace_col:
        if selected_module == "Dashboard": dashboard.render_page()
        elif selected_module == "Shipments": shipments.render_page()
        elif selected_module == "Fleet": fleet.render_page()
        elif selected_module == "Reports": reports.render_page()
        elif selected_module == "Audit Logs": audit_logs.render_page()