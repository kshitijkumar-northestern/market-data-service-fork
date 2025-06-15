import asyncio
import json
from typing import Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models.database import SessionLocal
from app.models.market_data import PricePoint, MovingAverage
from app.services.kafka_service import KafkaService
from app.services.market_service import MarketService
import logging

logger = logging.getLogger(__name__)


class MovingAverageConsumer:
    def __init__(self):
        self.kafka_service = KafkaService()
        self.market_service = MarketService(
            None, self.kafka_service
        )  # DB will be injected per message

    async def process_price_event(self, message: Dict[str, Any]) -> None:
        """Process a price event and calculate moving average"""
        db = SessionLocal()
        try:
            symbol = message.get("symbol")
            if not symbol:
                logger.warning("Message missing symbol field")
                return

            # Get last 5 price points for this symbol
            recent_prices = (
                db.query(PricePoint)
                .filter(PricePoint.symbol == symbol)
                .order_by(desc(PricePoint.timestamp))
                .limit(5)
                .all()
            )

            if len(recent_prices) < 2:  # Need at least 2 points for MA
                logger.info(f"Not enough data points for {symbol} moving average")
                return

            # Calculate 5-point moving average
            prices = [
                p.price for p in reversed(recent_prices)
            ]  # Reverse to get chronological order
            ma_value = self.market_service.calculate_moving_average(prices, period=5)

            # Store moving average
            moving_avg = MovingAverage(symbol=symbol, period=5, average_value=ma_value)

            db.add(moving_avg)
            db.commit()

            logger.info(f"Calculated MA for {symbol}: {ma_value}")

        except Exception as e:
            logger.error(f"Error processing price event: {e}")
            db.rollback()
        finally:
            db.close()

    async def start_consuming(self):
        """Start consuming price events"""
        logger.info("Starting Moving Average Consumer...")
        await self.kafka_service.consume_price_events(self.process_price_event)


# Standalone consumer script
async def main():
    consumer = MovingAverageConsumer()
    await consumer.start_consuming()


if __name__ == "__main__":
    asyncio.run(main())
