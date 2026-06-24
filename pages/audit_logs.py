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
    st.markdown("<h2 style='font-weight: 800; color: #f8fafc; margin-bottom: 0.5rem;'>🔐 Immutable Ledger</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #94a3b8; font-size: 0.95rem; margin-bottom: 1.5rem;'>System-wide audit trail for all operational transitions and authorizations.</p>", unsafe_allow_html=True)
    
    conn = get_db()
    cur = conn.cursor()
    try:
        cur.execute("SELECT sl.log_id AS \"Event ID\", sl.shipment_id AS \"Shipment Ref\", sl.old_status AS \"Previous State\", sl.new_status AS \"New State\", sl.notes AS \"System Notes\", u.full_name AS \"Authorized By\", TO_CHAR(sl.changed_at, 'YYYY-MM-DD HH24:MI:SS') AS \"Timestamp\" FROM status_log sl JOIN users u ON sl.changed_by = u.user_id ORDER BY sl.changed_at DESC LIMIT 200")
        data = cur.fetchall()
    except Exception as e:
        st.error(f"Failed to fetch audit logs: {e}")
        data = []
    finally:
        conn.close()

    if not data:
        st.info("No status transitions have been recorded yet.")
        return

    df = pd.DataFrame(data)
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_pagination(paginationAutoPageSize=True)
    gb.configure_side_bar()
    gb.configure_grid_options(rowHeight=55, headerHeight=50)
    
    status_jscode = JsCode("""
    function(params) {
        if (params.value === 'Delivered') return {'color': '#34d399', 'fontWeight': '700'};
        if (params.value === 'In Transit') return {'color': '#60a5fa', 'fontWeight': '700'};
        if (params.value === 'Delayed') return {'color': '#fbbf24', 'fontWeight': '700'};
        if (params.value === 'Cancelled') return {'color': '#f87171', 'fontWeight': '700'};
        return {'color': '#cbd5e1', 'fontWeight': '600'};
    }
    """)
    gb.configure_column("New State", cellStyle=status_jscode)
    gridOptions = gb.build()

    AgGrid(df, gridOptions=gridOptions, enable_enterprise_modules=False, columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS, theme='streamlit', allow_unsafe_jscode=True, custom_css=enterprise_css)