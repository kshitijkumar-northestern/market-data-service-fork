import httpx
from typing import Dict, Any
from .base import BaseProvider
from app.core.config import settings


class AlphaVantageProvider(BaseProvider):
    """Alpha Vantage API provider for fetching stock market data."""
    
    def __init__(self):
        """Initialize provider and validate API key is configured."""
        self.api_key = settings.ALPHA_VANTAGE_API_KEY
        if not self.api_key:
            raise ValueError("Alpha Vantage API key not configured")

    def get_provider_name(self) -> str:
        """Return provider identifier."""
        return "alpha_vantage"

    async def get_latest_price(self, symbol: str) -> Dict[str, Any]:
        """
        Fetch latest stock price from Alpha Vantage API.
        
        Args:
            symbol: Stock symbol (e.g., "AAPL")
            
        Returns:
            Formatted price data with symbol, price, timestamp, provider
        """
        # Alpha Vantage GLOBAL_QUOTE endpoint
        url = "https://www.alphavantage.co/query"
        params = {"function": "GLOBAL_QUOTE", "symbol": symbol, "apikey": self.api_key}

        # Make API request
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            # Check for API errors
            if "Error Message" in data:
                raise ValueError(f"API Error: {data['Error Message']}")

            # Validate response format
            if "Global Quote" not in data:
                raise ValueError(f"Unexpected API response format")

            # Extract price from response
            quote = data["Global Quote"]
            price = float(quote["05. price"])

            # Return standardized format
            return self.format_response(symbol=symbol, price=price, raw_data=data)