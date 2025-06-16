from fastapi import APIRouter
from app.api.endpoints.health import router as health_router
from app.api.endpoints.prices import router as prices_router

api_router = APIRouter()

# Include routers
api_router.include_router(health_router, tags=["health"])
api_router.include_router(prices_router, prefix="/prices", tags=["prices"])
