import os
import pymysql
from dotenv import load_dotenv
from urllib.parse import urlparse, unquote

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")


def get_db_connection():
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL is not set in .env")

    url = urlparse(DATABASE_URL)

    connection = pymysql.connect(
        host=url.hostname or "localhost",
        port=url.port or 3306,
        user=unquote(url.username or "root"),
        password=unquote(url.password or ""),
        database=url.path.lstrip("/"),
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=False
    )

    return connection


def get_db():
    conn = get_db_connection()
    try:
        yield conn
    finally:
        conn.close()