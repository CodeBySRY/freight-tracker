-- ─── FREIGHT TRACKER TRUE ENTERPRISE SCHEMA ──────────────────────

CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE carriers (
    carrier_id SERIAL PRIMARY KEY,
    company_name VARCHAR(100) NOT NULL,
    contact_phone VARCHAR(50),
    vehicle_type VARCHAR(50),
    is_available BOOLEAN DEFAULT TRUE
);

CREATE TABLE orders (
    order_id SERIAL PRIMARY KEY,
    customer_name VARCHAR(100) NOT NULL,
    origin_city VARCHAR(100) NOT NULL,
    destination_city VARCHAR(100) NOT NULL,
    cargo_description TEXT,
    cargo_type VARCHAR(50),
    cargo_weight_kg NUMERIC,
    priority VARCHAR(50),
    special_instructions TEXT,
    expected_delivery_date DATE,
    is_cancelled BOOLEAN DEFAULT FALSE,
    created_by INTEGER REFERENCES users(user_id)
);

CREATE TABLE shipments (
    shipment_id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES orders(order_id),
    carrier_id INTEGER REFERENCES carriers(carrier_id),
    status VARCHAR(50) DEFAULT 'Pending',
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    actual_delivery_date DATE,
    delivered_at TIMESTAMP,
    notes TEXT
);

CREATE TABLE status_log (
    log_id SERIAL PRIMARY KEY,
    shipment_id INTEGER REFERENCES shipments(shipment_id),
    old_status VARCHAR(50),
    new_status VARCHAR(50),
    notes TEXT,
    changed_by INTEGER REFERENCES users(user_id),
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ─── AUTHENTICATION SEEDING ──────────────────────────────────────
-- These are pre-hashed bcrypt passwords for the phrase: Giki2026!
-- We inject these so you are not locked out of your own app upon deployment.

INSERT INTO users (full_name, email, password_hash, role, is_active) VALUES 
('System Admin', 'admin@logitrack.pk', '$2b$12$FhfcqwOVU4EgH/LuULoh7eNc/H8Unro5ArOpaIgHALLYfywE2FHnO', 'System Administrator', TRUE),
('Muhammad Ahmad', 'ahmad@logitrack.pk', '$2b$12$jKNovhA/w2GVQvS6fRHKguX.craq1q0qGU2zxL/Q3lpBicHkhM8wi', 'Dispatcher', TRUE),
('Abdullah', 'abdullah@logitrack.pk', '$2b$12$hTXospgUPF02BATCVDiQj.ZNAOrn7P7gy8vaXOsuQeWgeyHtfgs/S', 'Warehouse Manager', TRUE);