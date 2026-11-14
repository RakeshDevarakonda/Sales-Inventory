"""
Database Schema Migration & Seed Script
Run this script once before starting the application server:
    uv run python -m backend.scripts.init_db
"""

import pymysql
from urllib.parse import urlparse, unquote
from backend.config.settings import DATABASE_URL
from backend.utils.security import hash_password


def _parse_db_url():
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL is not set in .env")

    url = urlparse(DATABASE_URL)
    if not url.hostname:
        raise ValueError("DATABASE_URL is missing host")
    if not url.port:
        raise ValueError("DATABASE_URL is missing port")
    if not url.username:
        raise ValueError("DATABASE_URL is missing username")
    if url.password is None:
        raise ValueError("DATABASE_URL is missing password")

    database_name = url.path.lstrip("/")
    if not database_name:
        raise ValueError("DATABASE_URL is missing database name")

    return {
        "host": url.hostname,
        "port": url.port,
        "user": unquote(url.username),
        "password": unquote(url.password),
        "database": database_name,
    }


TABLE_DEFINITIONS = [
    """
    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(50) NULL UNIQUE,
        email VARCHAR(100) NOT NULL UNIQUE,
        phone VARCHAR(20) NULL,
        password_hash VARCHAR(255) NOT NULL,
        role ENUM('SALES_REP', 'MANAGER') NOT NULL DEFAULT 'SALES_REP',
        is_active BOOLEAN DEFAULT TRUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
    ) ENGINE=InnoDB;
    """,
    """
    CREATE TABLE IF NOT EXISTS customers (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        email VARCHAR(100) NOT NULL,
        phone VARCHAR(20) NULL,
        address TEXT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
    ) ENGINE=InnoDB;
    """,
    """
    CREATE TABLE IF NOT EXISTS products (
        id INT AUTO_INCREMENT PRIMARY KEY,
        sku VARCHAR(50) NOT NULL UNIQUE,
        name VARCHAR(150) NOT NULL,
        description TEXT NULL,
        price DECIMAL(10, 2) NOT NULL,
        stock_quantity INT NOT NULL DEFAULT 0,
        is_active BOOLEAN DEFAULT TRUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        CONSTRAINT chk_product_price CHECK (price >= 0),
        CONSTRAINT chk_product_stock CHECK (stock_quantity >= 0)
    ) ENGINE=InnoDB;
    """,
    """
    CREATE TABLE IF NOT EXISTS orders (
        id INT AUTO_INCREMENT PRIMARY KEY,
        order_number VARCHAR(50) NOT NULL UNIQUE,
        customer_id INT NOT NULL,
        created_by_id INT NOT NULL,
        total_amount DECIMAL(12, 2) NOT NULL,
        status ENUM('PENDING_APPROVAL', 'CONFIRMED', 'APPROVED', 'REJECTED', 'CANCELLED') NOT NULL,
        reviewed_by_id INT NULL,
        approval_notes TEXT NULL,
        reviewed_at TIMESTAMP NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        FOREIGN KEY (customer_id) REFERENCES customers(id),
        FOREIGN KEY (created_by_id) REFERENCES users(id),
        FOREIGN KEY (reviewed_by_id) REFERENCES users(id)
    ) ENGINE=InnoDB;
    """,
    """
    CREATE TABLE IF NOT EXISTS order_items (
        id INT AUTO_INCREMENT PRIMARY KEY,
        order_id INT NOT NULL,
        product_id INT NOT NULL,
        quantity INT NOT NULL,
        unit_price DECIMAL(10, 2) NOT NULL,
        subtotal DECIMAL(12, 2) NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
        FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE RESTRICT,
        UNIQUE KEY uq_order_product (order_id, product_id),
        CONSTRAINT chk_item_quantity CHECK (quantity > 0),
        CONSTRAINT chk_item_price CHECK (unit_price >= 0),
        CONSTRAINT chk_item_subtotal CHECK (subtotal >= 0)
    ) ENGINE=InnoDB;
    """,
    """
    CREATE TABLE IF NOT EXISTS sessions (
        id VARCHAR(36) PRIMARY KEY,
        user_id INT NOT NULL,
        refresh_token_hash VARCHAR(64) NOT NULL,
        is_revoked BOOLEAN DEFAULT FALSE,
        expires_at TIMESTAMP NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    ) ENGINE=InnoDB;
    """
]

INDEX_DEFINITIONS = [
    ("orders", "idx_orders_status", "CREATE INDEX idx_orders_status ON orders(status);"),
    ("orders", "idx_orders_customer", "CREATE INDEX idx_orders_customer ON orders(customer_id);"),
    ("orders", "idx_orders_created_by", "CREATE INDEX idx_orders_created_by ON orders(created_by_id);"),
    ("sessions", "idx_sessions_user_id", "CREATE INDEX idx_sessions_user_id ON sessions(user_id);"),
]


def _index_exists(cursor, table_name: str, index_name: str) -> bool:
    cursor.execute(
        """
        SELECT COUNT(1) AS count
        FROM information_schema.statistics
        WHERE table_schema = DATABASE()
          AND table_name = %s
          AND index_name = %s;
        """,
        (table_name, index_name)
    )
    result = cursor.fetchone()
    return bool(result and result.get("count", 0) > 0)


def seed_initial_data(cursor):
    """Seed initial Manager, Sales Rep, Sample Customers, and Sample Products if empty."""
    # 1. Seed Manager & Sales Rep
    cursor.execute("SELECT COUNT(1) AS count FROM users;")
    if cursor.fetchone()["count"] == 0:
        default_manager_pwd = hash_password("Manager@123")
        default_sales_pwd = hash_password("SalesRep@123")
        cursor.execute(
            """
            INSERT INTO users (username, email, phone, password_hash, role)
            VALUES 
                ('manager', 'manager@salesinventory.com', '1234567890', %s, 'MANAGER'),
                ('salesrep', 'sales@salesinventory.com', '0987654321', %s, 'SALES_REP');
            """,
            (default_manager_pwd, default_sales_pwd)
        )
        print(" -> Seeded initial users: 'manager' and 'salesrep'")

    # 2. Seed Sample Customers
    cursor.execute("SELECT COUNT(1) AS count FROM customers;")
    if cursor.fetchone()["count"] == 0:
        cursor.execute(
            """
            INSERT INTO customers (name, email, phone, address)
            VALUES 
                ('Acme Enterprises', 'purchasing@acme.com', '+1-555-0100', '100 Industrial Parkway, Chicago, IL'),
                ('Apex Retailers', 'orders@apexretail.com', '+1-555-0144', '452 Marketplace Blvd, Dallas, TX'),
                ('Horizon Tech Corp', 'vendor@horizontech.com', '+1-555-0188', '789 Silicon Ave, Austin, TX');
            """
        )
        print(" -> Seeded 3 sample customers")

    # 3. Seed Sample Products with Inventory
    cursor.execute("SELECT COUNT(1) AS count FROM products;")
    if cursor.fetchone()["count"] == 0:
        cursor.execute(
            """
            INSERT INTO products (sku, name, description, price, stock_quantity)
            VALUES 
                ('PROD-LAPTOP-01', 'Enterprise Pro Laptop 15"', 'Intel i7, 32GB RAM, 1TB SSD', 1299.99, 25),
                ('PROD-MONITOR-02', '4K UHD Monitor 27"', 'IPS, HDR, 144Hz Refresh Rate', 349.50, 40),
                ('PROD-KEYBOARD-03', 'Wireless Mechanical Keyboard', 'RGB Backlit, Hot-swappable Switches', 89.99, 100),
                ('PROD-MOUSE-04', 'Ergonomic Precision Mouse', 'Bluetooth & 2.4G Dual Mode', 49.99, 8),
                ('PROD-DOCK-05', 'Thunderbolt 4 Docking Station', 'Dual 4K display, 100W PD charging', 199.00, 15);
            """
        )
        print(" -> Seeded 5 sample products with stock")


def run_migration_and_seeds():
    config = _parse_db_url()

    print(f"Connecting to MySQL server at {config['host']}:{config['port']}...")
    server_conn = pymysql.connect(
        host=config["host"],
        port=config["port"],
        user=config["user"],
        password=config["password"],
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True
    )
    try:
        with server_conn.cursor() as cursor:
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{config['database']}`;")
            print(f"Database '{config['database']}' confirmed.")
    finally:
        server_conn.close()

    db_conn = pymysql.connect(
        host=config["host"],
        port=config["port"],
        user=config["user"],
        password=config["password"],
        database=config["database"],
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=False
    )
    try:
        with db_conn.cursor() as cursor:
            print("Applying table definitions...")
            for statement in TABLE_DEFINITIONS:
                cursor.execute(statement)

            print("Applying index definitions...")
            for table_name, index_name, create_sql in INDEX_DEFINITIONS:
                if not _index_exists(cursor, table_name, index_name):
                    cursor.execute(create_sql)

            print("Applying seed data...")
            seed_initial_data(cursor)

        db_conn.commit()
        print("Migration and seeding completed successfully!")
    finally:
        db_conn.close()


if __name__ == "__main__":
    run_migration_and_seeds()
