# LogiTrack PK - System Architecture & Database Integration

## 1. Architectural Paradigm
LogiTrack PK utilizes a modern, decoupled **Three-Tier Architecture** that strictly separates data storage from application logic. This approach ensures high security, scalability, and maintainability.

The core philosophy of our implementation is the separation of **Data Definition (Schema)** from **Data Manipulation (Operations)**.

---

## 2. The Database Layer (Foundation & Schema)
The base of the DBMS is written in raw SQL. This is the **DDL (Data Definition Language)** layer. 

We used administrative tools (like pgAdmin 4 or the Render Cloud CLI) to execute these scripts. This lays the physical concrete of our database. Once executed, we rarely touch this layer again unless the architecture fundamentally changes.

### Example: DDL Execution (Defining the Foundation)
Here is the exact SQL script executed in pgAdmin to create our `users` table. Notice how it defines strict rules (`UNIQUE`, `NOT NULL`, `DEFAULT`) at the storage level:

```sql
-- Executed directly in pgAdmin
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    full_name VARCHAR(100),
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);
```

## 3. The Application Layer (Python, Streamlit & psycopg2)  
While the database dictates how data is structured, the Python backend determines when and what data moves. The actual execution of daily queries is wrapped entirely within our Python codebase using the psycopg2 driver.

This layer handles all **DML (Data Manipulation Language)**.

### 3.1 Establishing the Bridge (database.py)
Before any query can be run, the Python application must securely bridge the gap to the PostgreSQL server. We abstracted this into a reusable connection function.
```python
# From database.py
import psycopg2
from psycopg2.extras import RealDictCursor

def get_db():
    """Establishes a secure connection to the PostgreSQL database."""
    conn = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        port=DB_PORT,
        cursor_factory=RealDictCursor # Returns rows as dictionaries for easier frontend parsing
    )
    return conn
```
### 3.2 Dynamic Data Fetching (The SELECT Wrapper)
When a user attempts to log in via the Streamlit frontend, the Python wrapper dynamically constructs a query, checks the database, and enforces business logic.  
```python
# From app.py (Authentication Logic)
# 1. Open the connection
conn = get_db()
cur = conn.cursor()

# 2. Execute the query using the %s parameter for the email
cur.execute("SELECT * FROM users WHERE email=%s AND is_active=TRUE", (email,))

# 3. Fetch the result
user = cur.fetchone()

# 4. Close the connection to free up server memory
conn.close()

# 5. Application layer handles the security logic (Bcrypt comparison)
if user and verify_password(password, user['password_hash']):
    # Grant access
```

### 3.3 Transaction Management (The INSERT / UPDATE Wrapper)
When modifying data (e.g., creating a new shipment or updating a status), our Python wrapper utilizes explicit transaction management. If an error occurs midway through a complex operation, the transaction is rolled back, preventing corrupted data.
```python
# Conceptual Example: Updating a Shipment Status
def update_shipment_status(shipment_id, new_status, user_id):
    conn = get_db()
    cur = conn.cursor()
    
    try:
        # Step 1: Update the actual shipment record
        cur.execute("""
            UPDATE shipments 
            SET status = %s 
            WHERE shipment_id = %s
        """, (new_status, shipment_id))
        
        # Step 2: Write to the immutable audit log
        cur.execute("""
            INSERT INTO status_log (shipment_id, new_status, changed_by)
            VALUES (%s, %s, %s)
        """, (shipment_id, new_status, user_id))
        
        # Step 3: Explicitly commit BOTH changes to the database simultaneously (ACID Compliance)
        conn.commit()
        
    except Exception as e:
        # If either query fails, revert everything
        conn.rollback()
        print(f"Database Error: {e}")
        
    finally:
        conn.close()
```
## 4. Key Advantages of this Architecture
Wrapping our SQL queries inside the Python backend is not just convenient; it is a vital security and operational requirement for LogiTrack PK.
- **Prevention of SQL Injection:** By strictly using parameterized queries (the `%s` placeholders in `psycopg2`), the Python wrapper automatically sanitizes all user input. A user typing `admin' DROP TABLE users;--` into the login box will safely be treated as a literal string, not an executable command.
- **Separation of Concerns:** UI code (Streamlit buttons and layouts) does not contain raw SQL. The frontend simply calls backend Python functions, which handle the complex SQL joining and data transformation in the background.
- **Business Logic Enforcement:** SQL is optimized for storage, not complex procedural logic. Wrapping queries in Python allows LogiTrack PK to perform verifications before hitting the database—such as verifying a user's Bcrypt hash or checking Role-Based Access Control (RBAC) permissions to ensure a standard warehouse worker cannot delete executive records.
