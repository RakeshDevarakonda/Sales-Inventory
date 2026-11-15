# Sales & Inventory Management Enterprise System

A production-grade, full-stack Sales and Inventory Management Enterprise Application built with **React (TypeScript, Vite, Redux Toolkit, Tailwind CSS)**, **FastAPI (Python 3.13)**, **MySQL**, and **Pure Raw SQL** (PooledDB, zero ORM).

The system handles customer lifecycle management, inventory control, transactional stock reservations, order workflows with dynamic approval thresholds, revocable JWT authentication with HttpOnly cookies, and background email dispatch via SMTP.

---

## 🏛 System Architecture

The application is architected with a decoupled frontend and a 4-tier layered backend following **SOLID principles**:

```
[ Frontend (React 19 + TypeScript + Vite) ]
                    │
                    ▼ HTTP (Axios + HttpOnly Cookies)
[ 1. Routes Layer (FastAPI APIRouter) ]
                    │
                    ▼
[ 2. Handlers Layer (Controllers: HTTP parameters, Cookies, DTO validation) ]
                    │
                    ▼
[ 3. Services Layer (Business logic, Stock reservations, Threshold evaluation) ]
                    │
                    ▼
[ 4. Repositories Layer (Pure Parameterized Raw SQL, PooledDB Connection Pool) ]
                    │
                    ▼
[ MySQL 8.0 Database (sales_inventory_db) ]
```

---

## 🚀 Key Features

### 1. Authentication & Security
- **Dual-Token Architecture:** Short-lived access token + long-lived HttpOnly refresh token cookie.
- **Revocable Sessions:** MySQL-backed session records allowing instantaneous single-device and multi-device revocation.
- **Strict Role-Based Access Control (RBAC):**
  - `SALES_REP`: Customer directory management, order creation, view personal orders.
  - `MANAGER`: Catalog management, stock adjustments, order approvals, user administration.
- **Enterprise Password Policy:** Enforces $\ge 8$ characters, uppercase, lowercase, and numeric digits.

### 2. Commercial Order & Approval Engine
- **Transactional Stock Locking:** Uses `SELECT ... FOR UPDATE` in deterministic order to prevent race conditions and overselling.
- **Dynamic Approval Threshold:**
  - Sales representative orders $\le ₹1,000$ (configurable in DB/settings) are immediately `CONFIRMED` and stock is deducted.
  - Sales representative orders $> ₹1,000$ enter `PENDING_APPROVAL` with stock safely reserved.
  - Manager-placed orders are auto-confirmed without self-approval requirements.
- **Two-Way Email Notifications:**
  - **Approval Alert:** Automatically sends email notifications to active managers with an actionable direct review button.
  - **Decision Alert:** Automatically notifies the Sales Rep upon manager approval or rejection with custom review notes.
- **Cancellation & Inventory Restoration:** Cancelling any pending or active order automatically releases reserved inventory back to the catalog.

### 3. Catalog & Customer Management
- **Strict Customer Validation:** Mandatory full name, email, address, and strictly enforced **10-digit phone numbers** (`^\d{10}$`).
- **Inventory Adjustments:** Managers can record manual stock increments/decrements with audit logging.
- **Duplicate Prevention:** Disables already-selected products in subsequent line items to ensure order data integrity.

### 4. Enterprise UI/UX
- **Server-Side Pagination:** Supports query parameters `page` and `limit` across Customers, Products, and Orders (`Rows: 5, 10, 20, 50`).
- **Serial Numbers (`S.No`):** Consistent serial numbering across all tabular views respecting current page offset.
- **Compact Responsive Modals:** Custom animated backdrop dialogs for customer creation, stock adjustments, order line item inspection, and cancellation confirmation.
- **Typography & Localization:** Enterprise typography (`Inter`, `JetBrains Mono`) with Indian Rupee (`₹`) tabular currency formatting.

---

## 🛠 Tech Stack

### Frontend
- **Framework:** React 19, TypeScript, Vite
- **State Management:** Redux Toolkit (RTK)
- **Styling:** Tailwind CSS (v4)
- **Icons:** Lucide React
- **HTTP Client:** Axios (configured with `withCredentials: true` for HttpOnly cookie forwarding)

### Backend
- **Framework:** FastAPI, Uvicorn
- **Language:** Python 3.13
- **Database Driver:** PyMySQL + DBUtils (`PooledDB`)
- **Security:** bcrypt, PyJWT, Pydantic v2
- **Email Service:** Python smtplib with SMTP (Gmail / custom relays)

---

## 📋 Environment Configuration

### Backend (`backend/.env`)

Copy `backend/.env.example` to `backend/.env` and update the parameters:

```env
DATABASE_URL=mysql://root:password@localhost:3307/sales_inventory_db
SECRET_KEY=your_secure_hex_jwt_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
REFRESH_TOKEN_EXPIRE_DAYS=7
APPROVAL_THRESHOLD_AMOUNT=1000.00
FRONTEND_URL=http://localhost:5173
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_gmail_app_password
MAIL_FROM=your_email@gmail.com
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

> **Note:** Manager recipient emails are queried dynamically from the database (`users` table where `role = 'MANAGER' AND is_active = TRUE`).

### Frontend (`frontend/.env`)

```env
VITE_API_BASE_URL=http://localhost:8000
```

---

## ⚙️ Setup & Local Development

### Prerequisites
- Node.js $\ge 18$
- Python $\ge 3.13$
- MySQL Server $\ge 8.0$

### 1. Database Setup
Create the MySQL database:
```sql
CREATE DATABASE sales_inventory_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

Run database migrations and initial seed data:
```bash
cd backend
python -m backend.scripts.migrate
python -m backend.scripts.seed
```

Default credentials seeded:
- **Manager:** `manager` / `Manager@123`
- **Sales Rep:** `salesrep` / `SalesRep@123`

### 2. Backend Startup
```bash
cd backend
# Create virtual environment if needed
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Start FastAPI server
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```
API Documentation will be available at `http://127.0.0.1:8000/docs`.

### 3. Frontend Startup
```bash
cd frontend
npm install
npm run dev
```
The application will launch on `http://localhost:5173`.

---

## 🧪 Testing & Verification

- **Frontend Production Build:**
  ```bash
  cd frontend
  npm run build
  ```
- **SMTP Email Verification:**
  ```bash
  cd backend
  python test_email.py
  ```
