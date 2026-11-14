from contextlib import asynccontextmanager
from fastapi import FastAPI
from backend.config.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Run auto-migrations
    try:
        init_db()
    except Exception as e:
        print(f"Database initialization failed: {e}")

    yield

    # Graceful Shutdown
    print("Application is shutting down. Cleaning up resources...")


app = FastAPI(
    title="Sales and Inventory Management System",
    version="1.0.0",
    lifespan=lifespan
)


@app.get("/")
def home():
    return {"message": "Sales and Inventory API is running"}
