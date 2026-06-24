import streamlit as st
import pandas as pd
from database import get_db
from st_aggrid import AgGrid, GridOptionsBuilder, ColumnsAutoSizeMode, JsCode

def render_page():
    st.markdown("<h2 style='font-weight: 800; color: #f8fafc; margin-bottom: 0.5rem;'>📦 Shipment Management</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #94a3b8; font-size: 0.95rem; margin-bottom: 1.5rem;'>Monitor live freight movement, filter by status, and export dispatcher reports.</p>", unsafe_allow_html=True)
    
    # ─── 1. FETCH DATA ────────────────────────────────────────────────────
    conn = get_db()
    cur = conn.cursor()
    query = """
        SELECT 
            s.shipment_id AS "ID",
            o.customer_name AS "Client",
            o.origin_city AS "Origin",
            o.destination_city AS "Destination",
            o.priority AS "Priority",
            c.company_name AS "Carrier",
            s.status AS "Status",
            TO_CHAR(s.assigned_at, 'YYYY-MM-DD HH24:MI') AS "Assigned Time"
        FROM shipments s
        JOIN orders o ON s.order_id = o.order_id
        JOIN carriers c ON s.carrier_id = c.carrier_id
        ORDER BY s.assigned_at DESC
    """
    try:
        cur.execute(query)
        data = cur.fetchall()
    except Exception as e:
        st.error(f"Failed to fetch shipment data: {e}")
        data = []
    finally:
        conn.close()

    # ─── 2. RENDER GRID ───────────────────────────────────────────────────
    if not data:
        st.info("No active shipments found in the system.")
        return

    df = pd.DataFrame(data)
    
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_pagination(paginationAutoPageSize=True)
    gb.configure_side_bar()
    gb.configure_selection('single')
    
    # FIX 1: Use native cellStyle instead of raw HTML to prevent text leaking
    status_style_jscode = JsCode("""
    function(params) {
        if (params.value === 'Delivered') { return {'color': '#34d399', 'backgroundColor': '#064e3b', 'borderRadius': '8px', 'textAlign': 'center', 'fontWeight': '600'}; }
        if (params.value === 'In Transit') { return {'color': '#60a5fa', 'backgroundColor': '#1e3a8a', 'borderRadius': '8px', 'textAlign': 'center', 'fontWeight': '600'}; }
        if (params.value === 'Delayed') { return {'color': '#fbbf24', 'backgroundColor': '#78350f', 'borderRadius': '8px', 'textAlign': 'center', 'fontWeight': '600'}; }
        if (params.value === 'Cancelled') { return {'color': '#f87171', 'backgroundColor': '#7f1d1d', 'borderRadius': '8px', 'textAlign': 'center', 'fontWeight': '600'}; }
        return {'color': '#cbd5e1', 'backgroundColor': '#334155', 'borderRadius': '8px', 'textAlign': 'center', 'fontWeight': '600'};
    }
    """)
    gb.configure_column("Status", cellStyle=status_style_jscode)
    gridOptions = gb.build()

    # FIX 2: theme='streamlit' forces AgGrid to adopt your dark mode
    st.markdown("<div style='border: 1px solid #1e293b; border-radius: 12px; overflow: hidden; margin-bottom: 1.5rem;'>", unsafe_allow_html=True)
    response = AgGrid(
        df,
        gridOptions=gridOptions,
        enable_enterprise_modules=False,
        columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS,
        theme='streamlit', 
        height=500,
        fit_columns_on_grid_load=True,
        allow_unsafe_jscode=True
    )
    st.markdown("</div>", unsafe_allow_html=True)
    
    # ─── 3. EXPORT CAPABILITY ─────────────────────────────────────────────
    col1, col2, col3 = st.columns([1, 1, 3])
    with col1:
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Export View to CSV", data=csv, file_name="Shipments.csv", mime="text/csv", use_container_width=True)