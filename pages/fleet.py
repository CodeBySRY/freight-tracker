import streamlit as st
import pandas as pd
from database import get_db
from st_aggrid import AgGrid, GridOptionsBuilder, ColumnsAutoSizeMode, JsCode

# ─── PREMIUM AG-GRID CSS ─────────────────────────────────────────────────────
enterprise_css = {
    ".ag-root-wrapper":     {"border-radius": "16px !important", "border": "1px solid #1e293b !important", "background-color": "#0f172a !important", "overflow": "hidden !important"},
    ".ag-header":           {"background-color": "#020617 !important", "border-bottom": "1px solid #1e293b !important"},
    ".ag-header-cell-text": {"color": "#64748b !important", "font-family": "'Plus Jakarta Sans', sans-serif !important", "font-weight": "700 !important", "text-transform": "uppercase", "letter-spacing": "0.8px", "font-size": "0.72rem !important"},
    ".ag-row":              {"background-color": "#0f172a !important", "border-bottom": "1px solid #0f1a2e !important", "color": "#e2e8f0 !important", "font-family": "'Plus Jakarta Sans', sans-serif !important", "transition": "background-color 0.15s ease"},
    ".ag-row:hover":        {"background-color": "#1a2744 !important"},
    ".ag-row-selected":     {"background-color": "#172554 !important"},
    ".ag-cell":             {"border-right": "none !important", "display": "flex", "align-items": "center", "font-size": "0.85rem !important"},
    ".ag-paging-panel":     {"background-color": "#020617 !important", "border-top": "1px solid #1e293b !important", "color": "#64748b !important", "font-family": "'Plus Jakarta Sans', sans-serif !important", "font-size": "0.8rem !important"},
}

AVAILABILITY_JSCODE = JsCode("""
function(params) {
    if (params.value === 'Available') return {color:'#34d399', backgroundColor:'#022c22', borderRadius:'20px', textAlign:'center', fontWeight:'700', padding:'3px 10px', fontSize:'0.75rem'};
    return {color:'#fb923c', backgroundColor:'#431407', borderRadius:'20px', textAlign:'center', fontWeight:'700', padding:'3px 10px', fontSize:'0.75rem'};
}
""")

VTYPE_JSCODE = JsCode("""
function(params) {
    return {color:'#94a3b8', fontStyle:'italic'};
}
""")


def render_page():
    st.markdown("""
        <div style='margin-bottom:1.75rem;'>
            <div style='color:#475569;font-size:0.7rem;font-weight:800;letter-spacing:1.5px;text-transform:uppercase;margin-bottom:4px;'>FLEET</div>
            <h2 style='color:#f8fafc;font-weight:800;font-size:1.75rem;margin:0;letter-spacing:-0.5px;'>Fleet Operations</h2>
            <p style='color:#64748b;font-size:0.88rem;margin:4px 0 0 0;'>Manage carrier capacity, vehicle classifications, and dispatch availability.</p>
        </div>
    """, unsafe_allow_html=True)

    conn = get_db()
    cur  = conn.cursor()
    try:
        cur.execute("""
            SELECT
                carrier_id                                                    AS "ID",
                company_name                                                  AS "Company",
                contact_phone                                                 AS "Contact",
                vehicle_type                                                  AS "Vehicle Type",
                CASE WHEN is_available THEN 'Available' ELSE 'Dispatched' END AS "Status"
            FROM carriers
            ORDER BY is_available DESC, company_name ASC
        """)
        data = cur.fetchall()
    except Exception as e:
        st.error(f"Failed to fetch fleet data: {e}")
        data = []
    finally:
        conn.close()

    if not data:
        st.info("No carriers registered in the fleet.")
        return

    df = pd.DataFrame(data)

    # Summary pills
    total     = len(df)
    available = len(df[df['Status'] == 'Available'])
    dispatched = total - available

    st.markdown(f"""
        <div style='display:flex;gap:0.75rem;margin-bottom:1rem;flex-wrap:wrap;'>
            <span style='background:#1e293b;color:#94a3b8;border:1px solid #334155;border-radius:20px;padding:4px 14px;font-size:0.78rem;font-weight:700;'>🚛 {total} Total Carriers</span>
            <span style='background:#022c22;color:#34d399;border:1px solid #065f4633;border-radius:20px;padding:4px 14px;font-size:0.78rem;font-weight:700;'>✅ {available} Available</span>
            <span style='background:#431407;color:#fb923c;border:1px solid #9a341233;border-radius:20px;padding:4px 14px;font-size:0.78rem;font-weight:700;'>🚚 {dispatched} Dispatched</span>
        </div>
    """, unsafe_allow_html=True)

    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_pagination(paginationAutoPageSize=True)
    gb.configure_selection('single')
    gb.configure_grid_options(rowHeight=52, headerHeight=48, animateRows=True)
    gb.configure_column("Status",       cellStyle=AVAILABILITY_JSCODE)
    gb.configure_column("Vehicle Type", cellStyle=VTYPE_JSCODE)
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
