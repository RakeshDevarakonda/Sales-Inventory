from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.config.settings import CORS_ORIGINS
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

# Register CORS Middleware dynamically from CORS_ORIGINS environment variable
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Global Exception Handlers
register_error_handlers(app)

# Single entry point for all API routes
app.include_router(api_router)


@app.get("/")
def home():
    return {"message": "Sales and Inventory API is running"}
