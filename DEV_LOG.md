# FreightTracker — DEV_LOG

## Session 1 — Foundation Layer (May 9, 2026)

### What Was Built

| File | Purpose |
|---|---|
| `requirements.txt` | All Python dependencies for the project |
| `database.py` | PostgreSQL connection module |
| `auth.py` | Password hashing & verification module |

---

### Step 1: `requirements.txt`

**Libraries installed:**

| Library | Why It's Needed |
|---|---|
| `fastapi` | Web framework — handles HTTP routing, form parsing, and template rendering |
| `uvicorn` | ASGI server — runs the FastAPI application on localhost:8000 |
| `psycopg2-binary` | PostgreSQL driver — sends raw SQL from Python to the database |
| `jinja2` | Template engine — injects Python data into HTML pages server-side |
| `passlib[bcrypt]` | Password hashing — bcrypt algorithm via CryptContext |
| `python-multipart` | Required by FastAPI to parse `Form()` data from HTML form submissions |
| `starlette` | Foundation for FastAPI; provides `SessionMiddleware` for cookie-based sessions |
| `python-dotenv` | Reads `.env` file so credentials stay out of source code |

---

### Step 2: `database.py` — PostgreSQL Connection

**Why:** Every route in `main.py` needs to talk to PostgreSQL. This module centralizes that logic into a single `get_db()` function so the connection config is defined once and reused everywhere.

**How it works:**

1. `load_dotenv()` reads the `.env` file and loads `DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_PORT` into `os.environ`.
2. `DB_CONFIG` dictionary pulls each value via `os.getenv()` with safe defaults for local development.
3. `get_db()` calls `psycopg2.connect(**DB_CONFIG, cursor_factory=RealDictCursor)` and returns the connection.

**Why `RealDictCursor`?**

Standard psycopg2 returns rows as tuples: `(1, 'Pak Electronics')`. `RealDictCursor` returns them as dictionaries: `{'order_id': 1, 'customer_name': 'Pak Electronics'}`. This is critical because:
- Jinja2 templates access data by key: `{{ order.customer_name }}`
- Route handlers access data by key: `user['role']`
- It makes the code self-documenting — no need to remember column index positions

**DBMS Principles Applied:**

| Principle | How It's Applied |
|---|---|
| **Security** | Database password is loaded from `.env` via `os.getenv()` — never hardcoded in source. `.env` is listed in `.gitignore` so it never reaches GitHub. |
| **Separation of Concerns** | `database.py` is the *only* file that knows the DB credentials. `main.py` and `auth.py` don't import `psycopg2` directly. |
| **ACID — Durability** | The caller must explicitly call `conn.commit()` after writes, ensuring only intentional changes are persisted to disk. |

---

### Step 3: `auth.py` — Password Security

**Why:** Storing plaintext passwords violates basic security principles. If the database is ever compromised, all user accounts would be exposed. bcrypt hashing makes stored passwords computationally infeasible to reverse.

**How it works:**

1. `CryptContext(schemes=['bcrypt'], deprecated='auto')` creates a hashing engine.
   - `bcrypt` applies a one-way hash with an automatic random salt.
   - `deprecated='auto'` flags any old/weak hashes for automatic rehashing on next login.
2. `hash_password(password)` → takes plaintext, returns a 60-character bcrypt hash string. Called during user seeding (`/seed-users`).
3. `verify_password(plain, hashed)` → takes submitted password + stored hash, returns `True`/`False`. Called during login (`POST /login`).

**Security design decisions:**

| Decision | Rationale |
|---|---|
| bcrypt (not SHA-256, not MD5) | bcrypt is intentionally slow — ~100ms per hash — making brute-force attacks impractical. SHA-256 hashes billions per second. |
| Automatic salt | Each password gets a unique random salt embedded in the hash. Two users with the same password produce different hashes. |
| No plaintext logging | Neither function prints or logs the password. `verify_password` only returns a boolean. |
| Minimal surface area | `auth.py` exports exactly 2 functions. No user data, no database calls, no sessions — those belong in `main.py`. |

**DBMS Principles Applied:**

| Principle | How It's Applied |
|---|---|
| **Security — Confidentiality** | Passwords are hashed before `INSERT INTO users`. The `password_hash` column in the `users` table never contains plaintext. |
| **Security — Defense in Depth** | Even if an attacker reads the database, bcrypt hashes are computationally infeasible to reverse. |
| **Integrity** | `verify_password` ensures only correctly authenticated users can create sessions — protecting all downstream data operations. |

---

### Summary

The foundation layer establishes two critical invariants for the entire application:

1. **All database access flows through `get_db()`** — credentials are externalized, connections use dict-cursors, and the caller controls commit/rollback.
2. **All password operations flow through `auth.py`** — plaintext never touches the database, and the hashing algorithm (bcrypt) is industry-standard.

These modules are now ready to be imported by `main.py` as routes are built in the next session.


## Phase 6: Frontend Migration & Business Intelligence (Analytics)

### 1. The "Why" (Architectural Strategy)
The application's presentation layer was entirely migrated from a FastAPI/Jinja2 stack to **Streamlit**. 
* **UI/UX Logic:** Streamlit, as a Python-native data framework, allows for the direct injection of PostgreSQL query results into interactive dataframes and native charts without HTML/CSS overhead. This transforms the platform from a basic web form into an enterprise-grade "Command Center."
* **Analytics Logic:** Industry research (Logipulse) indicated that real-time analytics are essential for dispatchers. The Reports module was built to provide instant visibility into Carrier Performance, Overdue Deliveries, and Weekly Trends.

### 2. The "How" (Technical Execution & Security)
* **Session Management:** Replaced Starlette's `SessionMiddleware` with Streamlit's internal `st.session_state` to dictate UI rendering across the multi-page app architecture.
* **Role-Based Access Control (RBAC):** Access control is strictly enforced at the script level. For example, `4_carriers.py` and `6_users.py` begin with a hard evaluation of `st.session_state.user['role']`. If a Dispatcher or Warehouse user attempts to access these pages, execution is instantly halted via `st.stop()`.
* **ACID Transactions:** Order assignments and status updates are wrapped in `BEGIN`, `COMMIT`, and `ROLLBACK` blocks within Streamlit's `st.form_submit_button` event handlers to guarantee atomicity.

### 3. DBMS Principles & Advanced SQL Implementation
This phase heavily showcased advanced SQL querying to push computational workload to the PostgreSQL engine rather than the Python server.

**A. Advanced Aggregation & Filtering (Carrier Performance)**:  
Utilized `COUNT(*) FILTER` to calculate success rates within a single query pass, avoiding expensive sequential scans.
```sql
SELECT c.company_name, 
       COUNT(s.shipment_id) AS total_jobs, 
       COUNT(*) FILTER (WHERE s.status = 'Delivered') AS delivered, 
       COUNT(*) FILTER (WHERE s.status = 'Cancelled') AS cancelled 
FROM carriers c 
LEFT JOIN shipments s ON c.carrier_id = s.carrier_id 
GROUP BY c.company_name 
ORDER BY delivered DESC;
```

**B. Time-Series Grouping (Weekly Deliveries)**:  
Utilized PostgreSQL's DATE_TRUNC to group continuous timestamp data into discrete 7-day buckets for trend analysis.
```sql
SELECT DATE_TRUNC('week', delivered_at)::DATE AS week, 
       COUNT(*) AS deliveries 
FROM shipments 
WHERE status = 'Delivered' AND delivered_at >= NOW() - INTERVAL '28 days' 
GROUP BY DATE_TRUNC('week', delivered_at) 
ORDER BY week;
```

**C. Computed Columns & Date Math (Overdue Orders)**:  
Calculated days overdue dynamically (CURRENT_DATE - expected_delivery_date). A LEFT JOIN was critical here to identify orders that are overdue before they have even been assigned a carrier (s.status IS NULL).
```sql
SELECT o.order_id, o.customer_name, o.expected_delivery_date, 
       CURRENT_DATE - o.expected_delivery_date AS days_overdue 
FROM orders o 
LEFT JOIN shipments s ON o.order_id = s.order_id 
WHERE o.expected_delivery_date < CURRENT_DATE 
  AND (s.status IS NULL OR s.status NOT IN ('Delivered','Cancelled')) 
ORDER BY days_overdue DESC;
```

**D. Relational View (Active Shipments)**:  
Concatenated origin and destination for UI display while filtering strictly for in-transit logistics.
```sql
SELECT o.customer_name, o.origin_city || ' → ' || o.destination_city AS route, 
       c.company_name AS carrier, o.expected_delivery_date 
FROM shipments s 
JOIN orders o ON s.order_id = o.order_id 
JOIN carriers c ON s.carrier_id = c.carrier_id 
WHERE s.status = 'In Transit';
```


