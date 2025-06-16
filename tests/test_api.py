import pytest

def test_health_endpoint(client):
    """Test health endpoint returns 200"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data

def test_price_endpoint_exists(client):
    """Test that price endpoint exists"""
    response = client.get("/prices/latest?symbol=AAPL")
    # Should not return 404 (route not found)
    assert response.status_code != 404

def test_poll_endpoint_exists(client):
    """Test that poll endpoint exists"""
    response = client.post("/prices/poll", json={
        "symbols": ["AAPL"],
        "interval": 60
    })
    # Should not return 404 (route not found)
    assert response.status_code != 404
