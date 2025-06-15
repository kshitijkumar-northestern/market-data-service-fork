from fastapi import APIRouter
from app.api.v1.endpoints import prices, health

api_router = APIRouter()
api_router.include_router(prices.router, prefix="/prices", tags=["prices"])
api_router.include_router(health.router, tags=["health"])
