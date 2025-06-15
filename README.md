# market-data-service-main

Complete implementation of the Market Data Service microservice with all required functionality working end-to-end.

- FastAPI REST endpoints (`/prices/latest`, `/prices/poll`, `/health`)
- PostgreSQL database with Alembic migrations
- Apache Kafka integration for real-time streaming
- Docker containerization with docker-compose
- Yahoo Finance integration for market data
- Moving average calculations (ready for Kafka consumer)
- Comprehensive error handling and logging

How to Test
```bash
docker-compose up --build
curl http://localhost:8000/api/v1/health
curl "http://localhost:8000/api/v1/prices/latest?symbol=AAPL"
open http://localhost:8000/docs
