import streamlit as st
from database import get_db
import datetime

# Security: Redirect to login if unauthenticated
if 'user' not in st.session_state or st.session_state.user is None:
    st.switch_page("app.py")

user = st.session_state.user

# RBAC: Only Admin and Dispatcher can create orders
if user['role'] not in ['Admin', 'Dispatcher']:
    st.error("You do not have permission to access this page.")
    st.stop()

st.title("Create New Order")
st.write("Fill out the logistics details below to dispatch a new freight order.")

# Streamlit Form ensures the page doesn't reload until the user hits submit
with st.form("new_order_form", clear_on_submit=True):
    st.subheader("Customer & Routing")
    col1, col2 = st.columns(2)
    with col1:
        customer_name = st.text_input("Customer Name *")
        origin_city = st.text_input("Origin City *")
    with col2:
        expected_delivery_date = st.date_input("Expected Delivery Date", min_value=datetime.date.today())
        destination_city = st.text_input("Destination City *")
        
    st.subheader("Cargo Details")
    cargo_description = st.text_area("General Description *")
    
    col3, col4, col5 = st.columns(3)
    with col3:
        cargo_weight_kg = st.number_input("Weight (kg)", min_value=0.0, step=50.0)
    with col4:
        cargo_type = st.selectbox(
            "Cargo Type", 
            ["General Goods", "Perishables", "Hazardous Materials", "Electronics", "Pharmaceuticals", "Raw Materials", "Machinery"]
        )
    with col5:
        priority = st.selectbox("Priority Level", ["Standard", "Express", "Critical"])
        
    special_instructions = st.text_area("Special Instructions (Optional)")
    
    st.markdown("*Required fields")
    submit = st.form_submit_button("Create Order", type="primary", use_container_width=True)

    if submit:
        # Form Validation
        if not customer_name or not origin_city or not destination_city or not cargo_description:
            st.error("Please fill in all required fields.")
        elif origin_city.strip().lower() == destination_city.strip().lower():
            st.error("Origin and destination cities cannot be the same.")
        else:
            conn = get_db()
            cur = conn.cursor()
            try:
                # Insert all data into our upgraded schema
                cur.execute("""
                    INSERT INTO orders (
                        customer_name, cargo_description, origin_city, destination_city, created_by,
                        expected_delivery_date, cargo_weight_kg, cargo_type, priority, special_instructions
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    customer_name, cargo_description, origin_city, destination_city, user['user_id'],
                    expected_delivery_date, cargo_weight_kg, cargo_type, priority, special_instructions
                ))
                conn.commit()
                st.success("Order created successfully! Navigate to the 'Orders' page to view and assign it.")
            except Exception as e:
                conn.rollback()
                st.error(f"Database error occurred: {e}")
            finally:
                conn.close()