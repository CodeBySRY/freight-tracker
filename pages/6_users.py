import streamlit as st
import pandas as pd
from database import get_db
from auth import hash_password

# Security & RBAC: ONLY Admins can manage personnel
if 'user' not in st.session_state or st.session_state.user is None:
    st.switch_page("app.py")

user = st.session_state.user
if user['role'] != 'Admin':
    st.error("Security Violation: Only Administrators can access the User Management console.")
    st.stop()

st.title("👥 User Management")
st.write("Onboard new employees and manage system access credentials.")

conn = get_db()
cur = conn.cursor()

# --- 1. Add New User Form ---
with st.expander("➕ Onboard New Employee", expanded=False):
    with st.form("new_user_form", clear_on_submit=True):
        st.subheader("Employee Details")
        col1, col2 = st.columns(2)
        with col1:
            full_name = st.text_input("Full Name *")
            email = st.text_input("Email Address *")
        with col2:
            role = st.selectbox("System Role", ["Dispatcher", "Warehouse", "Admin"])
            # Generate a default password prompt
            st.info("Default password for new users will be set to: **welcome123**")
            
        submit_user = st.form_submit_button("Create Account", type="primary")

        if submit_user:
            if full_name.strip() and email.strip():
                # DBMS Principle: Never store plaintext passwords
                hashed_pw = hash_password("welcome123")
                try:
                    cur.execute(
                        "INSERT INTO users (full_name, email, password_hash, role, is_active) VALUES (%s, %s, %s, %s, TRUE)",
                        (full_name, email, hashed_pw, role)
                    )
                    conn.commit()
                    st.success(f"Account created for {full_name}. They can now log in.")
                    st.rerun()
                except Exception as e:
                    conn.rollback()
                    # Catch duplicate email errors (UNIQUE constraint)
                    if "unique constraint" in str(e).lower():
                        st.error("An account with this email already exists.")
                    else:
                        st.error(f"Database error: {e}")
            else:
                st.error("Name and Email are required.")

st.divider()

# --- 2. Personnel Directory & Soft Deletion ---
st.subheader("Personnel Directory")
st.caption("Deactivating a user removes their login access immediately, but preserves their historical logs in the database (Soft Delete).")

# Fetch all users except the currently logged-in admin (prevents self-lockout)
cur.execute("""
    SELECT user_id, full_name, email, role, is_active, created_at::DATE 
    FROM users 
    WHERE user_id != %s
    ORDER BY created_at DESC
""", (user['user_id'],))
users_data = cur.fetchall()

if users_data:
    df_users = pd.DataFrame(users_data)
    df_users.columns = ['ID', 'Full Name', 'Email', 'Role', 'Account Active', 'Date Joined']
    
    st.dataframe(
        df_users, 
        hide_index=True, 
        use_container_width=True,
        column_config={
            "Account Active": st.column_config.CheckboxColumn(help="Uncheck to lock account")
        }
    )

    st.markdown("#### Access Control")
    col3, col4 = st.columns([3, 1])
    with col3:
        user_to_toggle = st.selectbox(
            "Select an employee to modify access",
            options=users_data,
            format_func=lambda u: f"[{'✅ Active' if u['is_active'] else '🔒 Locked'}] {u['full_name']} ({u['role']})"
        )
    with col4:
        st.write("")
        st.write("")
        if st.button("Toggle Access", use_container_width=True):
            new_status = not user_to_toggle['is_active']
            cur.execute(
                "UPDATE users SET is_active = %s WHERE user_id = %s",
                (new_status, user_to_toggle['user_id'])
            )
            conn.commit()
            st.rerun()
else:
    st.info("You are the only user in the system.")

conn.close()