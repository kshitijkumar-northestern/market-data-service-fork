from fastapi import Depends
from sqlalchemy.orm import Session
from app.models.database import get_db
from app.services.kafka_service import KafkaService
from app.services.market_service import MarketService

# Global Kafka service instance
kafka_service = KafkaService()

def get_kafka_service() -> KafkaService:
    return kafka_service

def get_market_service(
    db: Session = Depends(get_db),
    kafka_service: KafkaService = Depends(get_kafka_service)
) -> MarketService:
    return MarketService(db, kafka_service)