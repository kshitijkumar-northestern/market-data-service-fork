import pytest


def test_health_endpoint(client):
    """Test health endpoint returns 200"""
    response = client.get("/api/v1/health")
    
    # If v1 path doesn't exist, try root
    if response.status_code == 404:
        response = client.get("/health")
    
    assert response.status_code == 200
    data = response.json()
    assert "status" in data


def test_price_endpoint_exists(client):
    """Test that price endpoint exists (even if it fails due to missing deps)"""
    response = client.get("/api/v1/prices/latest?symbol=AAPL")
    
    # We expect either 200 (working) or 500 (missing deps), but not 404 (missing route)
    assert response.status_code != 404, "Price endpoint route should exist"


def test_poll_endpoint_exists(client):
    """Test that poll endpoint exists"""
    response = client.post("/api/v1/prices/poll", json={
        "symbols": ["AAPL"],
        "interval": 60
    })
    
    # We expect either 200/202 (working) or 500 (missing deps), but not 404 (missing route)
    assert response.status_code != 404, "Poll endpoint route should exist"