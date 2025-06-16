from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime


class BaseProvider(ABC):
    """
    Abstract base class for all market data providers.
    
    Defines the interface that all data providers (Yahoo Finance, Alpha Vantage, etc.)
    must implement to ensure consistent behavior across different data sources.
    """
    
    @abstractmethod
    async def get_latest_price(self, symbol: str) -> Dict[str, Any]:
        """
        Fetch latest price for a stock symbol.
        
        Args:
            symbol: Stock symbol (e.g., "AAPL", "MSFT")
            
        Returns:
            Dict containing price data in standardized format
        """
        pass

    @abstractmethod
    def get_provider_name(self) -> str:
        """
        Return the provider identifier string.
        
        Returns:
            Provider name (e.g., "yfinance", "alpha_vantage")
        """
        pass

    def format_response(
        self, symbol: str, price: float, raw_data: Any
    ) -> Dict[str, Any]:
        """
        Format provider response to standardized format.
        
        Ensures all providers return consistent data structure regardless
        of their internal API response format.
        
        Args:
            symbol: Stock symbol
            price: Current price as float
            raw_data: Original API response for debugging
            
        Returns:
            Standardized response with symbol, price, timestamp, provider, raw_data
        """
        return {
            "symbol": symbol.upper(),               # Normalize symbol to uppercase
            "price": price,                         # Current stock price
            "timestamp": datetime.utcnow(),         # When data was fetched
            "provider": self.get_provider_name(),   # Which provider supplied data
            "raw_data": raw_data,                   # Original API response
        }