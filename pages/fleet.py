import streamlit as st
import pandas as pd
from database import get_db
from st_aggrid import AgGrid, GridOptionsBuilder, ColumnsAutoSizeMode, JsCode
from components.ui_elements import AGGRID_CSS, ID_JS

_STATUS_JS = JsCode("""
function(params) {
    const v = params.value;
    if (v === 'Available') return {
        color:'#34d399', backgroundColor:'#022c22', border:'1px solid #065f46',
        borderRadius:'20px', textAlign:'center', fontWeight:'700',
        fontSize:'0.7rem', padding:'2px 10px', display:'inline-block'
    };
    return {
        color:'#fb923c', backgroundColor:'#431407', border:'1px solid #9a3412',
        borderRadius:'20px', textAlign:'center', fontWeight:'700',
        fontSize:'0.7rem', padding:'2px 10px', display:'inline-block'
    };
}
""")

_VTYPE_JS = JsCode("""
function(p){ return {color:'#64748b',fontStyle:'italic',fontSize:'0.82rem'}; }
""")

_PHONE_JS = JsCode("""
function(p){ return {color:'#4a6080',fontFamily:'JetBrains Mono,monospace',fontSize:'0.78rem'}; }
""")


def render_page():
    st.markdown("""
        <div style='margin-bottom:1.75rem;'>
            <div style='color:#364a65;font-size:0.65rem;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;margin-bottom:4px;'>FLEET</div>
            <h2 style='color:#f1f5f9;font-weight:800;font-size:1.65rem;margin:0;letter-spacing:-0.5px;font-family:Inter,sans-serif;'>Fleet Operations</h2>
            <p style='color:#364a65;font-size:0.85rem;margin:4px 0 0 0;'>Carrier capacity, vehicle classifications, and dispatch availability.</p>
        </div>
    """, unsafe_allow_html=True)

    conn = get_db()
    cur  = conn.cursor()
    try:
        cur.execute("""
            SELECT
                carrier_id                                                    AS "ID",
                company_name                                                  AS "Carrier",
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
        st.markdown("""
            <div style='background:#0d1526;border:1px solid #1a2744;border-radius:12px;padding:3rem;text-align:center;'>
                <div style='font-size:2rem;margin-bottom:0.75rem;'>🚛</div>
                <div style='color:#4a6080;font-size:0.9rem;font-weight:600;'>No carriers registered yet.</div>
                <div style='color:#253355;font-size:0.8rem;margin-top:0.3rem;'>Register a carrier from the Command Center to begin dispatching.</div>
            </div>
        """, unsafe_allow_html=True)
        return

    df = pd.DataFrame(data)
    total      = len(df)
    available  = len(df[df['Status'] == 'Available'])
    dispatched = total - available

    # Summary strip
    st.markdown(f"""
        <div style='display:flex;gap:0.5rem;margin-bottom:1rem;flex-wrap:wrap;'>
            <span style='background:#1a2744;color:#64748b;border:1px solid #253355;border-radius:20px;padding:4px 14px;font-size:0.75rem;font-weight:700;'>🚛 {total} Carriers</span>
            <span style='background:#022c22;color:#34d399;border:1px solid #065f4633;border-radius:20px;padding:4px 14px;font-size:0.75rem;font-weight:700;'>✅ {available} Available</span>
            <span style='background:#431407;color:#fb923c;border:1px solid #9a341233;border-radius:20px;padding:4px 14px;font-size:0.75rem;font-weight:700;'>🚚 {dispatched} Dispatched</span>
        </div>
    """, unsafe_allow_html=True)

    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=15)
    gb.configure_selection('single')
    gb.configure_grid_options(rowHeight=46, headerHeight=44, animateRows=True, suppressCellFocus=True)
    gb.configure_column("ID",           cellStyle=ID_JS,     maxWidth=70, pinned='left')
    gb.configure_column("Status",       cellStyle=_STATUS_JS, maxWidth=130)
    gb.configure_column("Vehicle Type", cellStyle=_VTYPE_JS)
    gb.configure_column("Contact",      cellStyle=_PHONE_JS)

    AgGrid(
        df,
        gridOptions=gb.build(),
        enable_enterprise_modules=False,
        columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS,
        theme='streamlit',
        allow_unsafe_jscode=True,
        custom_css=AGGRID_CSS,
        height=460,
    )
