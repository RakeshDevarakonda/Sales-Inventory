import os
import pymysql
from urllib.parse import urlparse, unquote
from dbutils.pooled_db import PooledDB
from backend.config.settings import DATABASE_URL

# Global pool instance
_pool: PooledDB | None = None


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


def get_connection_pool() -> PooledDB:
    global _pool
    if _pool is None:
        config = _parse_db_url()
        _pool = PooledDB(
            creator=pymysql,
            maxconnections=10,  # Max number of connections allowed in pool
            mincached=2,        # Initial number of idle connections
            maxcached=5,        # Max number of idle connections
            blocking=True,      # Wait for a connection to be returned if pool is full
            host=config["host"],
            port=config["port"],
            user=config["user"],
            password=config["password"],
            database=config["database"],
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=False,
        )
    return _pool


def get_db_connection():
    # Reuses/iterates an existing connection from the pool if available
    pool = get_connection_pool()
    return pool.connection()


def get_db():
    conn = get_db_connection()
    try:
        yield conn
    finally:
        # Returns the connection back to the pool (does not physically terminate the socket)
        conn.close()


def close_connection_pool():
    global _pool
    if _pool is not None:
        _pool.close()
        _pool = None
        print("Database connection pool closed.")


TABLE_DEFINITIONS = [
    """
    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(50) NULL UNIQUE,
        email VARCHAR(100) NOT NULL UNIQUE,
        phone VARCHAR(20) NULL,
        password_hash VARCHAR(255) NOT NULL,
        full_name VARCHAR(100) NULL,
        role ENUM('SALES_REP', 'MANAGER') NOT NULL DEFAULT 'SALES_REP',
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
    """
    CREATE TABLE IF NOT EXISTS sessions (
        id VARCHAR(36) PRIMARY KEY,
        user_id INT NOT NULL,
        refresh_token_hash VARCHAR(64) NOT NULL,
        user_agent TEXT NULL,
        ip_address VARCHAR(45) NULL,
        is_revoked BOOLEAN DEFAULT FALSE,
        expires_at TIMESTAMP NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    ) ENGINE=InnoDB;
    """,
    """
    CREATE TABLE IF NOT EXISTS inventory_movements (
        id INT AUTO_INCREMENT PRIMARY KEY,
        product_id INT NOT NULL,
        change_quantity INT NOT NULL,
        previous_stock INT NOT NULL,
        new_stock INT NOT NULL,
        movement_type ENUM('ORDER_FULFILLMENT', 'ORDER_CANCELLED', 'MANUAL_ADJUSTMENT', 'RESTOCK') NOT NULL,
        reference_id VARCHAR(50) NULL,
        performed_by_id INT NOT NULL,
        notes TEXT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (product_id) REFERENCES products(id),
        FOREIGN KEY (performed_by_id) REFERENCES users(id)
    ) ENGINE=InnoDB;
    """
]

INDEX_DEFINITIONS = [
    ("orders", "idx_orders_status", "CREATE INDEX idx_orders_status ON orders(status);"),
    ("orders", "idx_orders_customer", "CREATE INDEX idx_orders_customer ON orders(customer_id);"),
    ("orders", "idx_orders_created_by", "CREATE INDEX idx_orders_created_by ON orders(created_by_id);"),
    ("sessions", "idx_sessions_user_id", "CREATE INDEX idx_sessions_user_id ON sessions(user_id);"),
    ("inventory_movements", "idx_movements_product", "CREATE INDEX idx_movements_product ON inventory_movements(product_id);"),
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


def _column_exists(cursor, table_name: str, column_name: str) -> bool:
    cursor.execute(
        """
        SELECT COUNT(1) AS count
        FROM information_schema.columns
        WHERE table_schema = DATABASE()
          AND table_name = %s
          AND column_name = %s;
        """,
        (table_name, column_name)
    )
    result = cursor.fetchone()
    return bool(result and result.get("count", 0) > 0)


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
            # Create tables
            for statement in TABLE_DEFINITIONS:
                cursor.execute(statement)

            # Auto-migrate: Add phone column to users table if not exists
            if not _column_exists(cursor, "users", "phone"):
                cursor.execute("ALTER TABLE users ADD COLUMN phone VARCHAR(20) NULL AFTER email;")
                cursor.execute("ALTER TABLE users MODIFY COLUMN username VARCHAR(50) NULL UNIQUE;")
                cursor.execute("ALTER TABLE users MODIFY COLUMN full_name VARCHAR(100) NULL;")

            # Create indexes only if they do not already exist
            for table_name, index_name, create_sql in INDEX_DEFINITIONS:
                if not _index_exists(cursor, table_name, index_name):
                    cursor.execute(create_sql)

        db_conn.commit()
        print(f"Database '{config['database']}' and tables initialized successfully.")
    finally:
        db_conn.close()
