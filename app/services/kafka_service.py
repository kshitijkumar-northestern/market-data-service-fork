import json
import asyncio
from typing import Dict, Any, Optional, Callable
from confluent_kafka import Producer, Consumer, KafkaError
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class KafkaService:
    def __init__(self):
        self.producer_config = {
            'bootstrap.servers': settings.KAFKA_BOOTSTRAP_SERVERS,
            'client.id': 'market-data-producer'
        }
        
        self.consumer_config = {
            'bootstrap.servers': settings.KAFKA_BOOTSTRAP_SERVERS,
            'group.id': 'market-data-consumers',
            'auto.offset.reset': 'earliest'
        }
        
        self.producer: Optional[Producer] = None
        self.consumer: Optional[Consumer] = None
    
    def get_producer(self) -> Producer:
        """Get or create Kafka producer"""
        if not self.producer:
            self.producer = Producer(self.producer_config)
        return self.producer
    
    def get_consumer(self) -> Consumer:
        """Get or create Kafka consumer"""
        if not self.consumer:
            self.consumer = Consumer(self.consumer_config)
        return self.consumer
    
    async def produce_price_event(self, message: Dict[str, Any]) -> None:
        """Produce a price event to Kafka"""
        producer = self.get_producer()
        
        def delivery_callback(err, msg):
            if err:
                logger.error(f"Failed to deliver message: {err}")
            else:
                logger.info(f"Message delivered to {msg.topic()} [{msg.partition()}]")
        
        try:
            producer.produce(
                topic=settings.KAFKA_TOPIC_PRICE_EVENTS,
                key=message.get("symbol", "").encode('utf-8'),
                value=json.dumps(message, default=str).encode('utf-8'),
                callback=delivery_callback
            )
            producer.flush(timeout=1.0)
        except Exception as e:
            logger.error(f"Error producing message: {e}")
            raise
    
    async def consume_price_events(self, callback: Callable[[Dict[str, Any]], None]) -> None:
        """Consume price events from Kafka"""
        consumer = self.get_consumer()
        consumer.subscribe([settings.KAFKA_TOPIC_PRICE_EVENTS])
        
        try:
            while True:
                msg = consumer.poll(timeout=1.0)
                
                if msg is None:
                    continue
                
                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        continue
                    else:
                        logger.error(f"Consumer error: {msg.error()}")
                        break
                
                try:
                    message_data = json.loads(msg.value().decode('utf-8'))
                    await callback(message_data)
                except Exception as e:
                    logger.error(f"Error processing message: {e}")
                    
        except Exception as e:
            logger.error(f"Consumer error: {e}")
        finally:
            consumer.close()
    
    def close(self):
        """Close producer and consumer"""
        if self.producer:
            self.producer.flush()
        if self.consumer:
            self.consumer.close()