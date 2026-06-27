import streamlit as st
import pandas as pd
from database import get_db
from st_aggrid import AgGrid, GridOptionsBuilder, ColumnsAutoSizeMode, JsCode
from components.ui_elements import AGGRID_CSS, ID_JS, TS_JS

_STATUS_JS = JsCode("""
function(params) {
    const v = params.value || '';
    const map = {
        'Delivered':  '#34d399',
        'In Transit': '#60a5fa',
        'Delayed':    '#fb923c',
        'Cancelled':  '#f87171',
        'Pending':    '#64748b',
    };
    return {color: map[v] || '#94a3b8', fontWeight: '700', fontSize: '0.82rem'};
}
""")

_ARROW_JS = JsCode("""
function(params) {
    const old_ = params.data['Previous State'] || '—';
    const new_ = params.data['New State'] || '—';
    const colors = {
        'Delivered':'#34d399','In Transit':'#60a5fa',
        'Delayed':'#fb923c','Cancelled':'#f87171','Pending':'#64748b'
    };
    const nc = colors[new_] || '#94a3b8';
    const oc = colors[old_] || '#4a6080';
    return {
        value: old_ + ' → ' + new_,
    };
}
""")


def render_page():
    st.markdown("""
        <div style='margin-bottom:1.75rem;'>
            <div style='color:#364a65;font-size:0.65rem;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;margin-bottom:4px;'>COMPLIANCE</div>
            <h2 style='color:#f1f5f9;font-weight:800;font-size:1.65rem;margin:0;letter-spacing:-0.5px;font-family:Inter,sans-serif;'>Audit Ledger</h2>
            <p style='color:#364a65;font-size:0.85rem;margin:4px 0 0 0;'>Immutable record of all status transitions and operator authorizations.</p>
        </div>
    """, unsafe_allow_html=True)

    conn = get_db()
    cur  = conn.cursor()
    try:
        cur.execute("""
            SELECT
                sl.log_id                                              AS "Event",
                sl.shipment_id                                         AS "Ship ID",
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
        st.markdown("""
            <div style='background:#0d1526;border:1px solid #1a2744;border-radius:12px;padding:3rem;text-align:center;'>
                <div style='font-size:2rem;margin-bottom:0.75rem;'>🔐</div>
                <div style='color:#4a6080;font-size:0.9rem;font-weight:600;'>No audit events recorded yet.</div>
            </div>
        """, unsafe_allow_html=True)
        return

    df = pd.DataFrame(data)

    # Header info strip
    st.markdown(f"""
        <div style='display:flex;gap:0.5rem;margin-bottom:1rem;align-items:center;'>
            <span style='background:#1a2744;color:#64748b;border:1px solid #253355;border-radius:20px;padding:4px 14px;font-size:0.75rem;font-weight:700;'>🔐 {len(df)} Events</span>
            <span style='color:#253355;font-size:0.72rem;'>Showing last 200 transitions · Ordered by most recent</span>
        </div>
    """, unsafe_allow_html=True)

    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=15)
    gb.configure_side_bar(filters_panel=True, columns_panel=False)
    gb.configure_grid_options(rowHeight=46, headerHeight=44, animateRows=True, suppressCellFocus=True)
    gb.configure_column("Event",          cellStyle=ID_JS,     maxWidth=80,  pinned='left')
    gb.configure_column("Ship ID",        cellStyle=ID_JS,     maxWidth=90)
    gb.configure_column("New State",      cellStyle=_STATUS_JS, maxWidth=130)
    gb.configure_column("Previous State", cellStyle=_STATUS_JS, maxWidth=130)
    gb.configure_column("Timestamp",      cellStyle=TS_JS,     maxWidth=175)

    AgGrid(
        df,
        gridOptions=gb.build(),
        enable_enterprise_modules=False,
        columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS,
        theme='streamlit',
        allow_unsafe_jscode=True,
        custom_css=AGGRID_CSS,
        height=560,
    )

    st.markdown("<br>", unsafe_allow_html=True)
    c1, _, _ = st.columns([1.3, 1, 2.5])
    with c1:
        st.download_button(
            "📥 Export Audit Log",
            data=df.to_csv(index=False).encode('utf-8'),
            file_name="AuditLog_LogiTrack.csv",
            mime="text/csv",
            use_container_width=True,
        )
