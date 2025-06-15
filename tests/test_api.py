from unittest.mock import patch, Mock, MagicMock, AsyncMock
import pytest
from datetime import datetime


@pytest.mark.skip(reason="Needs provider implementation to be completed")
def test_get_latest_price(client):
    """Test getting latest price - skipped until providers are implemented"""
    pass


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