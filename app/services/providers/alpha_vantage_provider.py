import httpx
from typing import Dict, Any
from .base import BaseProvider
from app.core.config import settings


class AlphaVantageProvider(BaseProvider):
    def __init__(self):
        self.api_key = settings.ALPHA_VANTAGE_API_KEY
        if not self.api_key:
            raise ValueError("Alpha Vantage API key not configured")

    def get_provider_name(self) -> str:
        return "alpha_vantage"

    async def get_latest_price(self, symbol: str) -> Dict[str, Any]:
        """Fetch latest price using Alpha Vantage API"""
        url = "https://www.alphavantage.co/query"
        params = {"function": "GLOBAL_QUOTE", "symbol": symbol, "apikey": self.api_key}

        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            response.raise_for_status()

            data = response.json()

            if "Error Message" in data:
                raise ValueError(f"API Error: {data['Error Message']}")

            if "Global Quote" not in data:
                raise ValueError(f"Unexpected API response format")

            quote = data["Global Quote"]
            price = float(quote["05. price"])

            return self.format_response(symbol=symbol, price=price, raw_data=data)
