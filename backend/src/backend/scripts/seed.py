"""
Database Seeding Script
Populates the database with initial Manager, Sales Rep, Customers, and Products.
Usage:
    uv run python -m backend.scripts.seed
"""

import pymysql
from urllib.parse import urlparse, unquote
from backend.config.settings import DATABASE_URL
from backend.utils.security import hash_password


def _parse_db_url():
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL is not set in .env")

    url = urlparse(DATABASE_URL)
    return {
        "host": url.hostname,
        "port": url.port,
        "user": unquote(url.username),
        "password": unquote(url.password),
        "database": url.path.lstrip("/"),
    }


def seed_database():
    config = _parse_db_url()

    print(f"Connecting to database '{config['database']}' for seeding...")
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
            # 1. Seed Manager & Sales Rep users
            cursor.execute("SELECT COUNT(1) AS count FROM users;")
            if cursor.fetchone()["count"] == 0:
                default_manager_pwd = hash_password("Manager@123")
                default_sales_pwd = hash_password("SalesRep@123")
                cursor.execute(
                    """
                    INSERT INTO users (username, email, phone, password_hash, role)
                    VALUES 
                        ('manager', 'rakeshdevarakonda2000@gmail.com', '9515147103', %s, 'MANAGER'),
                        ('salesrep', 'rakeshdevarakonda200@gmail.com', '9951255476', %s, 'SALES_REP');
                    """,
                    (default_manager_pwd, default_sales_pwd)
                )
                print(" -> Seeded initial users: 'manager' (Manager@123) and 'salesrep' (SalesRep@123)")
            else:
                print(" -> Users table already has data, skipping user seeds.")

            # 2. Seed Sample Customers
            cursor.execute("SELECT COUNT(1) AS count FROM customers;")
            if cursor.fetchone()["count"] == 0:
                cursor.execute(
                    """
                    INSERT INTO customers (name, email, phone, address)
                    VALUES 
                        ('Acme Enterprises', 'purchasing@acme.com', '9876543210', '100 Industrial Parkway, Chicago, IL'),
                        ('Apex Retailers', 'orders@apexretail.com', '9876543211', '452 Marketplace Blvd, Dallas, TX'),
                        ('Horizon Tech Corp', 'vendor@horizontech.com', '9876543212', '789 Silicon Ave, Austin, TX');
                    """
                )
                print(" -> Seeded 3 sample customers: Acme Enterprises, Apex Retailers, Horizon Tech Corp")
            else:
                print(" -> Customers table already has data, skipping customer seeds.")

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
            else:
                print(" -> Products table already has data, skipping product seeds.")

        db_conn.commit()
        print("Seeding completed successfully!")
    finally:
        db_conn.close()


if __name__ == "__main__":
    seed_database()
