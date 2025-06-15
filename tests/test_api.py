import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock

def test_health_endpoint(client):
    """Test health check endpoint"""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "timestamp" in data

@patch('app.services.providers.yfinance_provider.yf.Ticker')
def test_get_latest_price(mock_ticker, client):
    """Test getting latest price"""
    # Mock yfinance response
    mock_hist = Mock()
    mock_hist.empty = False
    mock_hist.__getitem__.return_value.iloc = Mock()
    mock_hist.__getitem__.return_value.iloc.__getitem__.return_value = 150.25
    mock_hist.tail.return_value.to_dict.return_value = {"Close": {0: 150.25}}
    
    mock_ticker.return_value.history.return_value = mock_hist
    
    response = client.get("/api/v1/prices/latest?symbol=AAPL")
    assert response.status_code == 200
    data = response.json()
    assert data["symbol"] == "AAPL"
    assert "price" in data
    assert "timestamp" in data