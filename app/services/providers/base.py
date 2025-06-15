from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime


class BaseProvider(ABC):
    @abstractmethod
    async def get_latest_price(self, symbol: str) -> Dict[str, Any]:
        """Fetch latest price for a symbol"""
        pass

    @abstractmethod
    def get_provider_name(self) -> str:
        """Return provider name"""
        pass

    def format_response(
        self, symbol: str, price: float, raw_data: Any
    ) -> Dict[str, Any]:
        """Format response to standard format"""
        return {
            "symbol": symbol.upper(),
            "price": price,
            "timestamp": datetime.utcnow(),
            "provider": self.get_provider_name(),
            "raw_data": raw_data,
        }
