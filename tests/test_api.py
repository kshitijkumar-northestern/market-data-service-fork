from unittest.mock import patch, Mock, MagicMock, AsyncMock
import pytest
from datetime import datetime


def test_get_latest_price(client):
    """Test getting latest price with comprehensive mocking"""
    # Mock all the dependencies that might be causing issues
    with patch.multiple(
        'app.api.dependencies',
        get_market_service=MagicMock(),
        get_kafka_service=MagicMock()
    ) as mocks:
        
        # Create a mock market service
        mock_service = MagicMock()
        mock_timestamp = datetime(2024, 1, 1, 0, 0, 0)
        
        # Mock the async get_latest_price method
        async def mock_get_latest_price(symbol, provider="yfinance"):
            return {
                "symbol": symbol.upper(),
                "price": 150.0,
                "timestamp": mock_timestamp,
                "provider": provider
            }
        
        mock_service.get_latest_price = mock_get_latest_price
        mocks['get_market_service'].return_value = mock_service
        
        # Make the API call
        response = client.get("/api/v1/prices/latest?symbol=AAPL")
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["symbol"] == "AAPL"
        assert data["price"] == 150.0
        assert "timestamp" in data
        assert data["provider"] == "yfinance"


def test_get_latest_price_with_provider(client):
    """Test getting latest price with specific provider"""
    with patch.multiple(
        'app.api.dependencies',
        get_market_service=MagicMock(),
        get_kafka_service=MagicMock()
    ) as mocks:
        
        mock_service = MagicMock()
        mock_timestamp = datetime(2024, 1, 1, 0, 0, 0)
        
        async def mock_get_latest_price(symbol, provider="yfinance"):
            return {
                "symbol": symbol.upper(),
                "price": 200.0,
                "timestamp": mock_timestamp,
                "provider": provider
            }
        
        mock_service.get_latest_price = mock_get_latest_price
        mocks['get_market_service'].return_value = mock_service
        
        # Test with custom provider
        response = client.get("/api/v1/prices/latest?symbol=TSLA&provider=custom")
        
        assert response.status_code == 200
        data = response.json()
        assert data["symbol"] == "TSLA"
        assert data["price"] == 200.0
        assert data["provider"] == "custom"


def test_create_polling_job(client):
    """Test creating a polling job"""
    with patch.multiple(
        'app.api.dependencies',
        get_market_service=MagicMock(),
        get_kafka_service=MagicMock()
    ) as mocks:
        
        mock_service = MagicMock()
        
        # Mock the create_polling_job method (this one is sync)
        mock_service.create_polling_job.return_value = {
            "job_id": "poll_12345678",
            "status": "accepted",
            "config": {
                "symbols": ["AAPL", "GOOGL"],
                "interval": 60,
                "provider": "yfinance"
            }
        }
        
        mocks['get_market_service'].return_value = mock_service
        
        # Make the API call
        response = client.post("/api/v1/prices/poll", json={
            "symbols": ["AAPL", "GOOGL"],
            "interval": 60,
            "provider": "yfinance"
        })
        
        assert response.status_code == 202
        data = response.json()
        assert data["status"] == "accepted"
        assert "job_id" in data
        assert data["config"]["symbols"] == ["AAPL", "GOOGL"]


def test_health_endpoint(client):
    """Test health endpoint"""
    # Try the correct health endpoint path
    response = client.get("/api/v1/health")
    
    # If that fails, try the root health path
    if response.status_code == 404:
        response = client.get("/health")
    
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "timestamp" in data
    assert "database" in data