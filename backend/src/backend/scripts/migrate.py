"""
Database Schema Migration Script
Creates the database, tables, and performance indexes.
Usage:
    uv run python -m backend.scripts.migrate
"""

import pymysql
from urllib.parse import urlparse, unquote
from backend.config.settings import DATABASE_URL


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
    """,
    """
    CREATE TABLE IF NOT EXISTS system_settings (
        setting_key VARCHAR(50) PRIMARY KEY,
        setting_value VARCHAR(255) NOT NULL,
        description VARCHAR(255) NULL,
        updated_by_id INT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        FOREIGN KEY (updated_by_id) REFERENCES users(id) ON DELETE SET NULL
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


def run_migrations():
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

        db_conn.commit()
        print("Schema migration completed successfully!")
    finally:
        db_conn.close()


if __name__ == "__main__":
    run_migrations()
