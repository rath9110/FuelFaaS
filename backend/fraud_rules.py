"""
Individual fraud detection rules for FuelGuard AI.
Each rule is a standalone function that checks for specific anomaly patterns.
"""

from datetime import datetime, timedelta, time
from typing import List, Dict, Optional, Tuple
from math import radians, cos, sin, asin, sqrt


def haversine(lon1: float, lat1: float, lon2: float, lat2: float) -> float:
    """
    Calculate the great circle distance in kilometers between two points 
    on the earth (specified in decimal degrees).
    
    Args:
        lon1: Longitude of first point
        lat1: Latitude of first point
        lon2: Longitude of second point
        lat2: Latitude of second point
    
    Returns:
        Distance in kilometers
    """
    # Convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    
    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    r = 6371  # Radius of earth in kilometers
    return c * r


def check_out_of_hours(
    transaction_time: datetime,
    worker_schedule_start: Optional[str],
    worker_schedule_end: Optional[str]
) -> Tuple[bool, Optional[str], int]:
    """
    Check if transaction occurred outside worker's scheduled hours.
    
    Args:
        transaction_time: Time of transaction
        worker_schedule_start: Worker start time in HH:MM format
        worker_schedule_end: Worker end time in HH:MM format
    
    Returns:
        (is_violation, reason, score)
    """
    if not worker_schedule_start or not worker_schedule_end:
        # No schedule defined, use broad construction hours (6 AM - 7 PM)
        hour = transaction_time.hour
        if hour < 6 or hour >= 19:
            return (
                True,
                "Fueling outside standard working hours (06:00-19:00)",
                25
            )
        return (False, None, 0)
    
    # Parse worker schedule
    try:
        start_time = datetime.strptime(worker_schedule_start, "%H:%M").time()
        end_time = datetime.strptime(worker_schedule_end, "%H:%M").time()
        current_time = transaction_time.time()
        
        # Check if transaction is within schedule
        if not (start_time <= current_time <= end_time):
            return (
                True,
                f"Fueling outside worker schedule ({worker_schedule_start}-{worker_schedule_end})",
                30
            )
    except ValueError:
        # Invalid schedule format, use default
        pass
    
    return (False, None, 0)


def check_geofence_violation(
    station_lat: float,
    station_lon: float,
    project_lat: Optional[float],
    project_lon: Optional[float],
    geofence_radius_km: Optional[float],
    project_name: Optional[str],
    buffer_km: float = 15.0
) -> Tuple[bool, Optional[str], int]:
    """
    Check if fueling station is outside project geofence.
    
    Args:
        station_lat: Station latitude
        station_lon: Station longitude
        project_lat: Project center latitude
        project_lon: Project center longitude
        geofence_radius_km: Geofence radius in km
        project_name: Project name for messaging
        buffer_km: Additional buffer allowance in km
    
    Returns:
        (is_violation, reason, score)
    """
    if project_lat is None or project_lon is None or geofence_radius_km is None:
        return (False, None, 0)
    
    distance = haversine(station_lon, station_lat, project_lon, project_lat)
    max_allowed = geofence_radius_km + buffer_km
    
    if distance > max_allowed:
        return (
            True,
            f"Fueling {distance:.1f}km away from project {project_name or 'site'} (max: {max_allowed:.1f}km)",
            40
        )
    
    return (False, None, 0)


def check_tank_capacity_violation(
    liters: float,
    tank_capacity: Optional[float]
) -> Tuple[bool, Optional[str], int]:
    """
    Check if fuel volume exceeds tank capacity.
    
    Args:
        liters: Amount of fuel purchased
        tank_capacity: Vehicle tank capacity in liters
    
    Returns:
        (is_violation, reason, score)
    """
    if tank_capacity is None:
        return (False, None, 0)
    
    # Allow 5% tolerance for measurement variance
    max_allowed = tank_capacity * 1.05
    
    if liters > max_allowed:
        return (
            True,
            f"Volume {liters:.1f}L exceeds tank capacity {tank_capacity:.1f}L",
            40
        )
    
    return (False, None, 0)


def check_vehicle_inactive(
    vehicle_status: Optional[str]
) -> Tuple[bool, Optional[str], int]:
    """
    Check if vehicle is marked as inactive.
    
    Args:
        vehicle_status: Current vehicle status
    
    Returns:
        (is_violation, reason, score)
    """
    if vehicle_status == "inactive":
        return (
            True,
            "Vehicle is marked as inactive",
            25
        )
    
    return (False, None, 0)


def check_double_dipping(
    transaction_time: datetime,
    recent_transactions: List[datetime],
    threshold_minutes: int = 30
) -> Tuple[bool, Optional[str], int]:
    """
    Check for multiple transactions in short time period (double-dipping).
    
    Args:
        transaction_time: Current transaction time
        recent_transactions: List of recent transaction timestamps for same vehicle
        threshold_minutes: Time threshold in minutes
    
    Returns:
        (is_violation, reason, score)
    """
    for recent_time in recent_transactions:
        time_diff = abs((transaction_time - recent_time).total_seconds() / 60)
        
        if time_diff < threshold_minutes:
            return (
                True,
                f"Multiple transactions within {threshold_minutes} minutes (possible double-dipping)",
                35
            )
    
    return (False, None, 0)


def check_price_anomaly(
    price_per_liter: float,
    market_average: Optional[float] = None,
    threshold_percent: float = 20.0
) -> Tuple[bool, Optional[str], int]:
    """
    Check if fuel price is anomalously high or low.
    
    Args:
        price_per_liter: Transaction price per liter
        market_average: Market average price (if available)
        threshold_percent: Percentage threshold for anomaly
    
    Returns:
        (is_violation, reason, score)
    """
    # If no market average, use a reasonable estimate for Swedish diesel/petrol
    if market_average is None:
        market_average = 18.0  # SEK per liter (approximate)
    
    deviation = abs(price_per_liter - market_average) / market_average * 100
    
    if deviation > threshold_percent:
        if price_per_liter > market_average:
            return (
                True,
                f"Price {price_per_liter:.2f} SEK/L is {deviation:.1f}% above market average",
                20
            )
        else:
            return (
                True,
                f"Price {price_per_liter:.2f} SEK/L is {deviation:.1f}% below market average (possible theft)",
                30
            )
    
    return (False, None, 0)


def check_transaction_frequency(
    transaction_date: datetime,
    recent_transaction_dates: List[datetime],
    max_per_day: int = 2
) -> Tuple[bool, Optional[str], int]:
    """
    Check if vehicle has too many transactions in one day.
    
    Args:
        transaction_date: Current transaction date
        recent_transaction_dates: List of recent transaction dates for same vehicle
        max_per_day: Maximum transactions allowed per day
    
    Returns:
        (is_violation, reason, score)
    """
    same_day_count = sum(
        1 for tx_date in recent_transaction_dates
        if tx_date.date() == transaction_date.date()
    )
    
    if same_day_count >= max_per_day:
        return (
            True,
            f"Excessive fueling: {same_day_count + 1} transactions today (max: {max_per_day})",
            30
        )
    
    return (False, None, 0)


def check_weekend_holiday(
    transaction_time: datetime,
    holidays: Optional[List[datetime]] = None
) -> Tuple[bool, Optional[str], int]:
    """
    Check if transaction occurred on weekend or holiday.
    
    Args:
        transaction_time: Transaction timestamp
        holidays: List of holiday dates
    
    Returns:
        (is_violation, reason, score)
    """
    # Check weekend
    if transaction_time.weekday() >= 5:  # Saturday=5, Sunday=6
        return (
            True,
            f"Fueling on weekend ({transaction_time.strftime('%A')})",
            20
        )
    
    # Check holidays
    if holidays:
        tx_date = transaction_time.date()
        for holiday in holidays:
            if tx_date == holiday.date():
                return (
                    True,
                    f"Fueling on holiday ({tx_date.strftime('%Y-%m-%d')})",
                    25
                )
    
    return (False, None, 0)


def check_consecutive_locations(
    current_lat: float,
    current_lon: float,
    current_time: datetime,
    previous_lat: Optional[float],
    previous_lon: Optional[float],
    previous_time: Optional[datetime],
    max_speed_kmh: float = 120.0
) -> Tuple[bool, Optional[str], int]:
    """
    Check if vehicle traveled impossible distance between transactions.
    
    Args:
        current_lat: Current transaction latitude
        current_lon: Current transaction longitude
        current_time: Current transaction time
        previous_lat: Previous transaction latitude
        previous_lon: Previous transaction longitude
        previous_time: Previous transaction time
        max_speed_kmh: Maximum reasonable speed in km/h
    
    Returns:
        (is_violation, reason, score)
    """
    if previous_lat is None or previous_lon is None or previous_time is None:
        return (False, None, 0)
    
    # Calculate distance between stations
    distance_km = haversine(previous_lon, previous_lat, current_lon, current_lat)
    
    # Calculate time difference in hours
    time_diff_hours = abs((current_time - previous_time).total_seconds()) / 3600
    
    if time_diff_hours == 0:
        # Simultaneous transactions at different locations
        if distance_km > 1:  # More than 1km apart
            return (
                True,
                f"Simultaneous transactions {distance_km:.1f}km apart (impossible)",
                45
            )
        return (False, None, 0)
    
    # Calculate required speed
    required_speed = distance_km / time_diff_hours
    
    if required_speed > max_speed_kmh:
        return (
            True,
            f"Impossible travel: {distance_km:.1f}km in {time_diff_hours:.1f}h (requires {required_speed:.0f}km/h)",
            35
        )
    
    return (False, None, 0)
