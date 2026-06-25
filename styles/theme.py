import streamlit as st

def apply_enterprise_theme():
    st.markdown("""
        <style>
            /* ─── FONTS: Geist for data, Inter for UI ─── */
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

            /* ─── GLOBAL BASE ─── */
            html, body, .stApp {
                background-color: #070d1a !important;
                color: #e2e8f0;
                font-family: 'Inter', system-ui, -apple-system, sans-serif;
                -webkit-font-smoothing: antialiased;
            }
            #MainMenu { visibility: hidden; }
            footer    { visibility: hidden; }
            header    { visibility: hidden; }

            /* ─── PAGE ANIMATION ─── */
            @keyframes fadeUp {
                from { opacity: 0; transform: translateY(10px); }
                to   { opacity: 1; transform: translateY(0); }
            }
            .main .block-container {
                animation: fadeUp 0.45s cubic-bezier(0.22, 1, 0.36, 1) both;
            }

            /* ─── KPI CARDS ─── */
            .kpi-card {
                background: #0d1526;
                border: 1px solid #1a2744;
                border-radius: 12px;
                padding: 1.25rem 1.4rem 1.1rem;
                position: relative;
                overflow: hidden;
                transition: transform 0.18s ease, box-shadow 0.18s ease, border-color 0.18s ease;
                cursor: default;
            }
            .kpi-card::after {
                content: '';
                position: absolute;
                top: 0; left: 0; right: 0; height: 2px;
                background: var(--kpi-accent, #10b981);
                border-radius: 12px 12px 0 0;
            }
            .kpi-card:hover {
                transform: translateY(-2px);
                box-shadow: 0 8px 24px -6px rgba(0,0,0,0.5);
                border-color: #253355;
            }
            .kpi-icon {
                font-size: 1.35rem;
                margin-bottom: 0.65rem;
                display: block;
                line-height: 1;
            }
            .kpi-title {
                color: #4a6080;
                font-size: 0.65rem;
                font-weight: 700;
                text-transform: uppercase;
                letter-spacing: 1.3px;
                margin-bottom: 0.35rem;
            }
            .kpi-value {
                color: #f1f5f9;
                font-size: 2.2rem;
                font-weight: 800;
                line-height: 1;
                letter-spacing: -1.5px;
                font-variant-numeric: tabular-nums;
            }
            .kpi-sub {
                color: #364a65;
                font-size: 0.72rem;
                margin-top: 0.45rem;
                font-weight: 500;
            }

            /* ─── ACTION CARDS ─── */
            .feature-card {
                background: #0d1526;
                border: 1px solid #1a2744;
                border-radius: 12px;
                min-height: 120px;
                transition: border-color 0.18s ease, box-shadow 0.18s ease;
            }
            .feature-card:hover {
                border-color: #10b981;
                box-shadow: 0 0 0 1px rgba(16,185,129,0.12), 0 6px 20px -6px rgba(16,185,129,0.12);
            }

            /* ─── ACTIVITY FEED ─── */
            .activity-feed {
                background: #0d1526;
                border: 1px solid #1a2744;
                border-radius: 12px;
                padding: 1rem 1.1rem;
                max-height: 315px;
                overflow-y: auto;
            }
            .activity-feed::-webkit-scrollbar { width: 3px; }
            .activity-feed::-webkit-scrollbar-track { background: transparent; }
            .activity-feed::-webkit-scrollbar-thumb { background: #1a2744; border-radius: 3px; }
            .activity-item {
                display: flex; align-items: flex-start; gap: 0.7rem;
                padding: 0.6rem 0;
                border-bottom: 1px solid #0f1a2e;
            }
            .activity-item:last-child { border-bottom: none; }
            .activity-dot {
                width: 7px; height: 7px; border-radius: 50%;
                flex-shrink: 0; margin-top: 5px;
            }
            .activity-text { color: #94a3b8; font-size: 0.8rem; line-height: 1.45; }
            .activity-time { color: #364a65; font-size: 0.7rem; margin-top: 2px; font-family: 'JetBrains Mono', monospace; }

            /* ─── SECTION LABELS ─── */
            .section-label {
                color: #364a65;
                font-size: 0.65rem;
                font-weight: 700;
                letter-spacing: 1.5px;
                text-transform: uppercase;
                margin-bottom: 0.65rem;
            }
            .section-divider {
                border: none;
                border-top: 1px solid #111d33;
                margin: 1.5rem 0;
            }

            /* ─── UNIFIED STATUS BADGES ─── */
            .badge {
                padding: 2px 9px;
                border-radius: 20px;
                font-size: 0.7rem;
                font-weight: 700;
                display: inline-block;
                border: 1px solid transparent;
                letter-spacing: 0.3px;
                font-family: 'Inter', sans-serif;
            }
            .badge-delivered  { background:#022c22; color:#34d399; border-color:#065f46; }
            .badge-transit    { background:#172554; color:#60a5fa; border-color:#1d4ed8; }
            .badge-delayed    { background:#451a03; color:#fb923c; border-color:#9a3412; }
            .badge-cancelled  { background:#450a0a; color:#f87171; border-color:#991b1b; }
            .badge-pending    { background:#1a2744; color:#64748b; border-color:#253355; }

            /* ─── INPUTS ─── */
            .stTextInput input,
            .stTextArea textarea,
            .stSelectbox div[data-baseweb="select"],
            .stNumberInput input,
            .stDateInput input {
                border-radius: 8px !important;
                border: 1px solid #1a2744 !important;
                background-color: #0d1526 !important;
                color: #e2e8f0 !important;
                font-family: 'Inter', sans-serif !important;
                font-size: 0.875rem !important;
                transition: border-color 0.15s ease, box-shadow 0.15s ease;
            }
            .stTextInput input:focus,
            .stTextArea textarea:focus {
                border-color: #10b981 !important;
                box-shadow: 0 0 0 3px rgba(16,185,129,0.12) !important;
                outline: none !important;
            }

            /* ─── BUTTONS ─── */
            /* Primary */
            .stButton > button[kind="primary"],
            button[data-testid="baseButton-primary"] {
                border-radius: 8px !important;
                background: linear-gradient(135deg, #059669, #10b981) !important;
                color: #fff !important;
                border: none !important;
                font-weight: 700 !important;
                font-family: 'Inter', sans-serif !important;
                font-size: 0.85rem !important;
                letter-spacing: 0.2px;
                transition: all 0.15s ease !important;
            }
            .stButton > button[kind="primary"]:hover {
                transform: translateY(-1px) !important;
                box-shadow: 0 6px 18px -4px rgba(16,185,129,0.4) !important;
            }
            /* Secondary */
            .stButton > button:not([kind="primary"]) {
                border-radius: 8px !important;
                border: 1px solid #1a2744 !important;
                color: #64748b !important;
                background: #0d1526 !important;
                font-weight: 600 !important;
                font-family: 'Inter', sans-serif !important;
                font-size: 0.85rem !important;
                transition: all 0.15s ease !important;
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

            /* ─── DOWNLOAD BUTTON ─── */
            .stDownloadButton > button {
                border-radius: 8px !important;
                border: 1px solid #1a2744 !important;
                background: #0d1526 !important;
                color: #64748b !important;
                font-weight: 600 !important;
                font-family: 'Inter', sans-serif !important;
                font-size: 0.82rem !important;
                transition: all 0.15s !important;
            }
            .stDownloadButton > button:hover {
                border-color: #10b981 !important;
                color: #10b981 !important;
            }

            /* ─── AG GRID GLOBAL OVERRIDES ─── */
            /* These target the streamlit-aggrid component wrapper */
            .stAgGrid {
                border-radius: 12px !important;
                overflow: hidden !important;
            }

            /* ─── PLOTLY CHART CONTAINER ─── */
            .stPlotlyChart > div {
                border-radius: 12px;
            }

            /* ─── ALERTS ─── */
            [data-testid="stAlert"] {
                border-radius: 10px !important;
                font-family: 'Inter', sans-serif !important;
                font-size: 0.875rem !important;
            }

            /* ─── SELECTBOX DROPDOWN ─── */
            [data-baseweb="popover"] {
                background: #0d1526 !important;
                border: 1px solid #1a2744 !important;
                border-radius: 8px !important;
            }
            [data-baseweb="option"] {
                background: #0d1526 !important;
                color: #e2e8f0 !important;
                font-family: 'Inter', sans-serif !important;
            }
            [data-baseweb="option"]:hover {
                background: #1a2744 !important;
            }

            /* ─── COLLAPSE CONTROL ─── */
            [data-testid="collapsedControl"] {
                color: #4a6080 !important;
                background: transparent !important;
            }
            [data-testid="collapsedControl"]:hover { color: #10b981 !important; }

            /* ─── DIALOG / MODAL ─── */
            [data-testid="stDialog"] > div {
                background: #0d1526 !important;
                border: 1px solid #1a2744 !important;
                border-radius: 16px !important;
            }

        </style>
    """, unsafe_allow_html=True)
