import streamlit as st
import pandas as pd
from database import get_db
from st_aggrid import AgGrid, GridOptionsBuilder, ColumnsAutoSizeMode, JsCode

# Premium Enterprise CSS for AG Grid
enterprise_css = {
    ".ag-root-wrapper": {"border-radius": "16px !important", "border": "1px solid #1e293b !important", "background-color": "#0f172a !important"},
    ".ag-header": {"background-color": "#020617 !important", "border-bottom": "1px solid #1e293b !important"},
    ".ag-header-cell-text": {"color": "#94a3b8 !important", "font-family": "'Plus Jakarta Sans', sans-serif !important", "font-weight": "700 !important", "text-transform": "uppercase", "letter-spacing": "1px"},
    ".ag-row": {"background-color": "#0f172a !important", "border-bottom": "1px solid #1e293b !important", "color": "#f8fafc !important", "font-family": "'Plus Jakarta Sans', sans-serif !important", "transition": "background-color 0.2s ease"},
    ".ag-row:hover": {"background-color": "#1e293b !important"},
    ".ag-cell": {"border-right": "none !important", "display": "flex", "align-items": "center"},
    ".ag-paging-panel": {"background-color": "#020617 !important", "border-top": "1px solid #1e293b !important", "color": "#94a3b8 !important", "font-family": "'Plus Jakarta Sans', sans-serif !important"}
}

def render_page():
    st.markdown("<h2 style='font-weight: 800; color: #f8fafc; margin-bottom: 0.5rem;'>🏢 Fleet Operations</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #94a3b8; font-size: 0.95rem; margin-bottom: 1.5rem;'>Manage carrier capacity, vehicle types, and dispatch availability.</p>", unsafe_allow_html=True)
    
    conn = get_db()
    cur = conn.cursor()
    try:
        cur.execute("SELECT carrier_id AS \"Carrier ID\", company_name AS \"Company\", contact_phone AS \"Dispatch Contact\", vehicle_type AS \"Classification\", CASE WHEN is_available THEN 'Available' ELSE 'Dispatched' END AS \"Status\" FROM carriers ORDER BY is_available DESC, company_name ASC")
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
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_pagination(paginationAutoPageSize=True)
    gb.configure_selection('single')
    gb.configure_grid_options(rowHeight=55, headerHeight=50)
    
    availability_jscode = JsCode("""
    function(params) {
        if (params.value === 'Available') { return {'color': '#34d399', 'backgroundColor': '#022c22', 'borderRadius': '8px', 'textAlign': 'center', 'fontWeight': '600', 'padding': '4px 8px'}; }
        return {'color': '#cbd5e1', 'backgroundColor': '#334155', 'borderRadius': '8px', 'textAlign': 'center', 'fontWeight': '600', 'padding': '4px 8px'};
    }
    """)
    gb.configure_column("Status", cellStyle=availability_jscode)
    gridOptions = gb.build()

    AgGrid(df, gridOptions=gridOptions, enable_enterprise_modules=False, columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS, theme='streamlit', allow_unsafe_jscode=True, custom_css=enterprise_css)