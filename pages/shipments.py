import streamlit as st
import pandas as pd
from database import get_db
from components.ui_elements import render_status_badge
from st_aggrid import AgGrid, GridOptionsBuilder, ColumnsAutoSizeMode

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
    
    # Configure AG Grid Options
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_pagination(paginationAutoPageSize=True) # Add pagination
    gb.configure_side_bar() # Add sidebar for advanced filtering
    gb.configure_selection('single')
    
    # Custom rendering for the Status column to use our Badges
    gb.configure_column(
        "Status",
        cellRenderer=st.components.v1.html(
            """
            function(params) {
                const statusMap = {
                    'Delivered': 'badge-delivered',
                    'In Transit': 'badge-transit',
                    'Delayed': 'badge-delayed',
                    'Cancelled': 'badge-cancelled',
                    'Pending': 'badge-pending'
                };
                const cssClass = statusMap[params.value] || 'badge-pending';
                return `<span class='badge ${cssClass}'>${params.value}</span>`;
            }
            """,
            height=0
        )
    )

    gridOptions = gb.build()

    # Render the Grid
    st.markdown("<div style='border: 1px solid #1e293b; border-radius: 12px; overflow: hidden; margin-bottom: 1.5rem;'>", unsafe_allow_html=True)
    response = AgGrid(
        df,
        gridOptions=gridOptions,
        enable_enterprise_modules=False,
        columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS,
        theme='alpine', # A clean, modern theme
        height=500,
        fit_columns_on_grid_load=True
    )
    st.markdown("</div>", unsafe_allow_html=True)
    
    # ─── 3. EXPORT CAPABILITY ─────────────────────────────────────────────
    st.markdown("<hr style='border-color: #1e293b; margin: 1.5rem 0;'>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1, 3])
    with col1:
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Export View to CSV",
            data=csv,
            file_name="LogiTrack_Shipments_Export.csv",
            mime="text/csv",
            use_container_width=True
        )