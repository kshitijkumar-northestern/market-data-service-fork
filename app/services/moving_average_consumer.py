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
    """
    Kafka consumer that processes price events and calculates moving averages.
    
    Runs as a background service, listening for price updates and computing
    5-point moving averages for real-time technical analysis.
    """
    
    def __init__(self):
        """Initialize consumer with Kafka service and market service."""
        self.kafka_service = KafkaService()
        # MarketService initialized without DB - will create per message
        self.market_service = MarketService(None, self.kafka_service)

    async def process_price_event(self, message: Dict[str, Any]) -> None:
        """
        Process incoming price event and calculate moving average.
        
        Args:
            message: Kafka message containing price data
        """
        # Create new database session for this message
        db = SessionLocal()
        try:
            # Extract symbol from message
            symbol = message.get("symbol")
            if not symbol:
                logger.warning("Message missing symbol field")
                return

            # Get last 5 price points for moving average calculation
            recent_prices = (
                db.query(PricePoint)
                .filter(PricePoint.symbol == symbol)
                .order_by(desc(PricePoint.timestamp))  # Most recent first
                .limit(5)
                .all()
            )

            # Need at least 2 points to calculate meaningful average
            if len(recent_prices) < 2:
                logger.info(f"Not enough data points for {symbol} moving average")
                return

            # Convert to price list in chronological order
            prices = [p.price for p in reversed(recent_prices)]
            
            # Calculate 5-point moving average
            ma_value = self.market_service.calculate_moving_average(prices, period=5)

            # Store calculated moving average in database
            moving_avg = MovingAverage(
                symbol=symbol, 
                period=5, 
                average_value=ma_value
            )
            db.add(moving_avg)
            db.commit()

            logger.info(f"Calculated MA for {symbol}: {ma_value}")

        except Exception as e:
            logger.error(f"Error processing price event: {e}")
            db.rollback()  # Rollback on error
        finally:
            db.close()  # Always close database connection

    async def start_consuming(self):
        """Start the Kafka consumer to process price events."""
        logger.info("Starting Moving Average Consumer...")
        await self.kafka_service.consume_price_events(self.process_price_event)


# Standalone consumer script
async def main():
    """Main function to run the moving average consumer."""
    consumer = MovingAverageConsumer()
    await consumer.start_consuming()


if __name__ == "__main__":
    # Run consumer as standalone application
    asyncio.run(main())