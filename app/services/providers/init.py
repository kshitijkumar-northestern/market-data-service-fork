from .base import BaseProvider
from .yfinance_provider import YFinanceProvider
from .alpha_vantage_provider import AlphaVantageProvider

# Registry of available market data providers
# Maps provider names to their implementation classes
PROVIDERS = {
    "yfinance": YFinanceProvider,
    "alpha_vantage": AlphaVantageProvider,
}


def get_provider(provider_name: str) -> BaseProvider:
    """
    Factory function to create provider instances.
    
    Uses the provider registry to instantiate the correct provider
    based on the requested name. Enables easy switching between
    different data sources without changing business logic.
    
    Args:
        provider_name: Name of provider to create ("yfinance", "alpha_vantage")
        
    Returns:
        Instantiated provider object implementing BaseProvider interface
        
    Raises:
        ValueError: If provider_name is not supported
    """
    # Validate provider exists in registry
    if provider_name not in PROVIDERS:
        raise ValueError(f"Unknown provider: {provider_name}")
    
    # Create and return new provider instance
    return PROVIDERS[provider_name]()