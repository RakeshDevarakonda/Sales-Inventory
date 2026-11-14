from contextlib import asynccontextmanager
from fastapi import FastAPI
from backend.config.database import check_database_connectivity, close_connection_pool
from backend.routes import api_router
from backend.handlers.error_handlers import register_error_handlers


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Verify database connection without running DDL
    print("Verifying database connectivity...")
    check_database_connectivity()
    print("Database connected successfully.")

    yield

    # Graceful Shutdown: Close connection pool and clean up sockets
    print("Application is shutting down. Cleaning up resources...")
    close_connection_pool()


app = FastAPI(
    title="Sales and Inventory Management System",
    version="1.0.0",
    lifespan=lifespan
)

# Register Global Exception Handlers
register_error_handlers(app)

# Single entry point for all API routes
app.include_router(api_router)


@app.get("/")
def home():
    return {"message": "Sales and Inventory API is running"}
