from unittest.mock import patch, Mock, MagicMock
import pytest
from fastapi.testclient import TestClient


@patch('app.services.providers.yfinance_provider.yf.Ticker')
def test_get_latest_price(mock_ticker, client):
    """Test getting latest price"""
    # Mock yfinance response properly
    mock_hist = MagicMock()
    mock_hist.empty = False
    
    # Mock the DataFrame-like behavior
    mock_close_data = MagicMock()
    mock_close_data.iloc = MagicMock()
    mock_close_data.iloc.__getitem__.return_value = 150.0  # Mock price
    
    # Set up the mock chain properly
    mock_hist.__getitem__ = MagicMock(return_value=mock_close_data)
    
    # Configure the ticker mock
    mock_ticker_instance = MagicMock()
    mock_ticker_instance.history.return_value = mock_hist
    mock_ticker.return_value = mock_ticker_instance
    
    # Make the API call
    response = client.get("/api/v1/prices/latest?symbol=AAPL")
    
    # Assertions
    assert response.status_code == 200
    data = response.json()
    assert data["symbol"] == "AAPL"
    assert "price" in data
    assert "timestamp" in data
    assert "provider" in data


def test_health_endpoint(client):
    """Test health endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "timestamp" in data
    assert "database" in data