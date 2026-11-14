from contextlib import asynccontextmanager
from fastapi import FastAPI
from backend.config.database import init_db, close_connection_pool
from backend.routes import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Run auto-migrations and establish connection pool
    init_db()

    yield

    # Graceful Shutdown: Close connection pool and clean up sockets
    print("Application is shutting down. Cleaning up resources...")
    close_connection_pool()


app = FastAPI(
    title="Sales and Inventory Management System",
    version="1.0.0",
    lifespan=lifespan
)

# Single entry point for all API routes
app.include_router(api_router)


@app.get("/")
def home():
    return {"message": "Sales and Inventory API is running"}
