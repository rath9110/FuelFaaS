import requests
from datetime import datetime, timedelta

BASE_URL = "http://127.0.0.1:8001"

def test_ingest():
    # 1. Normal Transaction
    tx_normal = {
        "transaction_id": "TX100",
        "provider": "okq8",
        "card_id": "C123",
        "vehicle_id": "V001", # Excavator, 200L
        "timestamp": datetime.now().isoformat(),
        "liters": 50,
        "price_per_liter": 20,
        "total_amount": 1000,
        "fuel_type": "Diesel",
        "station_id": "S1",
        "station_lat": 59.3293, # Near Stockholm project
        "station_lon": 18.0686
    }
    
    # 2. Anomalous Transaction (High Volume)
    tx_high_volume = {
        "transaction_id": "TX101",
        "provider": "okq8",
        "card_id": "C123",
        "vehicle_id": "V001",
        "timestamp": datetime.now().isoformat(),
        "liters": 250, # > 200L * 1.05
        "price_per_liter": 20,
        "total_amount": 5000,
        "fuel_type": "Diesel",
        "station_id": "S1",
        "station_lat": 59.3293,
        "station_lon": 18.0686
    }

    # 3. Anomalous Transaction (Far Distance)
    tx_far = {
        "transaction_id": "TX102",
        "provider": "okq8",
        "card_id": "C123",
        "vehicle_id": "V001",
        "timestamp": datetime.now().isoformat(),
        "liters": 50,
        "price_per_liter": 20,
        "total_amount": 1000,
        "fuel_type": "Diesel",
        "station_id": "S2",
        "station_lat": 60.0, # Far away
        "station_lon": 18.0
    }

    print("Sending Normal Transaction...")
    resp = requests.post(f"{BASE_URL}/ingest", json=tx_normal)
    print(resp.json())

    print("\nSending High Volume Transaction...")
    resp = requests.post(f"{BASE_URL}/ingest", json=tx_high_volume)
    print(resp.json())

    print("\nSending Far Distance Transaction...")
    resp = requests.post(f"{BASE_URL}/ingest", json=tx_far)
    print(resp.json())

    print("\nChecking Stats...")
    resp = requests.get(f"{BASE_URL}/stats")
    print(resp.json())

if __name__ == "__main__":
    try:
        test_ingest()
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure the backend is running: uvicorn backend.main:app --reload")
