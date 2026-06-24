import streamlit as st
import pandas as pd
from database import get_db
from st_aggrid import AgGrid, GridOptionsBuilder, ColumnsAutoSizeMode, JsCode

# ─── PREMIUM AG-GRID CSS ─────────────────────────────────────────────────────
enterprise_css = {
    ".ag-root-wrapper":      {"border-radius": "16px !important", "border": "1px solid #1e293b !important", "background-color": "#0f172a !important", "overflow": "hidden !important"},
    ".ag-header":            {"background-color": "#020617 !important", "border-bottom": "1px solid #1e293b !important"},
    ".ag-header-cell-text":  {"color": "#64748b !important", "font-family": "'Plus Jakarta Sans', sans-serif !important", "font-weight": "700 !important", "text-transform": "uppercase", "letter-spacing": "0.8px", "font-size": "0.72rem !important"},
    ".ag-row":               {"background-color": "#0f172a !important", "border-bottom": "1px solid #0f1a2e !important", "color": "#e2e8f0 !important", "font-family": "'Plus Jakarta Sans', sans-serif !important", "transition": "background-color 0.15s ease"},
    ".ag-row:hover":         {"background-color": "#1a2744 !important"},
    ".ag-row-selected":      {"background-color": "#172554 !important"},
    ".ag-cell":              {"border-right": "none !important", "display": "flex", "align-items": "center", "font-size": "0.85rem !important"},
    ".ag-paging-panel":      {"background-color": "#020617 !important", "border-top": "1px solid #1e293b !important", "color": "#64748b !important", "font-family": "'Plus Jakarta Sans', sans-serif !important", "font-size": "0.8rem !important"},
    ".ag-icon":              {"color": "#64748b !important"},
    ".ag-side-bar":          {"background-color": "#0f172a !important", "border-left": "1px solid #1e293b !important"},
}

STATUS_JSCODE = JsCode("""
function(params) {
    const s = params.value;
    if (s === 'Delivered')  return {color:'#34d399', backgroundColor:'#022c22', borderRadius:'20px', textAlign:'center', fontWeight:'700', padding:'3px 10px', fontSize:'0.75rem', letterSpacing:'0.3px'};
    if (s === 'In Transit') return {color:'#60a5fa', backgroundColor:'#172554', borderRadius:'20px', textAlign:'center', fontWeight:'700', padding:'3px 10px', fontSize:'0.75rem', letterSpacing:'0.3px'};
    if (s === 'Delayed')    return {color:'#fb923c', backgroundColor:'#431407', borderRadius:'20px', textAlign:'center', fontWeight:'700', padding:'3px 10px', fontSize:'0.75rem', letterSpacing:'0.3px'};
    if (s === 'Cancelled')  return {color:'#f87171', backgroundColor:'#450a0a', borderRadius:'20px', textAlign:'center', fontWeight:'700', padding:'3px 10px', fontSize:'0.75rem', letterSpacing:'0.3px'};
    return {color:'#94a3b8', backgroundColor:'#1e293b', borderRadius:'20px', textAlign:'center', fontWeight:'700', padding:'3px 10px', fontSize:'0.75rem'};
}
""")

PRIORITY_JSCODE = JsCode("""
function(params) {
    const p = params.value;
    if (p === 'Critical')   return {color:'#f87171', fontWeight:'700'};
    if (p === 'Overnight')  return {color:'#fb923c', fontWeight:'700'};
    if (p === 'Expedited')  return {color:'#fbbf24', fontWeight:'600'};
    return {color:'#94a3b8'};
}
""")


def render_page():
    st.markdown("""
        <div style='margin-bottom:1.75rem;'>
            <div style='color:#475569;font-size:0.7rem;font-weight:800;letter-spacing:1.5px;text-transform:uppercase;margin-bottom:4px;'>TRACKING</div>
            <h2 style='color:#f8fafc;font-weight:800;font-size:1.75rem;margin:0;letter-spacing:-0.5px;'>Shipment Management</h2>
            <p style='color:#64748b;font-size:0.88rem;margin:4px 0 0 0;'>Monitor live freight movement, filter by status, and export dispatcher reports.</p>
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
                o.priority           AS "Priority",
                c.company_name       AS "Carrier",
                s.status             AS "Status",
                TO_CHAR(s.assigned_at, 'YYYY-MM-DD HH24:MI') AS "Assigned"
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
        st.info("No active shipments found in the system.")
        return

    df = pd.DataFrame(data)

    # Quick summary pills above grid
    status_counts = df['Status'].value_counts().to_dict()
    colors = {'In Transit': '#3b82f6', 'Delivered': '#10b981', 'Delayed': '#f59e0b', 'Cancelled': '#ef4444', 'Pending': '#64748b'}
    bgs    = {'In Transit': '#172554', 'Delivered': '#022c22', 'Delayed': '#451a03', 'Cancelled': '#450a0a', 'Pending': '#1e293b'}

    pill_html = ""
    for status, cnt in status_counts.items():
        c   = colors.get(status, '#64748b')
        bg  = bgs.get(status, '#1e293b')
        pill_html += f"<span style='background:{bg};color:{c};border:1px solid {c}33;border-radius:20px;padding:4px 14px;font-size:0.78rem;font-weight:700;'>{cnt} {status}</span>"

    st.markdown(f"<div style='display:flex;flex-wrap:wrap;gap:0.5rem;margin-bottom:1rem;'>{pill_html}</div>", unsafe_allow_html=True)

    # AG Grid
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_pagination(paginationAutoPageSize=True)
    gb.configure_side_bar()
    gb.configure_selection('single')
    gb.configure_grid_options(rowHeight=52, headerHeight=48, animateRows=True)
    gb.configure_column("Status",   cellStyle=STATUS_JSCODE)
    gb.configure_column("Priority", cellStyle=PRIORITY_JSCODE)
    gridOptions = gb.build()

    AgGrid(
        df,
        gridOptions=gridOptions,
        enable_enterprise_modules=False,
        columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS,
        theme='streamlit',
        allow_unsafe_jscode=True,
        custom_css=enterprise_css,
    )

    st.markdown("<br>", unsafe_allow_html=True)
    col1, _, _ = st.columns([1.2, 1, 2])
    with col1:
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Export to CSV", data=csv, file_name="Shipments_LogiTrack.csv", mime="text/csv", use_container_width=True)
