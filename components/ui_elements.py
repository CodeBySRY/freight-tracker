import streamlit as st

def render_status_badge(status: str) -> str:
    """Returns the HTML for a unified status badge based on the shipment state."""
    status_map = {
        "Delivered": "badge-delivered",
        "In Transit": "badge-transit",
        "Delayed": "badge-delayed",
        "Cancelled": "badge-cancelled",
        "Pending": "badge-pending"
    }
    
    # Default to pending if status is unrecognized
    css_class = status_map.get(status, "badge-pending")
    return f"<span class='badge {css_class}'>{status}</span>"