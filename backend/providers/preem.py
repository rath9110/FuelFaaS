"""Preem fuel card provider implementation (mock for demonstration)."""

from datetime import datetime
from typing import List, Dict, Any
import random
from .base import BaseProviderClient, AuthenticationError
from ..models import FuelTransaction


class PreemProvider(BaseProviderClient):
    """Preem fuel card provider client."""
    
    @property
    def provider_name(self) -> str:
        return "preem"
    
    async def validate_credentials(self) -> bool:
        """Validate Preem API credentials."""
        if "api_key" not in self.credentials:
            raise AuthenticationError("Missing api_key for Preem")
        
        if self.credentials.get("api_key") == "invalid":
            raise AuthenticationError("Invalid Preem API key")
        
        return True
    
    async def fetch_transactions(
        self,
        start_date: datetime,
        end_date: datetime,
        **filters
    ) -> List[Dict[str, Any]]:
        """Fetch transactions from Preem Partner API."""
        # Mock Preem API response
        return [
            {
                "id": f"PREEM-{random.randint(10000, 99999)}",
                "card": self.credentials.get("card_number", "9876543210"),
                "vehicle": "XYZ789",
                "driver": "Anna Johansson",
                "date": start_date.strftime("%Y-%m-%d %H:%M:%S"),
                "product": "Diesel Evolution",
                "liters": round(random.uniform(40, 90), 2),
                "price_liter": round(random.uniform(18.0, 20.0), 2),
                "total_sek": 0,
                "station": {"id": f"PREEM-{random.randint(100, 999)}", "lat": 57.7089, "lon": 11.9746},
            }
            for _ in range(random.randint(1, 2))
        ]
    
    def normalize_transaction(self, raw_data: Dict[str, Any]) -> FuelTransaction:
        """Convert Preem format to standard FuelTransaction format."""
        station = raw_data.get("station", {})
        return FuelTransaction(
            transaction_id=raw_data["id"],
            provider="preem",
            card_id=raw_data["card"],
            vehicle_id=raw_data.get("vehicle", "UNKNOWN"),
            driver_id=raw_data.get("driver", "UNKNOWN"),
            timestamp=datetime.strptime(raw_data["date"], "%Y-%m-%d %H:%M:%S"),
            liters=raw_data["liters"],
            price_per_liter=raw_data["price_liter"],
            total_amount=raw_data["liters"] * raw_data["price_liter"],
            fuel_type=raw_data.get("product", "Diesel"),
            station_id=station.get("id", "UNKNOWN"),
            station_lat=station.get("lat"),
            station_lon=station.get("lon"),
        )
