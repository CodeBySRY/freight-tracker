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