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
