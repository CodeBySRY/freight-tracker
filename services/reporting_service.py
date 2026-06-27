from database import get_db
import pandas as pd


def fetch_executive_overview():
    conn = get_db()
    cur = conn.cursor()
    metrics = {
        'total_orders': 0, 'active_shipments': 0, 'delayed_shipments': 0,
        'available_carriers': 0, 'orders_today': 0, 'delivered_today': 0,
        'total_carriers': 0,
    }
    try:
        cur.execute("""
            SELECT
                (SELECT COUNT(*) FROM orders)                                                              AS total_orders,
                (SELECT COUNT(*) FROM shipments WHERE status = 'In Transit')                               AS active_shipments,
                (SELECT COUNT(*) FROM shipments WHERE status = 'Delayed')                                  AS delayed_shipments,
                (SELECT COUNT(*) FROM carriers WHERE is_available = TRUE)                                  AS available_carriers,
                (SELECT COUNT(*) FROM carriers)                                                            AS total_carriers,
                (SELECT COUNT(*) FROM orders WHERE expected_delivery_date = CURRENT_DATE)                  AS orders_today,
                (SELECT COUNT(*) FROM shipments WHERE status = 'Delivered'
                    AND actual_delivery_date = CURRENT_DATE)                                               AS delivered_today
        """)
        row = cur.fetchone()
        if row:
            metrics = {
                'total_orders':       int(row['total_orders']       or 0),
                'active_shipments':   int(row['active_shipments']   or 0),
                'delayed_shipments':  int(row['delayed_shipments']  or 0),
                'available_carriers': int(row['available_carriers'] or 0),
                'total_carriers':     int(row['total_carriers']     or 0),
                'orders_today':       int(row['orders_today']       or 0),
                'delivered_today':    int(row['delivered_today']    or 0),
            }
    except Exception as e:
        print(f"Reporting Service Error: {e}")
    finally:
        conn.close()
    return metrics


def fetch_activity_feed(limit: int = 12):
    conn = get_db()
    cur = conn.cursor()
    events = []
    try:
        cur.execute("""
            SELECT sl.log_id, sl.shipment_id, sl.old_status, sl.new_status, sl.notes,
                   u.full_name AS operator, sl.changed_at,
                   o.customer_name, o.origin_city, o.destination_city
            FROM status_log sl
            JOIN users     u ON sl.changed_by  = u.user_id
            JOIN shipments s ON sl.shipment_id  = s.shipment_id
            JOIN orders    o ON s.order_id      = o.order_id
            ORDER BY sl.changed_at DESC
            LIMIT %s
        """, (limit,))
        events = cur.fetchall()
    except Exception as e:
        print(f"Activity Feed Error: {e}")
    finally:
        conn.close()
    return events


def fetch_shipment_status_distribution():
    """Returns a DataFrame with shipment status counts. Uses safe alias 'n' to avoid reserved-word collision."""
    conn = get_db()
    cur = conn.cursor()
    rows = []
    try:
        cur.execute("SELECT status, COUNT(*) AS n FROM shipments GROUP BY status ORDER BY n DESC")
        rows = cur.fetchall()
    except Exception as e:
        print(f"Status distribution error: {e}")
    finally:
        conn.close()
    if not rows:
        return pd.DataFrame(columns=['status', 'n'])
    df = pd.DataFrame(rows)
    df['n'] = pd.to_numeric(df['n'], errors='coerce').fillna(0).astype(int)
    return df


def fetch_orders_timeline():
    conn = get_db()
    cur = conn.cursor()
    rows = []
    try:
        cur.execute("""
            SELECT expected_delivery_date AS dt, COUNT(*) AS n
            FROM orders
            WHERE expected_delivery_date IS NOT NULL
            GROUP BY expected_delivery_date
            ORDER BY expected_delivery_date
        """)
        rows = cur.fetchall()
    except Exception as e:
        print(f"Orders timeline error: {e}")
    finally:
        conn.close()
    if not rows:
        return pd.DataFrame(columns=['dt', 'n'])
    return pd.DataFrame(rows)


def fetch_carrier_utilization():
    conn = get_db()
    cur = conn.cursor()
    rows = []
    try:
        cur.execute("""
            SELECT c.company_name AS carrier,
                   COUNT(s.shipment_id) AS total_shipments,
                   SUM(CASE WHEN s.status = 'Delivered'  THEN 1 ELSE 0 END) AS delivered,
                   SUM(CASE WHEN s.status = 'In Transit' THEN 1 ELSE 0 END) AS in_transit,
                   CASE WHEN c.is_available THEN 'Available' ELSE 'Dispatched' END AS current_status
            FROM carriers c
            LEFT JOIN shipments s ON c.carrier_id = s.carrier_id
            GROUP BY c.carrier_id, c.company_name, c.is_available
            ORDER BY total_shipments DESC
            LIMIT 10
        """)
        rows = cur.fetchall()
    except Exception as e:
        print(f"Carrier utilization error: {e}")
    finally:
        conn.close()
    if not rows:
        return pd.DataFrame(columns=['carrier','total_shipments','delivered','in_transit','current_status'])
    df = pd.DataFrame(rows)
    for col in ['total_shipments','delivered','in_transit']:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
    return df


def fetch_delivery_performance():
    conn = get_db()
    cur = conn.cursor()
    rows = []
    try:
        cur.execute("""
            SELECT
                CASE
                    WHEN s.status = 'Delivered' AND s.actual_delivery_date <= o.expected_delivery_date THEN 'On Time'
                    WHEN s.status = 'Delivered' AND s.actual_delivery_date >  o.expected_delivery_date THEN 'Late'
                    WHEN s.status = 'Delayed'   THEN 'Delayed'
                    WHEN s.status = 'Cancelled' THEN 'Cancelled'
                    ELSE 'In Progress'
                END AS performance,
                COUNT(*) AS n
            FROM shipments s
            JOIN orders o ON s.order_id = o.order_id
            GROUP BY 1
            ORDER BY n DESC
        """)
        rows = cur.fetchall()
    except Exception as e:
        print(f"Delivery performance error: {e}")
    finally:
        conn.close()
    if not rows:
        return pd.DataFrame(columns=['performance','n'])
    df = pd.DataFrame(rows)
    df['n'] = pd.to_numeric(df['n'], errors='coerce').fillna(0).astype(int)
    return df
