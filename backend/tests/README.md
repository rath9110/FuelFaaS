# FuelGuard AI Test Suite

This directory contains comprehensive tests for the FuelGuard AI backend.

## Test Structure

```
tests/
├── conftest.py                  # Pytest fixtures and configuration
├── test_fraud_engine.py         # Unit tests for fraud detection rules
├── test_models.py               # Pydantic model validation tests
├── test_api_auth.py             # Authentication endpoint tests
├── test_api_vehicles.py         # Vehicle CRUD endpoint tests
└── test_api_transactions.py     # Transaction & anomaly endpoint tests
```

## Running Tests

### Run All Tests
```bash
pytest
```

### Run with Coverage
```bash
pytest --cov=backend --cov-report=html
```

### Run Specific Test Categories
```bash
# Unit tests only
pytest -m unit

# API integration tests
pytest -m api

# Fraud detection tests
pytest -m fraud

# Authentication tests
pytest -m auth
```

### Run Specific Test Files
```bash
pytest backend/tests/test_fraud_engine.py
pytest backend/tests/test_api_auth.py
```

### Run with Verbose Output
```bash
pytest -v
```

### Run and Stop on First Failure
```bash
pytest -x
```

## Test Coverage

The test suite covers:

- ✅ **Fraud Detection Rules** (9 rules)
  - Out-of-hours fueling
  - Geofence violations
  - Tank capacity violations
  - Inactive vehicle detection
  - Double-dipping detection
  - Price anomalies
  - Transaction frequency
  - Weekend/holiday detection
  - Impossible travel

- ✅ **Model Validation**
  - FuelTransaction schema
  - Vehicle schema
  - Project schema
  - Worker schema
  - User schema
  - AnomalyResult schema

- ✅ **API Endpoints**
  - Authentication (register, login, refresh, logout)
  - Vehicles (CRUD operations)
  - Transactions (ingestion, listing, filtering)
  - Anomalies (listing, filtering, review)
  - Statistics (dashboard metrics)

## Test Database

Tests use an in-memory SQLite database that is created and destroyed for each test session. This ensures:
- Fast test execution
- Test isolation
- No side effects on production database

## Fixtures

Common fixtures available in `conftest.py`:
- `test_db` - Database session
- `client` - HTTP test client
- `auth_headers` - Authenticated request headers
- `test_user` - Sample user
- `test_vehicle` - Sample vehicle
- `test_project` - Sample project
- `test_transaction` - Sample transaction
- `vehicle_factory` - Factory for creating vehicles
- `transaction_factory` - Factory for creating transactions

## Writing New Tests

Example test structure:

```python
@pytest.mark.api
@pytest.mark.asyncio
async def test_my_endpoint(client, auth_headers):
    """Test description."""
    response = await client.get(
        "/api/v1/my-endpoint",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    assert "expected_key" in response.json()
```

## Continuous Integration

Tests can be integrated into CI/CD pipelines:

```yaml
# Example GitHub Actions
- name: Run tests
  run: |
    pip install -r backend/requirements.txt
    pytest --cov=backend --cov-report=xml
```

## Coverage Goals

- Overall coverage target: **>80%**
- Critical modules (fraud_rules, engine): **>90%**
- API endpoints: **>85%**
