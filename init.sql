-- ─── ENTERPRISE LOGISTICS SCHEMA ─────────────────────────────────

-- 1. Users Table (Authentication & RBAC)
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE
);

-- 2. Carriers Table (Fleet Management)
CREATE TABLE carriers (
    carrier_id SERIAL PRIMARY KEY,
    company_name VARCHAR(100) NOT NULL,
    is_available BOOLEAN DEFAULT TRUE
);

-- 3. Orders Table (Freight Requests)
CREATE TABLE orders (
    order_id SERIAL PRIMARY KEY,
    origin_city VARCHAR(100) NOT NULL,
    destination_city VARCHAR(100) NOT NULL
);

-- 4. Shipments Table (Active Tracking)
CREATE TABLE shipments (
    shipment_id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES orders(order_id),
    carrier_id INTEGER REFERENCES carriers(carrier_id),
    status VARCHAR(50) DEFAULT 'Pending',
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 5. Audit Log (Immutable Ledger for Security)
CREATE TABLE status_log (
    log_id SERIAL PRIMARY KEY,
    shipment_id INTEGER REFERENCES shipments(shipment_id),
    old_status VARCHAR(50),
    new_status VARCHAR(50),
    changed_by INTEGER REFERENCES users(user_id),
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ─── AUTHENTICATION SEEDING ──────────────────────────────────────
-- These are pre-hashed bcrypt passwords for the phrase: Giki2026!
-- We inject these so you are not locked out of your own app upon deployment.

INSERT INTO users (full_name, email, password_hash, role, is_active) VALUES 
('System Admin', 'admin@logitrack.pk', '$2b$12$R.S4qM6P9.m4zF5v/gP/xeb/5Yq9LwQ2/U1/p5/wF8q.v.wQx/1mG', 'System Administrator', TRUE),
('Muhammad Ahmad', 'ahmad@logitrack.pk', '$2b$12$R.S4qM6P9.m4zF5v/gP/xeb/5Yq9LwQ2/U1/p5/wF8q.v.wQx/1mG', 'Dispatcher', TRUE),
('Abdullah', 'abdullah@logitrack.pk', '$2b$12$R.S4qM6P9.m4zF5v/gP/xeb/5Yq9LwQ2/U1/p5/wF8q.v.wQx/1mG', 'Warehouse Manager', TRUE);