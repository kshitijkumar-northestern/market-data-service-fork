from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Market Data Service"
    
    # Database
    DATABASE_URL: str = "postgresql://postgres:password@localhost:5432/marketdata"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # Kafka
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"
    KAFKA_TOPIC_PRICE_EVENTS: str = "price-events"
    
    # Market Data Providers
    ALPHA_VANTAGE_API_KEY: Optional[str] = None
    DEFAULT_PROVIDER: str = "yfinance"
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # Polling
    DEFAULT_POLL_INTERVAL: int = 60
    
    class Config:
        env_file = ".env"

settings = Settings()
