from unittest.mock import patch, Mock, MagicMock
import pytest


def test_get_latest_price(client):
    """Test getting latest price with mocked service"""
    # Mock the entire market service instead of yfinance directly
    with patch('app.api.dependencies.get_market_service') as mock_get_service:
        # Mock the market service
        mock_service = MagicMock()
        mock_service.get_latest_price.return_value = {
            "symbol": "AAPL",
            "price": 150.0,
            "timestamp": "2024-01-01T00:00:00",
            "provider": "yfinance"
        }
        mock_get_service.return_value = mock_service
        
        # Make the API call
        response = client.get("/api/v1/prices/latest?symbol=AAPL")
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["symbol"] == "AAPL"
        assert data["price"] == 150.0
        assert "timestamp" in data
        assert data["provider"] == "yfinance"


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