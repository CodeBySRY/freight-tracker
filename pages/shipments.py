import streamlit as st
import pandas as pd
from database import get_db
from st_aggrid import AgGrid, GridOptionsBuilder, ColumnsAutoSizeMode, JsCode

# ─── AG GRID THEME ───────────────────────────────────────────────────────────
# Designed to match industry-grade freight TMS tables (GoFreight / CargoWise style):
# – Near-black header, tight row heights, monospace IDs, pill-shaped status badges
_CSS = {
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
    ".ag-header-cell": {
        "padding": "0 16px !important",
    },
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
    ".ag-row:hover": {
        "background-color": "#111d33 !important",
        "color": "#f1f5f9 !important",
    },
    ".ag-row-selected": {
        "background-color": "#172554 !important",
    },
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

_STATUS_JS = JsCode("""
function(params) {
    const v = params.value || '';
    const map = {
        'Delivered':  {color:'#34d399', bg:'#022c22', border:'#065f46'},
        'In Transit': {color:'#60a5fa', bg:'#172554', border:'#1d4ed8'},
        'Delayed':    {color:'#fb923c', bg:'#431407', border:'#9a3412'},
        'Cancelled':  {color:'#f87171', bg:'#450a0a', border:'#991b1b'},
        'Pending':    {color:'#94a3b8', bg:'#1a2744', border:'#253355'},
    };
    const s = map[v] || map['Pending'];
    return {
        color: s.color,
        backgroundColor: s.bg,
        border: '1px solid ' + s.border,
        borderRadius: '20px',
        textAlign: 'center',
        fontWeight: '700',
        fontSize: '0.7rem',
        letterSpacing: '0.3px',
        padding: '2px 10px',
        display: 'inline-block',
    };
}
""")

_PRIORITY_JS = JsCode("""
function(params) {
    const v = params.value || '';
    if (v === 'Critical')  return {color:'#f87171', fontWeight:'700'};
    if (v === 'Overnight') return {color:'#fb923c', fontWeight:'700'};
    if (v === 'Expedited') return {color:'#fbbf24', fontWeight:'600'};
    return {color:'#64748b'};
}
""")

_ID_JS = JsCode("""
function(params) {
    return {
        color: '#4a6080',
        fontFamily: "'JetBrains Mono', monospace",
        fontSize: '0.78rem',
        fontWeight: '500',
    };
}
""")

_ROUTE_JS = JsCode("""
function(params) {
    return {color: '#94a3b8', fontSize: '0.82rem'};
}
""")


def render_page():
    st.markdown("""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600&display=swap');
        </style>
        <div style='margin-bottom:1.75rem;'>
            <div style='color:#364a65;font-size:0.65rem;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;margin-bottom:4px;'>TRACKING</div>
            <h2 style='color:#f1f5f9;font-weight:800;font-size:1.65rem;margin:0;letter-spacing:-0.5px;font-family:Inter,sans-serif;'>Shipment Register</h2>
            <p style='color:#364a65;font-size:0.85rem;margin:4px 0 0 0;'>Live freight movement across all active and completed runs.</p>
        </div>
    """, unsafe_allow_html=True)

    conn = get_db()
    cur  = conn.cursor()
    try:
        cur.execute("""
            SELECT
                s.shipment_id        AS "ID",
                o.customer_name      AS "Client",
                o.origin_city        AS "Origin",
                o.destination_city   AS "Destination",
                o.cargo_type         AS "Cargo",
                o.priority           AS "Priority",
                c.company_name       AS "Carrier",
                s.status             AS "Status",
                TO_CHAR(s.assigned_at, 'DD MMM, HH24:MI') AS "Assigned"
            FROM shipments s
            JOIN orders   o ON s.order_id   = o.order_id
            JOIN carriers c ON s.carrier_id = c.carrier_id
            ORDER BY s.assigned_at DESC
        """)
        data = cur.fetchall()
    except Exception as e:
        st.error(f"Failed to fetch shipment data: {e}")
        data = []
    finally:
        conn.close()

    if not data:
        st.markdown("""
            <div style='background:#0d1526;border:1px solid #1a2744;border-radius:12px;padding:3rem;text-align:center;'>
                <div style='font-size:2rem;margin-bottom:0.75rem;'>📭</div>
                <div style='color:#4a6080;font-size:0.9rem;font-weight:600;'>No shipments in the system yet.</div>
                <div style='color:#253355;font-size:0.8rem;margin-top:0.3rem;'>Draft an order and dispatch a carrier to get started.</div>
            </div>
        """, unsafe_allow_html=True)
        return

    df = pd.DataFrame(data)

    # ── Status summary strip ─────────────────────────────────────────────────
    status_colors = {
        'In Transit': ('#172554','#60a5fa'),
        'Delivered':  ('#022c22','#34d399'),
        'Delayed':    ('#431407','#fb923c'),
        'Cancelled':  ('#450a0a','#f87171'),
        'Pending':    ('#1a2744','#64748b'),
    }
    pills = ""
    for status, cnt in df['Status'].value_counts().items():
        bg, fg = status_colors.get(status, ('#1a2744','#64748b'))
        pills += f"<span style='background:{bg};color:{fg};border:1px solid {fg}22;border-radius:20px;padding:4px 14px;font-size:0.75rem;font-weight:700;'>{cnt} {status}</span>"
    st.markdown(f"<div style='display:flex;flex-wrap:wrap;gap:0.4rem;margin-bottom:1rem;'>{pills}</div>", unsafe_allow_html=True)

    # ── AG Grid ──────────────────────────────────────────────────────────────
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=15)
    gb.configure_side_bar(filters_panel=True, columns_panel=False)
    gb.configure_selection('single')
    gb.configure_grid_options(rowHeight=46, headerHeight=44, animateRows=True, suppressCellFocus=True)
    gb.configure_column("ID",          cellStyle=_ID_JS, maxWidth=70,  pinned='left')
    gb.configure_column("Status",      cellStyle=_STATUS_JS, maxWidth=130)
    gb.configure_column("Priority",    cellStyle=_PRIORITY_JS, maxWidth=110)
    gb.configure_column("Origin",      cellStyle=_ROUTE_JS)
    gb.configure_column("Destination", cellStyle=_ROUTE_JS)
    gb.configure_column("Assigned",    cellStyle=JsCode("function(p){return{color:'#4a6080',fontFamily:'JetBrains Mono,monospace',fontSize:'0.75rem'}}"))

    AgGrid(
        df,
        gridOptions=gb.build(),
        enable_enterprise_modules=False,
        columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS,
        theme='streamlit',
        allow_unsafe_jscode=True,
        custom_css=_CSS,
        height=560,
    )

    # ── Export ───────────────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    c1, _, _ = st.columns([1.3, 1, 2.5])
    with c1:
        st.download_button(
            "📥 Export to CSV",
            data=df.to_csv(index=False).encode('utf-8'),
            file_name="Shipments_LogiTrack.csv",
            mime="text/csv",
            use_container_width=True,
        )
