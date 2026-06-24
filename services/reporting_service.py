from database import get_db
import pandas as pd

def fetch_executive_overview():
    """
    Fetches the high-level operational summary for the Command Center.
    Returns a dict containing total, active, delayed, available metrics,
    plus today's order and delivery counts.
    """
    conn = get_db()
    cur = conn.cursor()

    metrics = {
        'total_orders': 0,
        'active_shipments': 0,
        'delayed_shipments': 0,
        'available_carriers': 0,
        'orders_today': 0,
        'delivered_today': 0,
        'total_carriers': 0,
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

        cur.execute("SELECT COUNT(*) AS total FROM carriers")
        metrics['total_carriers'] = cur.fetchone()['total']

        # Orders created today (using expected_delivery_date as proxy since no created_at on orders)
        cur.execute("SELECT COUNT(*) AS cnt FROM orders WHERE expected_delivery_date = CURRENT_DATE")
        metrics['orders_today'] = cur.fetchone()['cnt']

        cur.execute("SELECT COUNT(*) AS cnt FROM shipments WHERE status = 'Delivered' AND actual_delivery_date = CURRENT_DATE")
        metrics['delivered_today'] = cur.fetchone()['cnt']

    except Exception as e:
        print(f"Reporting Service Error: {e}")
    finally:
        conn.close()

    return metrics


def fetch_activity_feed(limit: int = 12):
    """
    Fetches the most recent status transitions for the live activity feed.
    Returns a list of dicts with event details.
    """
    conn = get_db()
    cur = conn.cursor()
    events = []
    try:
        cur.execute("""
            SELECT
                sl.log_id,
                sl.shipment_id,
                sl.old_status,
                sl.new_status,
                sl.notes,
                u.full_name AS operator,
                sl.changed_at,
                o.customer_name,
                o.origin_city,
                o.destination_city
            FROM status_log sl
            JOIN users u ON sl.changed_by = u.user_id
            JOIN shipments s ON sl.shipment_id = s.shipment_id
            JOIN orders o ON s.order_id = o.order_id
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
    """Returns a DataFrame with shipment status counts."""
    conn = get_db()
    try:
        df = pd.read_sql(
            "SELECT status, COUNT(*) AS count FROM shipments GROUP BY status ORDER BY count DESC",
            conn
        )
    except Exception:
        df = pd.DataFrame()
    finally:
        conn.close()
    return df


def fetch_orders_timeline():
    """Returns a DataFrame with order volume by expected delivery date."""
    conn = get_db()
    try:
        df = pd.read_sql(
            """
            SELECT expected_delivery_date AS date, COUNT(*) AS orders
            FROM orders
            WHERE expected_delivery_date IS NOT NULL
            GROUP BY expected_delivery_date
            ORDER BY expected_delivery_date
            """,
            conn
        )
    except Exception:
        df = pd.DataFrame()
    finally:
        conn.close()
    return df


def fetch_carrier_utilization():
    """Returns carrier utilization data (deliveries completed + current status)."""
    conn = get_db()
    try:
        df = pd.read_sql(
            """
            SELECT
                c.company_name AS carrier,
                COUNT(s.shipment_id) AS total_shipments,
                SUM(CASE WHEN s.status = 'Delivered' THEN 1 ELSE 0 END) AS delivered,
                SUM(CASE WHEN s.status = 'In Transit' THEN 1 ELSE 0 END) AS in_transit,
                CASE WHEN c.is_available THEN 'Available' ELSE 'Dispatched' END AS current_status
            FROM carriers c
            LEFT JOIN shipments s ON c.carrier_id = s.carrier_id
            GROUP BY c.carrier_id, c.company_name, c.is_available
            ORDER BY total_shipments DESC
            LIMIT 10
            """,
            conn
        )
    except Exception:
        df = pd.DataFrame()
    finally:
        conn.close()
    return df


def fetch_delivery_performance():
    """Returns on-time vs delayed delivery counts."""
    conn = get_db()
    try:
        df = pd.read_sql(
            """
            SELECT
                CASE
                    WHEN s.status = 'Delivered' AND s.actual_delivery_date <= o.expected_delivery_date THEN 'On Time'
                    WHEN s.status = 'Delivered' AND s.actual_delivery_date > o.expected_delivery_date THEN 'Late'
                    WHEN s.status = 'Delayed' THEN 'Delayed'
                    WHEN s.status = 'Cancelled' THEN 'Cancelled'
                    ELSE 'In Progress'
                END AS performance,
                COUNT(*) AS count
            FROM shipments s
            JOIN orders o ON s.order_id = o.order_id
            GROUP BY 1
            ORDER BY count DESC
            """,
            conn
        )
    except Exception:
        df = pd.DataFrame()
    finally:
        conn.close()
    return df
