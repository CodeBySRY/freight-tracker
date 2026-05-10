# app.py
import streamlit as st
from database import get_db
from auth import verify_password

# Must be the very first Streamlit command
st.set_page_config(page_title="LogiTrack PK", layout="wide", initial_sidebar_state="expanded")

# Initialize Session State
if 'user' not in st.session_state:
    st.session_state.user = None

def login_screen():
    # Centered Login UI
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("LogiTrack PK")
        st.caption("Freight Order & Shipment Tracking System")
        
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Sign In", use_container_width=True)
            
        if submit:
            conn = get_db()
            cur = conn.cursor()
            # Fetch user, ensuring they are active
            cur.execute("SELECT * FROM users WHERE email=%s AND is_active=TRUE", (email,))
            user = cur.fetchone()
            conn.close()
            
            if user and verify_password(password, user['password_hash']):
                st.session_state.user = {
                    'user_id': user['user_id'],
                    'full_name': user['full_name'],
                    'role': user['role']
                }
                st.rerun()
            else:
                st.error("Invalid email, password, or account deactivated.")

# Routing Logic
if not st.session_state.user:
    login_screen()
else:
    # Build the persistent sidebar for authenticated users
    st.sidebar.title("LogiTrack PK")
    st.sidebar.write(f"**{st.session_state.user['full_name']}**")
    st.sidebar.caption(f"Role: {st.session_state.user['role']}")
    
    st.sidebar.divider()
    
    if st.sidebar.button("Logout", use_container_width=True):
        st.session_state.user = None
        st.rerun()
        
    # Inform the user to build the pages
    st.info("Authentication successful. Streamlit will auto-populate the sidebar once the `pages/` directory is created.")