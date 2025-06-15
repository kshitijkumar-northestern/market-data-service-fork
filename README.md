# Market Data Service

A production-ready microservice for fetching, processing, and serving real-time market data with Kafka streaming and moving average calculations.

## Quick Start

```bash
# Start all services
docker-compose up --build

# Test endpoints
curl http://localhost:8000/api/v1/health
curl "http://localhost:8000/api/v1/prices/latest?symbol=AAPL"

# View API documentation
open http://localhost:8000/docs
```

## API Endpoints

### Get Latest Price
```http
GET /api/v1/prices/latest?symbol=AAPL&provider=yfinance
```

**Response:**
```json
{
  "symbol": "AAPL",
  "price": 181.45,
  "timestamp": "2024-03-20T15:30:00Z",
  "provider": "yfinance"
}
```

### Create Polling Job
```http
POST /api/v1/prices/poll
Content-Type: application/json

{
  "symbols": ["AAPL", "MSFT"],
  "interval": 60,
  "provider": "yfinance"
}
```

**Response:**
```json
{
  "job_id": "poll_abc123",
  "status": "accepted",
  "config": {
    "symbols": ["AAPL", "MSFT"],
    "interval": 60
  }
}
```

### Health Check
```http
GET /api/v1/health
```

## Development Setup

### Prerequisites
- Docker and Docker Compose
- Python 3.11+ (for local development)

### Local Development
```bash
# Start infrastructure services only
docker-compose up postgres kafka zookeeper redis -d

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements/dev.txt

# Run database migrations
alembic upgrade head

# Start API server
uvicorn app.main:app --reload
```

## Database Schema

**Tables:**
- `raw_market_responses` - Complete API responses with metadata
- `price_points` - Processed price data with timestamps
- `moving_averages` - Calculated 5-point moving averages
- `polling_jobs` - Background job configurations

**Key Indexes:**
- `idx_price_symbol_timestamp` - Optimized price queries
- `idx_ma_symbol_timestamp` - Moving average lookups

## Configuration

**Environment Variables:**
- `DATABASE_URL` - PostgreSQL connection string
- `KAFKA_BOOTSTRAP_SERVERS` - Kafka broker addresses
- `REDIS_URL` - Redis connection string
- `ALPHA_VANTAGE_API_KEY` - Alpha Vantage API key (optional)
- `DEFAULT_PROVIDER` - Default market data provider (yfinance)

## Services

**API Service (Port 8000):**
- FastAPI application with OpenAPI documentation
- Async endpoint handlers with dependency injection
- Comprehensive error handling and logging

**PostgreSQL (Port 5432):**
- Primary data storage with ACID compliance
- Optimized indexes for query performance
- Alembic migrations for schema management

**Apache Kafka (Port 9092):**
- Real-time message streaming
- Price event processing pipeline
- Auto-topic creation enabled

**Redis (Port 6379):**
- Caching layer for frequently accessed data
- Session storage and rate limiting

**Adminer (Port 8080):**
- Database administration interface
- Credentials: postgres/password

## Testing

```bash
# Run test suite
pytest tests/ -v

# Run with coverage
pytest --cov=app --cov-report=html

# Test specific functionality
pytest tests/test_market_service.py -v
```

## Monitoring

**Health Checks:**
- Database connectivity
- Kafka broker status
- External API availability

**Logging:**
- Structured JSON logging
- Request/response tracing
- Error tracking and alerting


