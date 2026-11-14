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


def get_connection_pool() -> PooledDB:
    global _pool
    if _pool is None:
        config = _parse_db_url()
        _pool = PooledDB(
            creator=pymysql,
            maxconnections=10,
            mincached=2,
            maxcached=5,
            blocking=True,
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
    pool = get_connection_pool()
    return pool.connection()


def get_db():
    conn = get_db_connection()
    try:
        yield conn
    finally:
        conn.close()


def check_database_connectivity():
    """Lightweight startup probe: ensures DB is reachable without executing any DDL."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT 1 AS status;")
            result = cursor.fetchone()
            if not result or result.get("status") != 1:
                raise RuntimeError("Database ping returned unexpected result")
    finally:
        conn.close()


def close_connection_pool():
    global _pool
    if _pool is not None:
        _pool.close()
        _pool = None
        print("Database connection pool closed.")
