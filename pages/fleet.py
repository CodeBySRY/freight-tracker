import streamlit as st
import pandas as pd
from database import get_db
from st_aggrid import AgGrid, GridOptionsBuilder, ColumnsAutoSizeMode, JsCode

def render_page():
    st.markdown("<h2 style='font-weight: 800; color: #f8fafc; margin-bottom: 0.5rem;'>🏢 Fleet Operations</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #94a3b8; font-size: 0.95rem; margin-bottom: 1.5rem;'>Manage carrier capacity, vehicle types, and dispatch availability.</p>", unsafe_allow_html=True)
    
    conn = get_db()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT 
                carrier_id AS "Carrier ID",
                company_name AS "Company",
                contact_phone AS "Dispatch Contact",
                vehicle_type AS "Classification",
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
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_pagination(paginationAutoPageSize=True)
    gb.configure_selection('single')
    
    # Custom color logic for availability
    availability_jscode = JsCode("""
    function(params) {
        if (params.value === 'Available') { return {'color': '#34d399', 'backgroundColor': '#022c22', 'borderRadius': '8px', 'textAlign': 'center', 'fontWeight': '600'}; }
        return {'color': '#cbd5e1', 'backgroundColor': '#334155', 'borderRadius': '8px', 'textAlign': 'center', 'fontWeight': '600'};
    }
    """)
    gb.configure_column("Status", cellStyle=availability_jscode)
    
    gridOptions = gb.build()

    st.markdown("<div style='border: 1px solid #1e293b; border-radius: 12px; overflow: hidden; margin-bottom: 1.5rem;'>", unsafe_allow_html=True)
    AgGrid(df, gridOptions=gridOptions, enable_enterprise_modules=False, columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS, theme='streamlit', allow_unsafe_jscode=True)
    st.markdown("</div>", unsafe_allow_html=True)