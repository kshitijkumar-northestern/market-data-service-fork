import json
from typing import Optional, List
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.models.market_data import (
    PricePoint,
    RawMarketResponse,
    MovingAverage,
    PollingJob,
)
from app.services.providers import get_provider
from app.services.kafka_service import KafkaService
import uuid


class MarketService:
    def __init__(self, db: Session, kafka_service: KafkaService):
        self.db = db
        self.kafka_service = kafka_service

    async def get_latest_price(self, symbol: str, provider: str = "yfinance") -> dict:
        """Get latest price for a symbol"""
        # Fetch from provider
        provider_instance = get_provider(provider)
        price_data = await provider_instance.get_latest_price(symbol)

        # Store raw response
        raw_response = RawMarketResponse(
            symbol=symbol.upper(),
            provider=provider,
            raw_response=json.dumps(price_data["raw_data"]),
        )
        self.db.add(raw_response)
        self.db.flush()

        # Store processed price point
        price_point = PricePoint(
            symbol=symbol.upper(),
            price=price_data["price"],
            timestamp=price_data["timestamp"],
            provider=provider,
            raw_response_id=raw_response.id,
        )
        self.db.add(price_point)
        self.db.commit()

        # Publish to Kafka
        kafka_message = {
            "symbol": symbol.upper(),
            "price": price_data["price"],
            "timestamp": price_data["timestamp"].isoformat(),
            "source": provider,
            "raw_response_id": str(raw_response.id),
        }
        await self.kafka_service.produce_price_event(kafka_message)

        return {
            "symbol": symbol.upper(),
            "price": price_data["price"],
            "timestamp": price_data["timestamp"],
            "provider": provider,
        }

    def create_polling_job(
        self, symbols: List[str], interval: int, provider: str
    ) -> dict:
        """Create a new polling job"""
        job_id = f"poll_{uuid.uuid4().hex[:8]}"

        polling_job = PollingJob(
            job_id=job_id,
            symbols=json.dumps(symbols),
            interval=interval,
            provider=provider,
        )

        self.db.add(polling_job)
        self.db.commit()

        return {
            "job_id": job_id,
            "status": "accepted",
            "config": {"symbols": symbols, "interval": interval, "provider": provider},
        }

    def calculate_moving_average(self, prices: List[float], period: int = 5) -> float:
        """Calculate moving average for given prices"""
        if len(prices) < period:
            return sum(prices) / len(prices)
        return sum(prices[-period:]) / period

    async def get_moving_average(self, symbol: str, period: int = 5) -> Optional[dict]:
        """Get latest moving average for a symbol"""
        moving_avg = (
            self.db.query(MovingAverage)
            .filter(
                MovingAverage.symbol == symbol.upper(), MovingAverage.period == period
            )
            .order_by(MovingAverage.timestamp.desc())
            .first()
        )

        if not moving_avg:
            return None

        return {
            "symbol": moving_avg.symbol,
            "period": moving_avg.period,
            "average_value": moving_avg.average_value,
            "timestamp": moving_avg.timestamp,
        }
