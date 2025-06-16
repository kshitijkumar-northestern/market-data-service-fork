import json
import asyncio
from typing import Dict, Any, Optional, Callable, Awaitable
from confluent_kafka import Producer, Consumer, KafkaError
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class KafkaService:
    """
    Kafka messaging service for producing and consuming price events.
    
    Handles real-time message streaming between API and background processors.
    Uses lazy initialization for producer/consumer instances.
    """
    
    def __init__(self):
        """Initialize Kafka configurations for producer and consumer."""
        # Producer configuration for publishing price events
        self.producer_config = {
            "bootstrap.servers": settings.KAFKA_BOOTSTRAP_SERVERS,
            "client.id": "market-data-producer",
        }
        
        # Consumer configuration for processing price events
        self.consumer_config = {
            "bootstrap.servers": settings.KAFKA_BOOTSTRAP_SERVERS,
            "group.id": "market-data-consumers",
            "auto.offset.reset": "earliest",  # Start from beginning if no offset
        }
        
        # Lazy initialization - created when first needed
        self.producer: Optional[Producer] = None
        self.consumer: Optional[Consumer] = None

    def get_producer(self) -> Producer:
        """Get or create Kafka producer instance (lazy initialization)."""
        if not self.producer:
            self.producer = Producer(self.producer_config)
        return self.producer

    def get_consumer(self) -> Consumer:
        """Get or create Kafka consumer instance (lazy initialization)."""
        if not self.consumer:
            self.consumer = Consumer(self.consumer_config)
        return self.consumer

    async def produce_price_event(self, message: Dict[str, Any]) -> None:
        """
        Publish price event to Kafka topic.
        
        Args:
            message: Price data containing symbol, price, timestamp, etc.
        """
        producer = self.get_producer()
        
        def delivery_callback(err, msg):
            """Callback to handle message delivery confirmation."""
            if err:
                logger.error(f"Failed to deliver message: {err}")
            else:
                logger.info(f"Message delivered to {msg.topic()} [{msg.partition()}]")

        try:
            # Publish message to price-events topic
            producer.produce(
                topic=settings.KAFKA_TOPIC_PRICE_EVENTS,
                key=message.get("symbol", "").encode("utf-8"),     # Use symbol as key for partitioning
                value=json.dumps(message, default=str).encode("utf-8"),  # JSON serialize message
                callback=delivery_callback,
            )
            # Wait for message to be delivered
            producer.flush(timeout=1.0)
        except Exception as e:
            logger.error(f"Error producing message: {e}")
            raise

    async def consume_price_events(
        self, callback: Callable[[Dict[str, Any]], Awaitable[None]]
    ) -> None:
        """
        Consume price events from Kafka topic.
        
        Args:
            callback: Async function to process each message
        """
        consumer = self.get_consumer()
        # Subscribe to price events topic
        consumer.subscribe([settings.KAFKA_TOPIC_PRICE_EVENTS])

        try:
            while True:
                # Poll for new messages
                msg = consumer.poll(timeout=1.0)

                if msg is None:
                    continue  # No message available

                # Check for consumer errors
                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        continue  # End of partition, not an error
                    else:
                        logger.error(f"Consumer error: {msg.error()}")
                        break

                try:
                    # Deserialize and process message
                    message_data = json.loads(msg.value().decode("utf-8"))
                    await callback(message_data)  # Call async callback
                except Exception as e:
                    logger.error(f"Error processing message: {e}")

        except Exception as e:
            logger.error(f"Consumer error: {e}")
        finally:
            consumer.close()

    def close(self):
        """Clean up producer and consumer connections."""
        if self.producer:
            self.producer.flush()  # Ensure all messages are sent
        if self.consumer:
            self.consumer.close()