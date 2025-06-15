import yfinance as yf
from typing import Dict, Any
from .base import BaseProvider
import asyncio


class YFinanceProvider(BaseProvider):
    def get_provider_name(self) -> str:
        return "yfinance"

    async def get_latest_price(self, symbol: str) -> Dict[str, Any]:
        """Fetch latest price using yfinance"""

        def _fetch_price():
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="1d", interval="1m")
            if hist.empty:
                raise ValueError(f"No data found for symbol {symbol}")

            latest_price = hist["Close"].iloc[-1]
            return {"price": float(latest_price), "raw_data": hist.tail(1).to_dict()}

        # Run in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, _fetch_price)

        return self.format_response(
            symbol=symbol, price=result["price"], raw_data=result["raw_data"]
        )
