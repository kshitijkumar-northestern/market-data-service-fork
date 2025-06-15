import pytest
from app.services.market_service import MarketService

def test_calculate_moving_average():
    """Test moving average calculation"""
    service = MarketService(None, None)
    
    # Test with exactly 5 prices
    prices = [100, 101, 99, 102, 98]
    result = service.calculate_moving_average(prices)
    expected = sum(prices) / len(prices)
    assert result == expected
    
    # Test with more than 5 prices
    prices = [100, 101, 99, 102, 98, 103, 97]
    result = service.calculate_moving_average(prices, period=5)
    expected = sum(prices[-5:]) / 5
    assert result == expected
    
    # Test with less than 5 prices
    prices = [100, 101, 99]
    result = service.calculate_moving_average(prices, period=5)
    expected = sum(prices) / len(prices)
    assert result == expected