import streamlit as st

def apply_enterprise_theme():
    """Injects global enterprise CSS, animations, and the Unified Status Badge system."""
    st.markdown(
        """
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');
            
            /* Global Typography & Deep Background */
            .stApp {
                background-color: #020617; 
                color: #f8fafc;
                font-family: 'Inter', system-ui, sans-serif;
            }

            /* Hide default Streamlit fluff (Header, Footer, Main Menu) */
            #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}

            /* Smooth page load animation */
            @keyframes fadeUp {
                from { opacity: 0; transform: translateY(15px); }
                to { opacity: 1; transform: translateY(0); }
            }
            .main .block-container { animation: fadeUp 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards; }

            /* ─── UNIFIED STATUS BADGE SYSTEM ─── */
            .badge {
                padding: 4px 10px;
                border-radius: 12px;
                font-size: 0.8rem;
                font-weight: 600;
                display: inline-block;
                border: 1px solid transparent;
            }
            .badge-delivered { background-color: #064e3b; color: #34d399; border-color: #065f46; } /* Green */
            .badge-transit { background-color: #1e3a8a; color: #60a5fa; border-color: #1e40af; }   /* Blue */
            .badge-delayed { background-color: #78350f; color: #fbbf24; border-color: #92400e; }   /* Orange */
            .badge-cancelled { background-color: #7f1d1d; color: #f87171; border-color: #991b1b; } /* Red */
            .badge-pending { background-color: #334155; color: #cbd5e1; border-color: #475569; }   /* Gray */

            /* Premium Inputs & Dataframes */
            .stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] {
                border-radius: 8px !important; border: 1px solid #1e293b !important;
                background-color: #0f172a !important; color: white !important; transition: all 0.2s ease;
            }
            .stTextInput input:focus, .stTextArea textarea:focus { 
                border-color: #10b981 !important; box-shadow: 0 0 0 2px rgba(16,185,129,0.2) !important; 
            }
            [data-testid="stDataFrame"] { border-radius: 12px; overflow: hidden; border: 1px solid #1e293b; }
            
            /* Subtly style the expand/collapse button to match the dark theme */
            [data-testid="collapsedControl"] {
                color: #94a3b8 !important;
                background-color: transparent !important;
                transition: color 0.2s ease;
            }
            [data-testid="collapsedControl"]:hover {
                color: #10b981 !important;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )