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
    """
    Core business logic service for market data operations.
    
    Orchestrates data fetching, storage, and messaging between different
    components of the system.
    """
    
    def __init__(self, db: Session, kafka_service: KafkaService):
        """Initialize service with database and Kafka dependencies."""
        self.db = db
        self.kafka_service = kafka_service

    async def get_latest_price(self, symbol: str, provider: str = "yfinance") -> dict:
        """
        Fetch, store, and return latest price for a stock symbol.
        
        Args:
            symbol: Stock symbol to fetch (e.g., "AAPL")
            provider: Data provider to use ("yfinance", "alpha_vantage")
            
        Returns:
            Dict with symbol, price, timestamp, and provider
        """
        # Fetch price data from external provider
        provider_instance = get_provider(provider)
        price_data = await provider_instance.get_latest_price(symbol)

        # Store complete raw API response for audit trail
        raw_response = RawMarketResponse(
            symbol=symbol.upper(),
            provider=provider,
            raw_response=json.dumps(price_data["raw_data"]),
        )
        self.db.add(raw_response)
        self.db.flush()  # Get ID without committing transaction

        # Store processed price point for fast queries
        price_point = PricePoint(
            symbol=symbol.upper(),
            price=price_data["price"],
            timestamp=price_data["timestamp"],
            provider=provider,
            raw_response_id=raw_response.id,
        )
        self.db.add(price_point)
        self.db.commit()  # Commit both records

        # Publish price event to Kafka for real-time processing
        kafka_message = {
            "symbol": symbol.upper(),
            "price": price_data["price"],
            "timestamp": price_data["timestamp"].isoformat(),
            "source": provider,
            "raw_response_id": str(raw_response.id),
        }
        await self.kafka_service.produce_price_event(kafka_message)

        # Return clean response to client
        return {
            "symbol": symbol.upper(),
            "price": price_data["price"],
            "timestamp": price_data["timestamp"],
            "provider": provider,
        }

    def create_polling_job(
        self, symbols: List[str], interval: int, provider: str
    ) -> dict:
        """
        Create background polling job for multiple symbols.
        
        Args:
            symbols: List of stock symbols to poll
            interval: Polling interval in seconds
            provider: Data provider to use
            
        Returns:
            Dict with job_id, status, and configuration
        """
        # Generate unique job identifier
        job_id = f"poll_{uuid.uuid4().hex[:8]}"

        # Store job configuration in database
        polling_job = PollingJob(
            job_id=job_id,
            symbols=json.dumps(symbols),  # Store symbols as JSON array
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
        """
        Calculate moving average for a list of prices.
        
        Args:
            prices: List of price values
            period: Number of periods for moving average
            
        Returns:
            Calculated moving average value
        """
        # If not enough data, use simple average
        if len(prices) < period:
            return sum(prices) / len(prices)
        
        # Calculate moving average using last N periods
        return sum(prices[-period:]) / period

    async def get_moving_average(self, symbol: str, period: int = 5) -> Optional[dict]:
        """
        Retrieve latest moving average for a symbol.
        
        Args:
            symbol: Stock symbol
            period: Moving average period
            
        Returns:
            Moving average data or None if not found
        """
        # Query latest moving average from database
        moving_avg = (
            self.db.query(MovingAverage)
            .filter(
                MovingAverage.symbol == symbol.upper(), 
                MovingAverage.period == period
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