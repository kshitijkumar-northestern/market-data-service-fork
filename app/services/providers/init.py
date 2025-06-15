from .base import BaseProvider
from .yfinance_provider import YFinanceProvider
from .alpha_vantage_provider import AlphaVantageProvider

PROVIDERS = {
    "yfinance": YFinanceProvider,
    "alpha_vantage": AlphaVantageProvider,
}


def get_provider(provider_name: str) -> BaseProvider:
    if provider_name not in PROVIDERS:
        raise ValueError(f"Unknown provider: {provider_name}")
    return PROVIDERS[provider_name]()
