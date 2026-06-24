import streamlit as st

def apply_enterprise_theme():
    """Injects global enterprise CSS, animations, and the Unified Status Badge system."""
    st.markdown(
        """
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:ital,opsz,wght@0,6..18,300;0,6..18,400;0,6..18,500;0,6..18,600;0,6..18,700;0,6..18,800;1,6..18,400&display=swap');
            
            /* ─── GLOBAL BASE ─── */
            .stApp {
                background-color: #020617;
                color: #f8fafc;
                font-family: 'Plus Jakarta Sans', system-ui, sans-serif;
            }

            #MainMenu { visibility: hidden; }
            footer { visibility: hidden; }
            header { visibility: hidden; }

            /* ─── SMOOTH PAGE LOAD ─── */
            @keyframes fadeUp {
                from { opacity: 0; transform: translateY(12px); }
                to   { opacity: 1; transform: translateY(0); }
            }
            .main .block-container {
                animation: fadeUp 0.5s cubic-bezier(0.16, 1, 0.3, 1) forwards;
            }

            /* ─── KPI CARDS ─── */
            .kpi-card {
                background: #0f172a;
                border: 1px solid #1e293b;
                border-radius: 16px;
                padding: 1.4rem 1.5rem;
                transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
                position: relative;
                overflow: hidden;
            }
            .kpi-card:hover {
                transform: translateY(-3px);
                box-shadow: 0 12px 30px -8px rgba(0,0,0,0.5);
                border-color: #334155;
            }
            .kpi-card::before {
                content: '';
                position: absolute;
                top: 0; left: 0; right: 0;
                height: 3px;
                background: var(--kpi-accent, #10b981);
                border-radius: 16px 16px 0 0;
            }
            .kpi-icon {
                font-size: 1.6rem;
                margin-bottom: 0.5rem;
                display: block;
            }
            .kpi-title {
                color: #64748b;
                font-size: 0.72rem;
                font-weight: 700;
                text-transform: uppercase;
                letter-spacing: 1.2px;
                margin-bottom: 0.4rem;
            }
            .kpi-value {
                color: #f8fafc;
                font-size: 2.4rem;
                font-weight: 800;
                line-height: 1;
                letter-spacing: -1px;
            }
            .kpi-sub {
                color: #475569;
                font-size: 0.75rem;
                margin-top: 0.5rem;
                font-weight: 500;
            }

            /* ─── FEATURE / ACTION CARDS ─── */
            .feature-card {
                background: #0f172a;
                border: 1px solid #1e293b;
                border-radius: 14px;
                transition: all 0.2s ease;
                min-height: 130px;
            }
            .feature-card:hover {
                border-color: #10b981;
                box-shadow: 0 0 0 1px rgba(16,185,129,0.15), 0 8px 24px -8px rgba(16,185,129,0.15);
            }
            .feature-card-icon {
                font-size: 1.5rem;
                margin-bottom: 0.6rem;
                display: block;
            }

            /* ─── SECTION HEADINGS ─── */
            .section-label {
                color: #475569;
                font-size: 0.7rem;
                font-weight: 800;
                letter-spacing: 1.5px;
                text-transform: uppercase;
                margin-bottom: 0.75rem;
            }

            /* ─── ACTIVITY FEED ─── */
            .activity-feed {
                background: #0f172a;
                border: 1px solid #1e293b;
                border-radius: 14px;
                padding: 1.25rem;
                max-height: 320px;
                overflow-y: auto;
            }
            .activity-feed::-webkit-scrollbar { width: 4px; }
            .activity-feed::-webkit-scrollbar-track { background: transparent; }
            .activity-feed::-webkit-scrollbar-thumb { background: #1e293b; border-radius: 4px; }
            .activity-item {
                display: flex;
                align-items: flex-start;
                gap: 0.75rem;
                padding: 0.65rem 0;
                border-bottom: 1px solid #0f1a2e;
            }
            .activity-item:last-child { border-bottom: none; }
            .activity-dot {
                width: 8px; height: 8px;
                border-radius: 50%;
                flex-shrink: 0;
                margin-top: 5px;
            }
            .activity-text { color: #cbd5e1; font-size: 0.82rem; line-height: 1.45; }
            .activity-time { color: #475569; font-size: 0.72rem; margin-top: 2px; }

            /* ─── UNIFIED STATUS BADGE SYSTEM ─── */
            .badge {
                padding: 3px 10px;
                border-radius: 20px;
                font-size: 0.75rem;
                font-weight: 700;
                display: inline-block;
                border: 1px solid transparent;
                letter-spacing: 0.3px;
            }
            .badge-delivered  { background: #022c22; color: #34d399; border-color: #065f46; }
            .badge-transit    { background: #172554; color: #60a5fa; border-color: #1d4ed8; }
            .badge-delayed    { background: #451a03; color: #fb923c; border-color: #9a3412; }
            .badge-cancelled  { background: #450a0a; color: #f87171; border-color: #991b1b; }
            .badge-pending    { background: #1e293b; color: #94a3b8; border-color: #334155; }

            /* ─── DIVIDERS ─── */
            .section-divider {
                border: none;
                border-top: 1px solid #1e293b;
                margin: 1.5rem 0;
            }

            /* ─── INPUTS ─── */
            .stTextInput input,
            .stTextArea textarea,
            .stSelectbox div[data-baseweb="select"] {
                border-radius: 8px !important;
                border: 1px solid #1e293b !important;
                background-color: #0f172a !important;
                color: #f8fafc !important;
                transition: all 0.2s ease;
            }
            .stTextInput input:focus,
            .stTextArea textarea:focus {
                border-color: #10b981 !important;
                box-shadow: 0 0 0 2px rgba(16,185,129,0.15) !important;
            }

            /* ─── DATAFRAMES ─── */
            [data-testid="stDataFrame"] {
                border-radius: 12px;
                overflow: hidden;
                border: 1px solid #1e293b;
            }

            /* ─── PLOTLY CHARTS container ─── */
            .stPlotlyChart {
                background: #0f172a !important;
                border-radius: 14px;
                border: 1px solid #1e293b;
                padding: 0.5rem;
            }

            /* ─── INFO / WARNING / ERROR messages ─── */
            [data-testid="stAlert"] {
                border-radius: 10px !important;
            }

            /* ─── Collapse control ─── */
            [data-testid="collapsedControl"] {
                color: #94a3b8 !important;
                background-color: transparent !important;
            }
            [data-testid="collapsedControl"]:hover { color: #10b981 !important; }

            /* ─── DOWNLOAD BUTTON ─── */
            .stDownloadButton > button {
                border-radius: 8px !important;
                border: 1px solid #1e293b !important;
                background: #0f172a !important;
                color: #94a3b8 !important;
                font-weight: 600 !important;
                transition: all 0.2s !important;
            }
            .stDownloadButton > button:hover {
                border-color: #10b981 !important;
                color: #10b981 !important;
            }

            /* ─── NUMBER INPUT ─── */
            .stNumberInput input {
                background-color: #0f172a !important;
                border: 1px solid #1e293b !important;
                color: #f8fafc !important;
                border-radius: 8px !important;
            }

            /* ─── DATE INPUT ─── */
            .stDateInput input {
                background-color: #0f172a !important;
                border: 1px solid #1e293b !important;
                color: #f8fafc !important;
                border-radius: 8px !important;
            }

            /* ─── METRIC widget (native Streamlit) ─── */
            [data-testid="stMetric"] {
                background: #0f172a;
                border: 1px solid #1e293b;
                border-radius: 14px;
                padding: 1rem 1.25rem;
            }
            [data-testid="stMetricLabel"] { color: #64748b !important; font-size: 0.75rem !important; font-weight: 700 !important; text-transform: uppercase; letter-spacing: 1px; }
            [data-testid="stMetricValue"] { color: #f8fafc !important; font-size: 2rem !important; font-weight: 800 !important; }

        </style>
        """,
        unsafe_allow_html=True,
    )
