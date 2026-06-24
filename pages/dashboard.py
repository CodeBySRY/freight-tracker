import streamlit as st
from services.reporting_service import fetch_executive_overview

def render_page():
    st.markdown("<h2 style='font-weight: 800; color: #f8fafc; margin-bottom: 1.5rem;'>🌐 Command Center</h2>", unsafe_allow_html=True)
    
    # ─── 1. EXECUTIVE OVERVIEW ──────────────────────────────────────────
    metrics = fetch_executive_overview()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class="kpi-card" style="border-top: 4px solid #3b82f6;">
            <div class="kpi-title">Total Orders</div>
            <div class="kpi-value">{metrics.get('total_orders', 0)}</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="kpi-card" style="border-top: 4px solid #10b981;">
            <div class="kpi-title">Active (In Transit)</div>
            <div class="kpi-value">{metrics.get('active_shipments', 0)}</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="kpi-card" style="border-top: 4px solid #f59e0b;">
            <div class="kpi-title">Delayed</div>
            <div class="kpi-value">{metrics.get('delayed_shipments', 0)}</div>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
        <div class="kpi-card" style="border-top: 4px solid #8b5cf6;">
            <div class="kpi-title">Available Fleet</div>
            <div class="kpi-value">{metrics.get('available_carriers', 0)}</div>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("<br><br>", unsafe_allow_html=True)

    # ─── 2. ACTION CARDS (Contextual Workflows) ───────────────────────
    st.markdown("<h3 style='font-weight: 700; color: #f8fafc; margin-bottom: 1rem;'>⚡ Operational Workflows</h3>", unsafe_allow_html=True)
    
    ac1, ac2, ac3 = st.columns(3)
    user_role = st.session_state.user['role']
    
    with ac1:
        st.markdown("""
        <div class="feature-card" style="padding: 1.5rem;">
            <h4 style="color: #f8fafc; margin-top: 0;">📦 Draft New Order</h4>
            <p style="color: #94a3b8; font-size: 0.85rem; margin-bottom: 1rem;">Create and validate a new freight contract into the pending queue.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Initiate Draft", key="btn_draft", use_container_width=True):
            st.info("Opening contextual Draft Order workflow...")
            
    with ac2:
        if user_role in ["System Administrator", "Dispatcher"]:
            st.markdown("""
            <div class="feature-card" style="padding: 1.5rem;">
                <h4 style="color: #f8fafc; margin-top: 0;">🚚 Dispatch Fleet</h4>
                <p style="color: #94a3b8; font-size: 0.85rem; margin-bottom: 1rem;">Assign pending orders to available carriers and deploy trucks.</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Open Dispatch UI", key="btn_dispatch", use_container_width=True):
                st.info("Opening contextual Dispatch workflow...")
        else:
            st.markdown("""
            <div class="feature-card" style="padding: 1.5rem; opacity: 0.5;">
                <h4 style="color: #f8fafc; margin-top: 0;">🚚 Dispatch Fleet</h4>
                <p style="color: #94a3b8; font-size: 0.85rem; margin-bottom: 1rem;">Clearance Level Insufficient. Please contact Dispatch.</p>
            </div>
            """, unsafe_allow_html=True)
            st.button("Restricted", key="btn_dispatch_locked", disabled=True, use_container_width=True)

    with ac3:
        if user_role in ["System Administrator", "Warehouse Manager"]:
            st.markdown("""
            <div class="feature-card" style="padding: 1.5rem;">
                <h4 style="color: #f8fafc; margin-top: 0;">✅ Update Status</h4>
                <p style="color: #94a3b8; font-size: 0.85rem; margin-bottom: 1rem;">Record delivery progress, mark delays, or close out shipments.</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Update Log", key="btn_update", use_container_width=True):
                st.info("Opening contextual Status Update workflow...")
        else:
            st.markdown("""
            <div class="feature-card" style="padding: 1.5rem; opacity: 0.5;">
                <h4 style="color: #f8fafc; margin-top: 0;">✅ Update Status</h4>
                <p style="color: #94a3b8; font-size: 0.85rem; margin-bottom: 1rem;">Clearance Level Insufficient. Please contact Warehouse.</p>
            </div>
            """, unsafe_allow_html=True)
            st.button("Restricted", key="btn_update_locked", disabled=True, use_container_width=True)