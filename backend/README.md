# Sales & Inventory Management System - Backend API

A high-performance, production-grade Sales & Inventory Management backend built with **FastAPI**, **Python 3.13**, **MySQL**, and **Pure Raw SQL** (no ORM).

The system handles customer and product catalogs, sales orders, inventory control, automated multi-tier approval workflows with threshold checks, revocable JWT session authentication, and asynchronous email notifications.

---

## Architecture Overview

The backend is built using a strict **4-Tier Layered Architecture**:

```
Client / HTTP Requests
         │
         ▼
 1. routes/        ──> URL definitions, HTTP methods, response models & dependency injection
         │
         ▼
 2. handlers/      ──> Controllers: extracts query/body/cookies, calls services, sets cookies
         │
         ▼
 3. services/      ──> Core business logic, order threshold engine, password hashing, JWT rotation
         │
         ▼
 4. repositories/  ──> Database access layer: pure parameterized raw SQL queries
         │
         ▼
       MySQL
```

---

## Key Features

- **Authentication & Sessions:**
  - Password strength enforcement ($\ge 8$ chars, uppercase, lowercase, digit).
  - Short-lived Access Token (30 min) + long-lived HttpOnly Refresh Token Cookie (7 days).
  - MySQL-backed revocable sessions with native `UUID()` IDs.
  - Dedicated `/api/auth/change-password` endpoint that revokes active sessions on password change.
- **Role-Based Access Control (RBAC):**
  - `SALES_REP`: Creates sales orders, manages customers, views personal order history.
  - `MANAGER`: Full system access, manager-only user administration, stock adjustments, order approvals and rejections.
- **Sales Order Approval Engine:**
  - Validates customer existence, active product status, and available stock.
  - **Threshold Check:** Orders $> \$1,000$ enter `PENDING_APPROVAL` and dispatch an async email alert to the Manager.
  - Orders $\le \$1,000$ are auto-confirmed and stock is deducted immediately.
  - Manager can Approve (deducts stock and emails sales rep) or Reject (emails sales rep with notes).
  - Cancelling an order restores deducted stock back to the products table.
- **Production-Grade Database Design:**
  - Pure raw SQL with connection pooling (`dbutils.pooled_db`).
  - Zero runtime DDL: web server startup performs only a 1ms `SELECT 1` ping.
  - Automated `created_at` and `updated_at` timestamps on all tables.
  - Standalone migration & seeding script (`init_db.py`).
- **Global Error Handling:**
  - Standardized JSON responses for `HTTPException` (4xx/5xx).
  - Clean field-level formatting for Pydantic validation errors (422).
  - Global catch-all 500 handler that logs full tracebacks to the console while returning clean responses to clients.

---

## Tech Stack

- **Framework:** FastAPI
- **Server:** Uvicorn
- **Package Manager:** `uv`
- **Database:** MySQL
- **Database Driver & Pool:** `PyMySQL` + `DBUtils (PooledDB)`
- **Security:** `bcrypt`, `pyjwt`
- **Data Validation:** `pydantic`, `email-validator`

---

## Project Structure

```
backend/
├── src/backend/
│   ├── config/
│   │   ├── database.py         # PooledDB connection pool & health probe
│   │   └── settings.py         # Centralized environment variable loader
│   ├── handlers/               # Controllers (HTTP layer)
│   │   ├── auth_handler.py
│   │   ├── customer_handler.py
│   │   ├── dashboard_handler.py
│   │   ├── error_handlers.py   # Global exception formatting
│   │   ├── health_handler.py
│   │   ├── inventory_handler.py
│   │   ├── order_handler.py
│   │   └── user_handler.py
│   ├── repositories/           # Pure Raw SQL Data Layer
│   │   ├── customer_repository.py
│   │   ├── dashboard_repository.py
│   │   ├── inventory_repository.py
│   │   ├── order_repository.py
│   │   ├── product_repository.py
│   │   ├── session_repository.py
│   │   └── user_repository.py
│   ├── routes/                 # API Endpoints & Routers
│   │   ├── __init__.py         # Single consolidated api_router
│   │   ├── auth_routes.py
│   │   ├── customer_routes.py
│   │   ├── dashboard_routes.py
│   │   ├── health_routes.py
│   │   ├── inventory_routes.py
│   │   ├── order_routes.py
│   │   └── product_routes.py
│   ├── schemas/                # Pydantic DTOs & Validation
│   │   ├── auth.py
│   │   ├── customer.py
│   │   ├── dashboard.py
│   │   ├── inventory.py
│   │   ├── order.py
│   │   ├── order_item.py
│   │   └── user.py
│   ├── scripts/
│   │   └── init_db.py          # Standalone Migration & Seed script
│   ├── services/               # Core Business Logic Layer
│   │   ├── customer_service.py
│   │   ├── dashboard_service.py
│   │   ├── email_service.py
│   │   ├── inventory_service.py
│   │   ├── order_service.py
│   │   └── user_service.py
│   └── utils/
│       └── security.py         # Password hashing, token encoding, role dependencies
├── main.py                     # Application entry point & lifespan
├── pyproject.toml              # Dependencies & project metadata
└── .env                        # Local configuration
```

---

## Getting Started

### 1. Prerequisites
- Python 3.13+
- MySQL Server (running locally or remotely)
- `uv` package manager (`pip install uv`)

### 2. Configure Environment (`.env`)
Create a `.env` file in the `backend/` folder:

```env
# Database Configuration (Exact URL, no default fallbacks)
DATABASE_URL=mysql://root:YOUR_PASSWORD@localhost:3306/sales_inventory_db

# Security
SECRET_KEY=your_super_secret_jwt_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Business Thresholds
APPROVAL_THRESHOLD_AMOUNT=1000.00

# Email Configuration (Optional - logs to console if empty)
MAIL_SERVER=smtp.mailtrap.io
MAIL_PORT=587
MAIL_USERNAME=
MAIL_PASSWORD=
MAIL_FROM=noreply@salesinventory.com
MANAGER_EMAIL=manager@salesinventory.com
```

### 3. Initialize Database & Seed Sample Data
Run the standalone migration and seeding scripts:

```powershell
# 1. Run migrations (creates database, tables, and indexes)
uv run python -m backend.scripts.migrate

# 2. Seed initial test data (users, customers, and products)
uv run python -m backend.scripts.seed
```
This automatically:
- Creates the `sales_inventory_db` database if missing.
- Builds all tables and performance indexes.
- Seeds default test accounts and sample catalog:
  - **Manager Account:** `username: manager`, `password: Manager@123`
  - **Sales Rep Account:** `username: salesrep`, `password: SalesRep@123`
  - 3 Sample Customers (Acme Enterprises, Apex Retailers, Horizon Tech)
  - 5 Sample Products with active stock (Laptops, 4K Monitors, Keyboards, Mice, Docks)

### 4. Run the API Server
Start the development server:
```powershell
uv run fastapi dev main.py
```

The API will be available at:
- **API Base:** `http://127.0.0.1:8000`
- **Interactive Swagger Documentation:** `http://127.0.0.1:8000/docs`
- **ReDoc Documentation:** `http://127.0.0.1:8000/redoc`

---

## API Endpoints Reference

### Authentication (`/api/auth`)
| Method | Endpoint | Description | Access |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/auth/register` | Register new sales representative | Public |
| `POST` | `/api/auth/login` | Login, issue access token + HttpOnly cookie | Public |
| `POST` | `/api/auth/logout` | Revoke session row & delete refresh cookie | Authenticated |
| `GET` | `/api/auth/me` | Get current logged-in profile | Authenticated |
| `POST` | `/api/auth/refresh` | Rotate access & refresh tokens | Public (Cookie) |
| `PATCH` | `/api/auth/change-password` | Change password & revoke existing sessions | Authenticated |

### User Management (`/api/users`)
| Method | Endpoint | Description | Access |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/users` | Create user with assigned role | `MANAGER` |
| `GET` | `/api/users` | List all users | `MANAGER` |
| `GET` | `/api/users/{user_id}` | Get user details | `MANAGER` |
| `PATCH` | `/api/users/{user_id}` | Update user profile | `MANAGER` |
| `PATCH` | `/api/users/{user_id}/role` | Change user role (`SALES_REP` / `MANAGER`) | `MANAGER` |
| `PATCH` | `/api/users/{user_id}/status` | Activate/deactivate user (revokes sessions) | `MANAGER` |

### Customer Directory (`/api/customers`)
| Method | Endpoint | Description | Access |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/customers` | Create a customer | Authenticated |
| `GET` | `/api/customers` | List all customers | Authenticated |
| `GET` | `/api/customers/{customer_id}` | View customer profile | Authenticated |
| `PUT` | `/api/customers/{customer_id}` | Update customer details | Authenticated |
| `DELETE`| `/api/customers/{customer_id}` | Delete customer (safe-check for orders) | Authenticated |

### Product Catalog (`/api/products`)
| Method | Endpoint | Description | Access |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/products` | Create product | `MANAGER` |
| `GET` | `/api/products` | List all products | Authenticated |
| `GET` | `/api/products/{product_id}` | Get product details | Authenticated |
| `PATCH` | `/api/products/{product_id}` | Update product pricing / stock | `MANAGER` |
| `PATCH` | `/api/products/{product_id}/status`| Activate / deactivate product | `MANAGER` |

### Inventory Management (`/api/inventory`)
| Method | Endpoint | Description | Access |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/inventory` | View all product stock levels | Authenticated |
| `GET` | `/api/inventory/low-stock` | View products with low stock ($\le 10$) | Authenticated |
| `GET` | `/api/inventory/{product_id}` | View stock for specific product | Authenticated |
| `POST` | `/api/inventory/adjustments` | Manually adjust product stock | `MANAGER` |

### Sales Orders & Approval Workflow (`/api/orders`)
| Method | Endpoint | Description | Access |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/orders` | Create sales order (threshold check applied) | `SALES_REP` / Auth |
| `GET` | `/api/orders` | List all sales orders | Authenticated |
| `GET` | `/api/orders/my-orders` | View logged-in rep's orders | `SALES_REP` |
| `GET` | `/api/orders/{order_id}` | Get full order details with line items | Owner / `MANAGER` |
| `PATCH` | `/api/orders/{order_id}` | Edit order while `PENDING_APPROVAL` | Owner |
| `POST` | `/api/orders/{order_id}/cancel` | Cancel order (restores stock if confirmed) | Owner / `MANAGER` |
| `POST` | `/api/orders/{order_id}/approve`| Approve order (deducts stock, emails rep) | `MANAGER` |
| `POST` | `/api/orders/{order_id}/reject` | Reject order (emails rep with reason notes) | `MANAGER` |

### Dashboard & Analytics (`/api/dashboard`)
| Method | Endpoint | Description | Access |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/dashboard/stats` | High-level metrics: revenue, order breakdowns, low-stock count, recent orders | Authenticated |

### Health Probe (`/health`)
| Method | Endpoint | Description | Access |
| :--- | :--- | :--- | :--- |
| `GET` | `/health` | Live database connectivity status ping | Public |
