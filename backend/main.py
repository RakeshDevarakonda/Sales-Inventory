from fastapi import FastAPI
from backend.config.database import get_db_connection

app = FastAPI(
    title="Sales and Inventory Management System",
    version="1.0.0"
)

# Test database connection on startup / module import
try:
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("SELECT 1 AS status")
    conn.close()
    print("Database connected successfully.")
except Exception as e:
    print(f"Database connection error: {e}")


@app.get("/")
def home():
    return {"message": "Sales and Inventory API is running"}
