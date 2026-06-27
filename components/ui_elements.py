import streamlit as st
from st_aggrid import JsCode

# ─── SHARED AGGRID CSS (used by shipments, fleet, audit_logs) ─────────────────
AGGRID_CSS = {
    ".ag-root-wrapper": {
        "border-radius": "12px !important",
        "border": "1px solid #1a2744 !important",
        "background-color": "#0d1526 !important",
        "overflow": "hidden !important",
        "font-family": "'Inter', system-ui, sans-serif !important",
    },
    ".ag-header": {
        "background-color": "#070d1a !important",
        "border-bottom": "1px solid #1a2744 !important",
    },
    ".ag-header-cell": {"padding": "0 16px !important"},
    ".ag-header-cell-text": {
        "color": "#364a65 !important",
        "font-family": "'Inter', sans-serif !important",
        "font-weight": "700 !important",
        "font-size": "0.65rem !important",
        "text-transform": "uppercase !important",
        "letter-spacing": "1.2px !important",
    },
    ".ag-row": {
        "background-color": "#0d1526 !important",
        "border-bottom": "1px solid #0f1a2e !important",
        "color": "#cbd5e1 !important",
        "font-family": "'Inter', sans-serif !important",
        "font-size": "0.84rem !important",
        "transition": "background-color 0.12s ease !important",
    },
    ".ag-row:hover": {"background-color": "#111d33 !important", "color": "#f1f5f9 !important"},
    ".ag-row-selected": {"background-color": "#172554 !important"},
    ".ag-cell": {
        "border-right": "none !important",
        "display": "flex !important",
        "align-items": "center !important",
        "padding": "0 16px !important",
    },
    ".ag-paging-panel": {
        "background-color": "#070d1a !important",
        "border-top": "1px solid #1a2744 !important",
        "color": "#364a65 !important",
        "font-family": "'Inter', sans-serif !important",
        "font-size": "0.78rem !important",
        "padding": "8px 16px !important",
    },
    ".ag-icon": {"color": "#364a65 !important"},
    ".ag-paging-button": {"color": "#64748b !important"},
    ".ag-side-bar": {
        "background-color": "#0d1526 !important",
        "border-left": "1px solid #1a2744 !important",
    },
    ".ag-tool-panel-wrapper": {"background-color": "#0d1526 !important"},
}

# ─── SHARED CELLSTYLE JS ──────────────────────────────────────────────────────
ID_JS = JsCode("""
function(p){ return {color:'#4a6080',fontFamily:'JetBrains Mono,monospace',fontSize:'0.78rem',fontWeight:'500'}; }
""")

TS_JS = JsCode("""
function(p){ return {color:'#364a65',fontFamily:'JetBrains Mono,monospace',fontSize:'0.75rem'}; }
""")

ROUTE_JS = JsCode("""
function(params) { return {color: '#94a3b8', fontSize: '0.82rem'}; }
""")
