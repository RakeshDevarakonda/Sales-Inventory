from fastapi import APIRouter
from backend.routes.health_routes import router as health_router
from backend.routes.auth_routes import router as auth_router
from backend.routes.user_routes import router as user_router
from backend.routes.customer_routes import router as customer_router
from backend.routes.product_routes import router as product_router
from backend.routes.inventory_routes import router as inventory_router
from backend.routes.order_routes import router as order_router
from backend.routes.dashboard_routes import router as dashboard_router

api_router = APIRouter()

api_router.include_router(health_router)
api_router.include_router(auth_router)
api_router.include_router(user_router)
api_router.include_router(customer_router)
api_router.include_router(product_router)
api_router.include_router(inventory_router)
api_router.include_router(order_router)
api_router.include_router(dashboard_router)
