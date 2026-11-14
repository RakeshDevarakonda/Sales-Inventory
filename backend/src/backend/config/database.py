import os
import pymysql
from dotenv import load_dotenv
from urllib.parse import urlparse, unquote

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")


def _parse_db_url():
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL is not set in .env")
    url = urlparse(DATABASE_URL)
    return {
        "host": url.hostname or "localhost",
        "port": url.port or 3306,
        "user": unquote(url.username or "root"),
        "password": unquote(url.password or ""),
        "database": url.path.lstrip("/"),
    }


def get_db_connection():
    config = _parse_db_url()
    connection = pymysql.connect(
        host=config["host"],
        port=config["port"],
        user=config["user"],
        password=config["password"],
        database=config["database"],
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=False,
    )
    return connection


def get_db():
    conn = get_db_connection()
    try:
        yield conn
    finally:
        conn.close()


TABLE_DEFINITIONS = [
    """
    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(50) NOT NULL UNIQUE,
        email VARCHAR(100) NOT NULL UNIQUE,
        password_hash VARCHAR(255) NOT NULL,
        full_name VARCHAR(100) NOT NULL,
        role ENUM('SALES_REP', 'MANAGER') NOT NULL,
        is_active BOOLEAN DEFAULT TRUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    ) ENGINE=InnoDB;
    """,
    """
    CREATE TABLE IF NOT EXISTS customers (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        email VARCHAR(100) NOT NULL,
        phone VARCHAR(20) NULL,
        address TEXT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
        FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
        FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE RESTRICT,
        UNIQUE KEY uq_order_product (order_id, product_id),
        CONSTRAINT chk_item_quantity CHECK (quantity > 0),
        CONSTRAINT chk_item_price CHECK (unit_price >= 0),
        CONSTRAINT chk_item_subtotal CHECK (subtotal >= 0)
    ) ENGINE=InnoDB;
    """,
    "CREATE INDEX idx_orders_status ON orders(status);",
    "CREATE INDEX idx_orders_customer ON orders(customer_id);",
    "CREATE INDEX idx_orders_created_by ON orders(created_by_id);"
]


def init_db():
    config = _parse_db_url()

    # 1. Connect without selecting database to ensure database exists
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
    finally:
        server_conn.close()

    # 2. Connect to the target database and create tables & indexes
    db_conn = get_db_connection()
    try:
        with db_conn.cursor() as cursor:
            for statement in TABLE_DEFINITIONS:
                try:
                    cursor.execute(statement)
                except pymysql.err.OperationalError as e:
                    # Ignore duplicate index errors if already created (Error 1061)
                    if e.args[0] == 1061:
                        pass
                    else:
                        raise e
        db_conn.commit()
        print(f"Database '{config['database']}' and tables initialized successfully.")
    finally:
        db_conn.close()
