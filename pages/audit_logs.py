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
    ".ag-cell":             {"border-right": "none !important", "display": "flex", "align-items": "center", "font-size": "0.85rem !important"},
    ".ag-paging-panel":     {"background-color": "#020617 !important", "border-top": "1px solid #1e293b !important", "color": "#64748b !important", "font-family": "'Plus Jakarta Sans', sans-serif !important", "font-size": "0.8rem !important"},
    ".ag-side-bar":         {"background-color": "#0f172a !important", "border-left": "1px solid #1e293b !important"},
}

STATUS_JSCODE = JsCode("""
function(params) {
    const s = params.value;
    if (s === 'Delivered')  return {color:'#34d399', fontWeight:'700'};
    if (s === 'In Transit') return {color:'#60a5fa', fontWeight:'700'};
    if (s === 'Delayed')    return {color:'#fb923c', fontWeight:'700'};
    if (s === 'Cancelled')  return {color:'#f87171', fontWeight:'700'};
    return {color:'#94a3b8', fontWeight:'600'};
}
""")


def render_page():
    st.markdown("""
        <div style='margin-bottom:1.75rem;'>
            <div style='color:#475569;font-size:0.7rem;font-weight:800;letter-spacing:1.5px;text-transform:uppercase;margin-bottom:4px;'>COMPLIANCE</div>
            <h2 style='color:#f8fafc;font-weight:800;font-size:1.75rem;margin:0;letter-spacing:-0.5px;'>Immutable Audit Ledger</h2>
            <p style='color:#64748b;font-size:0.88rem;margin:4px 0 0 0;'>System-wide audit trail for all operational transitions and authorizations. Last 200 events.</p>
        </div>
    """, unsafe_allow_html=True)

    conn = get_db()
    cur  = conn.cursor()
    try:
        cur.execute("""
            SELECT
                sl.log_id                                              AS "Event ID",
                sl.shipment_id                                         AS "Shipment",
                sl.old_status                                          AS "Previous State",
                sl.new_status                                          AS "New State",
                sl.notes                                               AS "Notes",
                u.full_name                                            AS "Authorized By",
                TO_CHAR(sl.changed_at, 'YYYY-MM-DD HH24:MI:SS')       AS "Timestamp"
            FROM status_log sl
            JOIN users u ON sl.changed_by = u.user_id
            ORDER BY sl.changed_at DESC
            LIMIT 200
        """)
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

    # Event count badge
    st.markdown(f"""
        <span style='background:#1e293b;color:#94a3b8;border:1px solid #334155;border-radius:20px;padding:4px 14px;font-size:0.78rem;font-weight:700;margin-bottom:1rem;display:inline-block;'>
            🔐 {len(df)} Events Logged
        </span>
    """, unsafe_allow_html=True)

    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_pagination(paginationAutoPageSize=True)
    gb.configure_side_bar()
    gb.configure_grid_options(rowHeight=52, headerHeight=48, animateRows=True)
    gb.configure_column("New State",      cellStyle=STATUS_JSCODE)
    gb.configure_column("Previous State", cellStyle=STATUS_JSCODE)
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
        st.download_button("📥 Export Audit Log", data=csv, file_name="AuditLog_LogiTrack.csv", mime="text/csv", use_container_width=True)
