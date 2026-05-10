import streamlit as st
import pandas as pd
from database import get_db

# Security & RBAC: Redirect if not logged in OR if not an Admin
if 'user' not in st.session_state or st.session_state.user is None:
    st.switch_page("app.py")

user = st.session_state.user
if user['role'] != 'Admin':
    st.error("Access Denied. Only Administrators can manage the carrier fleet.")
    st.stop() # Halts execution of the rest of the page

st.title("Fleet & Carrier Management")
st.write("Register new logistics partners and manage fleet availability.")

conn = get_db()
cur = conn.cursor()

# --- 1. Register New Carrier Form ---
with st.expander("➕ Register New Carrier", expanded=False):
    with st.form("new_carrier_form", clear_on_submit=True):
        st.subheader("Carrier Details")
        company_name = st.text_input("Company Name *")
        vehicle_type = st.selectbox(
            "Primary Vehicle Type", 
            ["Heavy Truck", "Pickup Van", "Container Truck", "Air Cargo", "Train/Rail"]
        )
        contact_phone = st.text_input("Contact Phone")
        
        submit_carrier = st.form_submit_button("Register Carrier", type="primary")

        if submit_carrier:
            if company_name.strip():
                try:
                    cur.execute(
                        "INSERT INTO carriers (company_name, vehicle_type, contact_phone, is_available) VALUES (%s, %s, %s, TRUE)",
                        (company_name, vehicle_type, contact_phone)
                    )
                    conn.commit()
                    st.success(f"{company_name} registered successfully!")
                    st.rerun() # Refresh page to show the new data
                except Exception as e:
                    conn.rollback()
                    st.error(f"Database error: {e}")
            else:
                st.error("Company name is required.")

st.divider()

# --- 2. Carrier Registry & Availability Toggle ---
st.subheader("Registered Carriers")

cur.execute("SELECT carrier_id, company_name, vehicle_type, contact_phone, is_available FROM carriers ORDER BY company_name")
carriers = cur.fetchall()

if carriers:
    # Render the data elegantly using a Pandas DataFrame
    df = pd.DataFrame(carriers)
    # Rename columns for a clean UI presentation
    df.columns = ['ID', 'Company Name', 'Vehicle Type', 'Contact Phone', 'Is Available']
    st.dataframe(df, hide_index=True, use_container_width=True)

    st.markdown("#### Quick Actions: Toggle Availability")
    st.caption("Marking a carrier as 'Unavailable' removes them from the Dispatcher's assignment dropdown.")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        # A dropdown to select which carrier to modify
        carrier_to_toggle = st.selectbox(
            "Select a Carrier to update",
            options=carriers,
            format_func=lambda c: f"[{'✅ Active' if c['is_available'] else '❌ Inactive'}] {c['company_name']}"
        )
    with col2:
        st.write("") # Vertical alignment spacing
        st.write("")
        if st.button("Toggle Status", use_container_width=True):
            new_status = not carrier_to_toggle['is_available']
            cur.execute(
                "UPDATE carriers SET is_available = %s WHERE carrier_id = %s",
                (new_status, carrier_to_toggle['carrier_id'])
            )
            conn.commit()
            st.rerun() # Refresh to update the table and dropdown instantly
else:
    st.info("No carriers registered in the system.")

conn.close()