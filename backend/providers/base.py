"""Base provider interface for fuel card integrations."""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Dict, Any, Optional
from ..models import FuelTransaction


class ProviderError(Exception):
    """Base exception for provider errors."""
    pass


class AuthenticationError(ProviderError):
    """Authentication failed with provider."""
    pass


class BaseProviderClient(ABC):
    """Abstract base class for fuel card provider clients."""
    
    def __init__(self, credentials: Dict[str, Any]):
        """
        Initialize provider with credentials.
        
        Args:
            credentials: Provider-specific credentials (API keys, tokens, etc.)
        """
        self.credentials = credentials
        self._validated = False
    
    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return the provider name."""
        pass
    
    @abstractmethod
    async def validate_credentials(self) -> bool:
        """
        Validate that credentials are correct and working.
        
        Returns:
            True if credentials are valid
            
        Raises:
            AuthenticationError: If credentials are invalid
        """
        pass
    
    @abstractmethod
    async def fetch_transactions(
        self,
        start_date: datetime,
        end_date: datetime,
        **filters
    ) -> List[Dict[str, Any]]:
        """
        Fetch transactions from provider API.
        
        Args:
            start_date: Start of date range
            end_date: End of date range
            **filters: Additional provider-specific filters
            
        Returns:
            List of raw transaction data from provider
            
        Raises:
            ProviderError: If API call fails
        """
        pass
    
    @abstractmethod
    def normalize_transaction(self, raw_data: Dict[str, Any]) -> FuelTransaction:
        """
        Convert provider-specific transaction format to standard format.
        
        Args:
            raw_data: Raw transaction data from provider
            
        Returns:
            Normalized FuelTransaction object
        """
        pass
    
    async def get_transactions(
        self,
        start_date: datetime,
        end_date: datetime,
        **filters
    ) -> List[FuelTransaction]:
        """
        Fetch and normalize transactions.
        
        This is the main entry point for getting transactions.
        
        Args:
            start_date: Start of date range
            end_date: End of date range
            **filters: Additional provider-specific filters
            
        Returns:
            List of normalized FuelTransaction objects
        """
        if not self._validated:
            await self.validate_credentials()
            self._validated = True
        
        raw_transactions = await self.fetch_transactions(start_date, end_date, **filters)
        return [self.normalize_transaction(tx) for tx in raw_transactions]
