# database.py — PostgreSQL Connection Module
# The ONLY file in the project that knows about the database.
# Every route in main.py calls get_db() to obtain a connection.

import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv

# Load environment variables from the .env file located in the project root.
# This keeps credentials (DB_PASSWORD, etc.) out of source code and version control.
# 1. Load the variables first!
load_dotenv()

# Database configuration pulled entirely from environment variables.
# Defaults are provided for local development convenience, but production
# deployments on Render.com will override these via their dashboard.
DB_CONFIG = {
    'host':     os.getenv('DB_HOST', 'localhost'),
    'database': os.getenv('DB_NAME', 'freight_db'),
    'user':     os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', ''),      # Never hardcode passwords!
    'port':     int(os.getenv('DB_PORT', 5432))
}


def get_db():
    """
    Open and return a new psycopg2 connection using RealDictCursor.

    RealDictCursor ensures every row returned by fetchone() / fetchall()
    is a Python dictionary keyed by column name, e.g.:
        {'order_id': 1, 'customer_name': 'Pak Electronics Ltd', ...}
    instead of a plain tuple like:
        (1, 'Pak Electronics Ltd', ...)

    This makes template rendering with Jinja2 straightforward:
        {{ order.customer_name }}

    IMPORTANT — Caller is responsible for:
        conn.commit()   after INSERT / UPDATE / DELETE
        conn.close()    when done (preferably in a finally block)
    """
    conn = psycopg2.connect(**DB_CONFIG, cursor_factory=RealDictCursor)
    return conn


# ---------------------------------------------------------------------------
# Usage pattern (reference for every route in main.py):
#
#   conn = get_db()
#   cur  = conn.cursor()
#   cur.execute('SELECT * FROM orders WHERE order_id = %s', (order_id,))
#   row  = cur.fetchone()    # → dict  or None
#   rows = cur.fetchall()    # → list of dicts
#   conn.commit()            # Required after INSERT / UPDATE / DELETE
#   conn.close()             # Always close!
# ---------------------------------------------------------------------------
