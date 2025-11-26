"""Shell fuel card provider implementation (mock for demonstration)."""

from datetime import datetime
from typing import List, Dict, Any
import random
from .base import BaseProviderClient, AuthenticationError
from ..models import FuelTransaction


class ShellProvider(BaseProviderClient):
    """Shell Fleet Card provider client."""
    
    @property
    def provider_name(self) -> str:
        return "shell"
    
    async def validate_credentials(self) -> bool:
        """Validate Shell Fleet API credentials."""
        required = ["username", "password"]
        if not all(k in self.credentials for k in required):
            raise AuthenticationError(f"Missing credentials for Shell: {required}")
        return True
    
    async def fetch_transactions(
        self,
        start_date: datetime,
        end_date: datetime,
        **filters
    ) -> List[Dict[str, Any]]:
        """Fetch from Shell Fleet Card API."""
        return [
            {
                "transId": f"SH-{random.randint(100000, 999999)}",
                "cardNum": self.credentials.get("card_number", "SHELL123"),
                "vehicleIdentifier": "DEF456",
                "timestamp": start_date.isoformat(),
                "productCode": "DSL",
                "quantity": round(random.uniform(35, 75), 2),
                "unitPrice": round(random.uniform(18.5, 19.5), 2),
                "grossAmount": 0,
                "siteCode": f"SHELL-{random.randint(1000, 9999)}",
                "location": {"lat": 59.33, "lng": 18.07},
            }
            for _ in range(random.randint(1, 2))
        ]
    
    def normalize_transaction(self, raw_data: Dict[str, Any]) -> FuelTransaction:
        """Convert Shell format to standard format."""
        loc = raw_data.get("location", {})
        return FuelTransaction(
            transaction_id=raw_data["transId"],
            provider="shell",
            card_id=raw_data["cardNum"],
            vehicle_id=raw_data.get("vehicleIdentifier", "UNKNOWN"),
            driver_id="UNKNOWN",  # Shell doesn't always provide driver
            timestamp=datetime.fromisoformat(raw_data["timestamp"]),
            liters=raw_data["quantity"],
            price_per_liter=raw_data["unitPrice"],
            total_amount=raw_data["quantity"] * raw_data["unitPrice"],
            fuel_type="Diesel" if raw_data["productCode"] == "DSL" else "Unleaded",
            station_id=raw_data["siteCode"],
            station_lat=loc.get("lat"),
            station_lon=loc.get("lng"),
        )
