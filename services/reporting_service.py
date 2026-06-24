from database import get_db

def fetch_executive_overview():
    """
    Fetches the high-level operational summary for the Command Center.
    Returns a dict containing total, active, delayed, and available metrics.
    """
    conn = get_db()
    cur = conn.cursor()
    
    metrics = {
        'total_orders': 0,
        'active_shipments': 0,
        'delayed_shipments': 0,
        'available_carriers': 0
    }
    
    try:
        cur.execute("SELECT COUNT(*) AS total FROM orders")
        metrics['total_orders'] = cur.fetchone()['total']
        
        cur.execute("SELECT COUNT(*) AS active FROM shipments WHERE status = 'In Transit'")
        metrics['active_shipments'] = cur.fetchone()['active']
        
        cur.execute("SELECT COUNT(*) AS delayed FROM shipments WHERE status = 'Delayed'")
        metrics['delayed_shipments'] = cur.fetchone()['delayed']
        
        cur.execute("SELECT COUNT(*) AS available FROM carriers WHERE is_available = TRUE")
        metrics['available_carriers'] = cur.fetchone()['available']
        
    except Exception as e:
        print(f"Reporting Service Error: {e}")
    finally:
        conn.close()
        
    return metrics