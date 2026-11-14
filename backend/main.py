from contextlib import asynccontextmanager
from fastapi import FastAPI
from backend.config.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Run auto-migrations. Fail fast if database cannot connect.
    init_db()

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
