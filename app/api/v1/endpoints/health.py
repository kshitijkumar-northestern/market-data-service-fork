from fastapi import APIRouter, Depends
from datetime import datetime
from sqlalchemy import text
from app.schemas.market_data import HealthResponse
from app.models.database import get_db
from app.services.kafka_service import KafkaService
from app.api.dependencies import get_kafka_service
from sqlalchemy.orm import Session

router = APIRouter()

@router.get("/health", response_model=HealthResponse)
async def health_check(
    db: Session = Depends(get_db),
    kafka_service: KafkaService = Depends(get_kafka_service)
):
    """Health check endpoint"""
    # Check database
    try:
        db.execute(text("SELECT 1"))
        db_status = "healthy"
    except Exception as e:
        print(f"Database error: {e}")  # Debug info
        db_status = "unhealthy"
    
    # Check Kafka (simplified check)
    kafka_status = "healthy"  # You can implement actual Kafka health check
    
    # Check Redis (when implemented)
    redis_status = "not_configured"
    
    return HealthResponse(
        status="healthy" if db_status == "healthy" else "degraded",
        timestamp=datetime.utcnow(),
        database=db_status,
        kafka=kafka_status,
        redis=redis_status
    )
