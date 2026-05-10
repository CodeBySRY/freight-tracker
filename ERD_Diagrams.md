# LogiTrack PK - Database Architecture & ERD Documentation

## 1. System Overview
The LogiTrack PK database is built on a highly relational, ACID-compliant PostgreSQL architecture. The schema is designed using Domain-Driven Design (DDD) principles, strictly separating the "intent" of a delivery (Orders) from the "physical execution" of a delivery (Shipments). This separation ensures data integrity, prevents double-booking of carriers, and provides an immutable audit trail for all logistics operations.

## 2. Entity Schemas & Design Choices

### 2.1 `users` (Access & Authentication)
**Purpose:** Manages system access, Role-Based Access Control (RBAC), and accountability for system actions.
* `user_id` (SERIAL, PK): Auto-incrementing primary key for fast indexing.
* `full_name` (VARCHAR): Display name for the UI.
* `email` (VARCHAR, UNIQUE): Enforces unique logins at the database level.
* `password_hash` (VARCHAR): Stores Bcrypt hashed passwords; plain text is never saved.
* `role` (VARCHAR): Determines RBAC permissions (e.g., Admin, Dispatcher, Warehouse).
* `is_active` (BOOLEAN): Soft-delete implementation. Instead of deleting users and breaking foreign key constraints on historical orders, accounts are simply deactivated.

### 2.2 `carriers` (Fleet Management)
**Purpose:** Acts as the vendor registry for 3PL (Third-Party Logistics) partners and internal fleet vehicles.
* `carrier_id` (SERIAL, PK): Unique identifier for the transport entity.
* `company_name` (VARCHAR): The name of the logistics provider (e.g., TCS, Leopard).
* `vehicle_type` (VARCHAR): Defines capacity constraints (e.g., Flatbed, Container).
* `is_available` (BOOLEAN): Allows dispatchers to instantly filter out carriers currently at capacity or undergoing maintenance.

### 2.3 `orders` (The Logistics Intent)
**Purpose:** Represents a customer request to move freight. An order exists purely as a logistical requirement before any physical assets are assigned to it.
* `order_id` (SERIAL, PK): Unique tracking number for the customer.
* `origin_city` / `destination_city` (VARCHAR): Core routing logic.
* `cargo_weight_kg` (NUMERIC): Allows for precise payload calculations.
* `priority` (VARCHAR): Flags high-stakes deliveries (e.g., Standard vs. Expedited).
* `is_cancelled` (BOOLEAN): Soft-delete flag for aborted requests.
* `created_by` (INT, FK): Links the creation of the order back to a specific `users` record for accountability.

### 2.4 `shipments` (The Physical Execution)
**Purpose:** The bridge between an `order` (the request) and a `carrier` (the truck). 
* `shipment_id` (SERIAL, PK): Internal tracking ID for the warehouse.
* `order_id` (INT, FK, UNIQUE): Links back to the original order. The `UNIQUE` constraint is a critical design choice preventing the same order from being shipped twice.
* `carrier_id` (INT, FK): Identifies which truck is executing the delivery.
* `status` (VARCHAR): Current real-time state (e.g., In Transit, Delivered).
* `actual_delivery_date` / `delivered_at` (TIMESTAMP): Granular timestamps for calculating KPI metrics like "On-Time Delivery Rate."

### 2.5 `status_log` (The Immutable Audit Trail)
**Purpose:** A chronological ledger of every single state change a shipment undergoes. Crucial for resolving disputes and tracking bottlenecks.
* `log_id` (SERIAL, PK): Sequential ID for the event.
* `shipment_id` (INT, FK): The shipment being tracked.
* `old_status` / `new_status` (VARCHAR): Captures the exact transition (e.g., from 'Pending' to 'Dispatched').
* `changed_by` (INT, FK): Identifies the specific user/employee who authorized the status change.
* `changed_at` (TIMESTAMP): The exact millisecond the transition occurred.

---

## 3. Relational Cardinality & Business Logic

The Entity-Relationship Diagram (ERD) defines how these tables interact, enforcing the business rules of the LogiTrack PK platform.

### Users ↔ Orders (1 : N)
* **Cardinality:** One User can create Zero-to-Many Orders.
* **Justification:** A single dispatcher or admin handles high-volume data entry. By linking every order to the `user_id` of the person who created it, the system maintains strict accountability and allows for performance tracking per employee.

### Orders ↔ Shipments (1 : 0..1)
* **Cardinality:** One Order is linked to Zero-or-One Shipment.
* **Justification:** This is the most vital architectural decision in the database. When a customer requests freight movement, an `Order` is generated. It exists independently (0 shipments). Only when a dispatcher successfully assigns a truck does a `Shipment` record generate. Enforcing a strict 1:1 maximum prevents catastrophic logistical errors, such as dispatching two separate trucks to pick up the same single cargo load.

### Carriers ↔ Shipments (1 : N)
* **Cardinality:** One Carrier can execute Zero-to-Many Shipments.
* **Justification:** A logistics company relies on recurring partnerships. A specific carrier (like Pakistan Freight Services) will be contracted to handle hundreds of different shipments over the lifecycle of the database. 

### Shipments ↔ Status_Log (1 : N)
* **Cardinality:** One Shipment generates One-to-Many Status Logs.
* **Justification:** A physical delivery is not a binary state; it is a timeline. A single shipment will generate multiple log entries as it moves from *Assigned* → *In Transit* → *At Customs* → *Delivered*. This 1:N relationship acts as a blockchain-like ledger, ensuring that no status change is ever overwritten or lost.

### Users ↔ Status_Log (1 : N)
* **Cardinality:** One User generates Zero-to-Many Status Logs.
* **Justification:** Security and auditing. If a high-value shipment is suddenly marked as "Cancelled" or "Missing," management must know exactly which user account triggered that change in the system.

---
*Engineered by Shayan Rizwan, Agha Salaat, and Anzar Mubashir.*