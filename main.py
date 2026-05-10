# main.py — Application Entry Point & All Routes
# FastAPI serves both HTML pages (via Jinja2) and processes form submissions.
# There is no separate API server — this single file is the entire backend.

from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from database import get_db
from auth import hash_password, verify_password
import secrets

# ─── App Initialization ───────────────────────────────────────────────
app = FastAPI(title='Freight Order & Shipment Tracking System')

# ─── Session Middleware ────────────────────────────────────────────────
# Signs the session cookie with a cryptographically random key.
# This prevents session tampering — if a user modifies the cookie,
# the signature check fails and the session is invalidated.
app.add_middleware(SessionMiddleware, secret_key=secrets.token_hex(32))

# ─── Static Files ─────────────────────────────────────────────────────
# Mount the static/ directory so CSS is served at /static/style.css
app.mount('/static', StaticFiles(directory='static'), name='static')

# ─── Jinja2 Templates ─────────────────────────────────────────────────
# Point FastAPI to the templates/ folder for HTML rendering
templates = Jinja2Templates(directory='templates')


# ─── Helper: Get Current User from Session ─────────────────────────────
def get_current_user(request: Request):
    """
    Retrieve the authenticated user dict from the session cookie.

    Returns a dict like {'user_id': 1, 'full_name': 'Admin', 'role': 'Admin'}
    or None if no user is logged in.

    Called at the top of every protected route to enforce authentication.
    """
    return request.session.get('user')  # Returns dict or None


# ═══════════════════════════════════════════════════════════════════════
#  ROUTES
# ═══════════════════════════════════════════════════════════════════════

# ─── Login Page (GET) ──────────────────────────────────────────────────
@app.get('/login', response_class=HTMLResponse)
async def login_page(request: Request):
    """Render the login form. Public — no authentication required."""
    return templates.TemplateResponse(
        name='login.html',
        request=request,
        context={'error': None}
    )


# ─── Root Redirect ────────────────────────────────────────────────────
@app.get('/')
async def root():
    """Redirect the bare domain to the login page."""
    return RedirectResponse('/login')

# ─── Login (POST) ─────────────────────────────────────────────────────
@app.post('/login')
async def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...)
):
    """
    Process the login form submission.

    Steps:
      1. Query the users table for a record matching the submitted email.
      2. If no user found, or password doesn't match the stored hash,
         re-render the login page with a generic error message.
         (Same message for both cases — prevents user enumeration.)
      3. If valid, store user_id, full_name, and role in the session,
         then redirect to /dashboard.
    """
    conn = get_db()
    cur  = conn.cursor()

    cur.execute(
        'SELECT * FROM users WHERE email = %s',
        (email,)
    )
    user = cur.fetchone()   # Returns a dict via RealDictCursor, or None
    conn.close()

    # Validate: user must exist AND password must match the bcrypt hash
    if not user or not verify_password(password, user['password_hash']):
        return templates.TemplateResponse(
            name='login.html',
            request=request,
            context={'error': 'Invalid email or password'}
        )

    # Store only the minimum needed in the session — never the hash
    request.session['user'] = {
        'user_id':   user['user_id'],
        'full_name': user['full_name'],
        'role':      user['role']
    }

    # 303 See Other is the correct redirect code after a POST
    return RedirectResponse('/dashboard', status_code=303)

@app.get('/seed-users')
async def seed_users():
    """One-time route to seed the database with initial users."""
    conn = get_db()
    cur = conn.cursor()
    
    # Check if users already exist to avoid duplicates
    cur.execute("SELECT COUNT(*) FROM users")
    if cur.fetchone()['count'] > 0:
        conn.close()
        return {"message": "Database already seeded."}

    # Roles and initial passwords [cite: 1610-1612]
    users_to_seed = [
        ('Admin User', 'admin@freight.com', 'Admin'),
        ('Dispatcher User', 'dispatcher@freight.com', 'Dispatcher'),
        ('Warehouse User', 'warehouse@freight.com', 'Warehouse')
    ]

    for name, email, role in users_to_seed:
        hashed = hash_password('password123') # Default password for testing
        cur.execute(
            "INSERT INTO users (full_name, email, password_hash, role) VALUES (%s, %s, %s, %s)",
            (name, email, hashed, role)
        )
    
    conn.commit()
    conn.close()
    return {"message": "Users seeded successfully. Use 'password123' to login."}

@app.get('/dashboard', response_class=HTMLResponse)
async def dashboard(request: Request):
    user = get_current_user(request)
    if not user:
        return RedirectResponse('/login')

    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) AS total FROM orders")
    total_orders = cur.fetchone()['total']

    cur.execute("SELECT COUNT(*) AS total FROM shipments WHERE status = 'In Transit'")
    active_shipments = cur.fetchone()['total']

    cur.execute("SELECT COUNT(*) AS total FROM shipments WHERE status = 'Delivered' AND delivered_at > NOW() - INTERVAL '7 days'")
    delivered_this_week = cur.fetchone()['total']

    cur.execute("""
        SELECT COUNT(*) AS total FROM orders o 
        LEFT JOIN shipments s ON o.order_id = s.order_id 
        WHERE s.shipment_id IS NULL
    """)
    unassigned_orders = cur.fetchone()['total']
    
    conn.close()

    # FIX: Use keyword arguments to ensure the dictionary is treated as context
    return templates.TemplateResponse(
        request=request, 
        name="dashboard.html", 
        context={
            "user": user,
            "total_orders": total_orders,
            "active_shipments": active_shipments,
            "delivered_this_week": delivered_this_week,
            "unassigned_orders": unassigned_orders
        }
    )

@app.get('/logout')
async def logout(request: Request):
    request.session.clear() # Clear the session cookie [cite: 724, 734]
    return RedirectResponse('/login')

# ─── Orders List (GET) ────────────────────────────────────────────────
@app.get('/orders', response_class=HTMLResponse)
async def orders_list(request: Request):
    user = get_current_user(request)
    if not user: return RedirectResponse('/login')

    conn = get_db()
    cur = conn.cursor()
    # DBMS Showcase: LEFT JOIN to pull order, shipment, and carrier data in one query
    cur.execute("""
        SELECT o.order_id, o.customer_name, o.origin_city, o.destination_city, 
               s.status, c.company_name AS carrier_name, s.shipment_id
        FROM orders o
        LEFT JOIN shipments s ON o.order_id = s.order_id
        LEFT JOIN carriers c ON s.carrier_id = c.carrier_id
        ORDER BY o.created_at DESC
    """)
    orders = cur.fetchall()
    conn.close()
    
    return templates.TemplateResponse(
        request=request, 
        name="orders.html", 
        context={"user": user, "orders": orders}
    )

# ─── New Order Form (GET) ──────────────────────────────────────────────
@app.get('/orders/new', response_class=HTMLResponse)
async def new_order_form(request: Request):
    user = get_current_user(request)
    # RBAC Security: Only Admin and Dispatcher can create orders
    if not user or user['role'] not in ['Admin', 'Dispatcher']:
        return RedirectResponse('/dashboard')
        
    return templates.TemplateResponse(
        request=request, 
        name="new_order.html", 
        context={"user": user}
    )

# ─── Create Order (POST) ──────────────────────────────────────────────
@app.post('/orders/new')
async def create_order(
    request: Request,
    customer_name: str = Form(...),
    cargo_description: str = Form(...),
    origin_city: str = Form(...),
    destination_city: str = Form(...)
):
    user = get_current_user(request)
    if not user or user['role'] not in ['Admin', 'Dispatcher']:
        return RedirectResponse('/login')

    # Server-side Validation [cite: 820-823]
    if origin_city.strip().lower() == destination_city.strip().lower():
        return templates.TemplateResponse(
            request=request, 
            name="new_order.html", 
            context={"user": user, "error": "Origin and destination must differ"}
        )

    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO orders (customer_name, cargo_description, origin_city, destination_city, created_by) VALUES (%s, %s, %s, %s, %s)",
        (customer_name, cargo_description, origin_city, destination_city, user['user_id'])
    )
    conn.commit()
    conn.close()
    
    return RedirectResponse('/orders', status_code=303)

# ─── Assign Carrier Form (GET) ─────────────────────────────────────────
@app.get('/orders/{order_id}/assign', response_class=HTMLResponse)
async def assign_carrier_form(request: Request, order_id: int):
    user = get_current_user(request)
    if not user or user['role'] == 'Warehouse':
        return RedirectResponse('/orders')

    conn = get_db()
    cur = conn.cursor()
    
    # Fetch the order details
    cur.execute("SELECT * FROM orders WHERE order_id = %s", (order_id,))
    order = cur.fetchone()
    
    # Fetch ONLY available carriers
    cur.execute("SELECT * FROM carriers WHERE is_available = TRUE")
    available_carriers = cur.fetchall()
    
    conn.close()
    
    if not order:
        return RedirectResponse('/orders')
        
    return templates.TemplateResponse(
        request=request, 
        name="assign_carrier.html", 
        context={"user": user, "order": order, "carriers": available_carriers}
    )

# ─── Process Assignment Transaction (POST) ────────────────────────────
@app.post('/orders/{order_id}/assign')
async def process_assignment(request: Request, order_id: int, carrier_id: int = Form(...)):
    user = get_current_user(request)
    if not user or user['role'] == 'Warehouse':
        return RedirectResponse('/orders')

    conn = get_db()
    cur = conn.cursor()
    
    try:
        # 1. BEGIN ACID TRANSACTION
        cur.execute("BEGIN")
        
        # 2. Insert into Shipments (Assigning the carrier to the order)
        cur.execute("""
            INSERT INTO shipments (order_id, carrier_id, status, assigned_at) 
            VALUES (%s, %s, 'Pending', CURRENT_TIMESTAMP) 
            RETURNING shipment_id
        """, (order_id, carrier_id))
        shipment_id = cur.fetchone()['shipment_id']
        
        # NOTE: Removed the 'is_available = FALSE' update. 
        # Carriers are now treated as fleets and can take infinite orders.
        
        # 3. Insert Audit Log (Crucial for DBMS History)
        cur.execute("""
            INSERT INTO status_log (shipment_id, old_status, new_status, changed_by) 
            VALUES (%s, NULL, 'Pending', %s)
        """, (shipment_id, user['user_id']))
        
        # 4. COMMIT (Save everything if no errors occurred)
        cur.execute("COMMIT")
        
    except Exception as e:
        # ROLLBACK (Undo everything if ANY step failed)
        cur.execute("ROLLBACK")
        print(f"Transaction Failed: {e}")
    finally:
        conn.close()

    return RedirectResponse('/orders', status_code=303)

# ─── Update Shipment Status (POST) ────────────────────────────────────
@app.post('/shipments/{shipment_id}/status')
async def update_status(request: Request, shipment_id: int, new_status: str = Form(...)):
    user = get_current_user(request)
    if not user:
        return RedirectResponse('/login')

    # State Machine Validation 
    valid_statuses = ['Pending', 'In Transit', 'Delivered', 'Cancelled']
    if new_status not in valid_statuses:
        return RedirectResponse('/orders')

    conn = get_db()
    cur = conn.cursor()
    
    try:
        cur.execute("BEGIN")
        
        # Get current status to log the change
        cur.execute("SELECT status FROM shipments WHERE shipment_id = %s", (shipment_id,))
        shipment = cur.fetchone()
        if not shipment:
            raise Exception("Shipment not found")
            
        old_status = shipment['status']
        
        # Only update if the status is actually changing
        if old_status != new_status:
            # Update the shipment
            cur.execute(
                "UPDATE shipments SET status = %s WHERE shipment_id = %s", 
                (new_status, shipment_id)
            )
            
            # If delivered, record the timestamp
            if new_status == 'Delivered':
                cur.execute(
                    "UPDATE shipments SET delivered_at = CURRENT_TIMESTAMP WHERE shipment_id = %s",
                    (shipment_id,)
                )
                
            # Insert into Audit Log
            cur.execute("""
                INSERT INTO status_log (shipment_id, old_status, new_status, changed_by) 
                VALUES (%s, %s, %s, %s)
            """, (shipment_id, old_status, new_status, user['user_id']))
            
        cur.execute("COMMIT")
    except Exception as e:
        cur.execute("ROLLBACK")
        print(f"Status Update Failed: {e}")
    finally:
        conn.close()

    return RedirectResponse('/orders', status_code=303)

# ─── View Shipment Audit History (GET) ────────────────────────────────
@app.get('/shipments/{shipment_id}/history', response_class=HTMLResponse)
async def shipment_history(request: Request, shipment_id: int):
    user = get_current_user(request)
    if not user:
        return RedirectResponse('/login')

    conn = get_db()
    cur = conn.cursor()
    
    # 1. Fetch Shipment Context
    cur.execute("""
        SELECT o.order_id, o.customer_name, s.status, c.company_name
        FROM shipments s
        JOIN orders o ON s.order_id = o.order_id
        JOIN carriers c ON s.carrier_id = c.carrier_id
        WHERE s.shipment_id = %s
    """, (shipment_id,))
    shipment_info = cur.fetchone()
    
    # 2. Fetch the Audit Log Timeline
    cur.execute("""
        SELECT sl.old_status, sl.new_status, sl.changed_at, u.full_name as changed_by
        FROM status_log sl
        JOIN users u ON sl.changed_by = u.user_id
        WHERE sl.shipment_id = %s
        ORDER BY sl.changed_at DESC
    """, (shipment_id,))
    logs = cur.fetchall()
    conn.close()

    if not shipment_info:
        return RedirectResponse('/orders')

    return templates.TemplateResponse(
        request=request, 
        name="history.html", 
        context={"user": user, "shipment": shipment_info, "logs": logs}
    )