"""OKQ8 fuel card provider implementation (mock for demonstration)."""

from datetime import datetime
from typing import List, Dict, Any
import random
from .base import BaseProviderClient, AuthenticationError, ProviderError
from ..models import FuelTransaction


class OKQ8Provider(BaseProviderClient):
    """OKQ8 fuel card provider client."""
    
    @property
    def provider_name(self) -> str:
        return "okq8"
    
    async def validate_credentials(self) -> bool:
        """
        Validate OKQ8 API credentials.
        
        In production, this would call OKQ8's OAuth2 token endpoint.
        For demo, we just check credentials dict has required keys.
        """
        required_keys = ["client_id", "client_secret"]
        if not all(key in self.credentials for key in required_keys):
            raise AuthenticationError(
                f"Missing required credentials for OKQ8: {required_keys}"
            )
        
        # Mock validation - in production, would call real API
        if self.credentials.get("client_id") == "invalid":
            raise AuthenticationError("Invalid OKQ8 credentials")
        
        return True
    
    async def fetch_transactions(
        self,
        start_date: datetime,
        end_date: datetime,
        **filters
    ) -> List[Dict[str, Any]]:
        """
        Fetch transactions from OKQ8 API.
        
        In production, this would call:
        GET https://api.okq8.se/v1/transactions?start_date=X&end_date=Y
        
        For demo, we return mock data.
        """
        # Mock API response data
        mock_transactions = [
            {
                "transactionId": f"OKQ8-{random.randint(10000, 99999)}",
                "cardNumber": self.credentials.get("card_id", "1234567890"),
                "vehicleReg": "ABC123",
                "driverName": "Erik Andersson",
                "dateTime": start_date.isoformat(),
                "fuelType": "Diesel",
                "volume": round(random.uniform(30, 80), 2),
                "pricePerLiter": round(random.uniform(17.5, 19.5), 2),
                "totalAmount": 0,  # Will be calculated
                "stationId": f"OKQ8-{random.randint(100, 999)}",
                "latitude": 59.3293 + random.uniform(-0.1, 0.1),
                "longitude": 18.0686 + random.uniform(-0.1, 0.1),
            }
            for _ in range(random.randint(1, 3))
        ]
        
        # Calculate total amounts
        for tx in mock_transactions:
            tx["totalAmount"] = round(tx["volume"] * tx["pricePerLiter"], 2)
        
        return mock_transactions
    
    def normalize_transaction(self, raw_data: Dict[str, Any]) -> FuelTransaction:
        """Convert OKQ8 format to standard FuelTransaction format."""
        return FuelTransaction(
            transaction_id=raw_data["transactionId"],
            provider="okq8",
            card_id=raw_data["cardNumber"],
            vehicle_id=raw_data.get("vehicleReg", "UNKNOWN"),
            driver_id=raw_data.get("driverName", "UNKNOWN"),
            timestamp=datetime.fromisoformat(raw_data["dateTime"]),
            liters=raw_data["volume"],
            price_per_liter=raw_data["pricePerLiter"],
            total_amount=raw_data["totalAmount"],
            fuel_type=raw_data["fuelType"],
            station_id=raw_data["stationId"],
            station_lat=raw_data.get("latitude"),
            station_lon=raw_data.get("longitude"),
        )
