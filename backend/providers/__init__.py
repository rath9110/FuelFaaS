"""Provider package for fuel card integrations."""

from .base import BaseProviderClient, ProviderError, AuthenticationError
from .okq8 import OKQ8Provider
from .preem import PreemProvider
from .shell import ShellProvider
from .circlek import CircleKProvider

__all__ = [
    "BaseProviderClient",
    "ProviderError",
    "AuthenticationError",
    "OKQ8Provider",
    "PreemProvider",
    "ShellProvider",
    "CircleKProvider",
]

# Provider registry
PROVIDERS = {
    "okq8": OKQ8Provider,
    "preem": PreemProvider,
    "shell": ShellProvider,
    "circlek": CircleKProvider,
}


def get_provider(provider_name: str, credentials: dict) -> BaseProviderClient:
    """Get a provider instance by name."""
    provider_class = PROVIDERS.get(provider_name.lower())
    if not provider_class:
        raise ValueError(f"Unknown provider: {provider_name}")
    return provider_class(credentials)
