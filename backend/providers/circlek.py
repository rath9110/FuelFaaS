"""Circle K fuel card provider implementation (mock for demonstration)."""

from datetime import datetime
from typing import List, Dict, Any
import random
from .base import BaseProviderClient, AuthenticationError
from ..models import FuelTransaction


class CircleKProvider(BaseProviderClient):
    """Circle K fuel card provider client."""
    
    @property
    def provider_name(self) -> str:
        return "circlek"
    
    async def validate_credentials(self) -> bool:
        """Validate Circle K Partner API credentials."""
        if "partner_id" not in self.credentials or "api_token" not in self.credentials:
            raise AuthenticationError("Missing partner_id or api_token for Circle K")
        return True
    
    async def fetch_transactions(
        self,
        start_date: datetime,
        end_date: datetime,
        **filters
    ) -> List[Dict[str, Any]]:
        """Fetch from Circle K Partner API."""
        return [
            {
                "transaction_id": f"CK-{random.randint(100000, 999999)}",
                "card_number": self.credentials.get("fleet_card", "CK987654"),
                "vehicle_license": "GHI789",
                "transaction_date": start_date.strftime("%Y-%m-%dT%H:%M:%S"),
                "fuel_grade": "Diesel Miles",
                "volume_liters": round(random.uniform(45, 85), 2),
                "price_per_unit": round(random.uniform(18.2, 19.8), 2),
                "total_price": 0,
                "site_number": f"CK-{random.randint(1000, 9999)}",
                "coordinates": {"latitude": 59.32, "longitude": 18.08},
            }
            for _ in range(random.randint(1, 3))
        ]
    
    def normalize_transaction(self, raw_data: Dict[str, Any]) -> FuelTransaction:
        """Convert Circle K format to standard format."""
        coords = raw_data.get("coordinates", {})
        return FuelTransaction(
            transaction_id=raw_data["transaction_id"],
            provider="circlek",
            card_id=raw_data["card_number"],
            vehicle_id=raw_data.get("vehicle_license", "UNKNOWN"),
            driver_id="UNKNOWN",
            timestamp=datetime.strptime(raw_data["transaction_date"], "%Y-%m-%dT%H:%M:%S"),
            liters=raw_data["volume_liters"],
            price_per_liter=raw_data["price_per_unit"],
            total_amount=raw_data["volume_liters"] * raw_data["price_per_unit"],
            fuel_type=raw_data.get("fuel_grade", "Diesel"),
            station_id=raw_data["site_number"],
            station_lat=coords.get("latitude"),
            station_lon=coords.get("longitude"),
        )
