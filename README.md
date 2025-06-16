# Market Data Service

A production-ready microservice for fetching, processing, and serving real-time market data with Kafka streaming and moving average calculations.

## Quick Start

### Docker Deployment
```bash
docker-compose up --build

# Verify service health
curl http://localhost:8000/health

# Test price endpoint
curl "http://localhost:8000/prices/latest?symbol=AAPL"
```

### Local Development
```bash
# Start infrastructure services
docker-compose up postgres kafka zookeeper redis -d

# Setup Python environment
python -m venv venv
source venv/bin/activate
pip install -r requirements/dev.txt

# Start application
python -m app.main

# Start consumer (separate terminal)
python -m app.services.moving_average_consumer
```

## API Reference

### Endpoints

#### Get Latest Price
```http
GET /prices/latest?symbol={symbol}&provider={provider}
```

**Parameters:**
- `symbol` (required): Stock symbol (e.g., AAPL)
- `provider` (optional): Data provider (default: yfinance)

**Response:**
```json
{
  "symbol": "AAPL",
  "price": 181.45,
  "timestamp": "2024-03-20T15:30:00Z",
  "provider": "yfinance"
}
```

#### Create Polling Job
```http
POST /prices/poll
```

**Request Body:**
```json
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
    "interval": 60,
    "provider": "yfinance"
  }
}
```

#### Health Check
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-03-20T15:30:00Z",
  "database": "healthy",
  "kafka": "healthy",
  "redis": "not_configured"
}
```

### Documentation
- Interactive API Documentation: `http://localhost:8000/docs`
- ReDoc Documentation: `http://localhost:8000/redoc`

## Database Schema

### Tables
- **raw_market_responses**: Complete API responses with metadata
- **price_points**: Processed price data with timestamps
- **moving_averages**: Calculated 5-point moving averages
- **polling_jobs**: Background job configurations

### Indexes
- `idx_price_symbol_timestamp`: Optimized price queries
- `idx_ma_symbol_timestamp`: Moving average lookups
- `idx_raw_symbol_timestamp`: Raw data lookups

## Configuration

### Environment Variables
| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://postgres:password@localhost:5432/marketdata` |
| `KAFKA_BOOTSTRAP_SERVERS` | Kafka broker addresses | `localhost:9092` |
| `REDIS_URL` | Redis connection string | `redis://localhost:6379` |
| `ALPHA_VANTAGE_API_KEY` | Alpha Vantage API key | Optional |
| `DEFAULT_PROVIDER` | Default market data provider | `yfinance` |

### Service Ports
| Service | Port | Description |
|---------|------|-------------|
| API | 8000 | FastAPI application |
| PostgreSQL | 5432 | Primary database |
| Kafka | 9092 | Message broker |
| Redis | 6379 | Cache layer |
| Adminer | 8080 | Database admin |

## Testing

### Test Suite
```bash
# Run all tests
pytest tests/ -v

# Run with coverage report
pytest --cov=app --cov-report=html

# Test specific module
pytest tests/test_market_service.py -v
```

### Integration Testing
```bash
# Test complete pipeline
curl "http://localhost:8000/prices/latest?symbol=AAPL"
curl "http://localhost:8000/prices/latest?symbol=MSFT"
curl "http://localhost:8000/prices/latest?symbol=AAPL"
```

## Message Queue

### Kafka Configuration
- **Topic**: `price-events`
- **Replication Factor**: 1
- **Auto-create Topics**: Enabled

### Message Schema
```json
{
  "symbol": "AAPL",
  "price": 150.25,
  "timestamp": "2024-03-20T10:30:00Z",
  "source": "yfinance",
  "raw_response_id": "uuid-here"
}
```

### Consumer Process
1. Consumes price events from `price-events` topic
2. Retrieves last 5 price points for symbol
3. Calculates 5-point moving average
4. Stores result in `moving_averages` table

## Monitoring

### Health Monitoring
```bash
# Database connectivity
python -c "from app.models.database import engine; engine.connect().execute('SELECT 1')"

# Kafka broker status
docker-compose logs kafka

# Application health
curl http://localhost:8000/health
```

### Logging
- Structured logging with configurable levels
- Request/response tracing
- Error tracking and monitoring
- Performance metrics collection

## Troubleshooting

### Database Issues
```bash
# Check PostgreSQL status
docker-compose ps postgres

# View database logs
docker-compose logs postgres

# Connect to database
docker-compose exec postgres psql -U postgres -d marketdata
```

### Kafka Issues
```bash
# Check Kafka status
docker-compose ps kafka

# View Kafka logs
docker-compose logs kafka

# List topics
docker-compose exec kafka kafka-topics --list --bootstrap-server localhost:9092
```

### Application Issues
```bash
# View application logs
docker-compose logs api

# Check service health
curl http://localhost:8000/health

# Verify API routes
curl http://localhost:8000/docs
```

## Production Deployment

### Docker Deployment
```bash
# Build production image
docker build -t market-data-service:latest .

# Deploy with environment configuration
docker run -d \
  --name market-data-api \
  -p 8000:8000 \
  --env-file .env.prod \
  market-data-service:latest
```

### Environment Setup
```bash
# Configure environment
cp .env.example .env

# Edit configuration file
# Update database URLs, API keys, and service endpoints
```

