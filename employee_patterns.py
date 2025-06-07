# Employee Pattern Learning System
# Simplified implementation for basic historical pattern recognition

def get_employee_adjustment(employee_id, current_trip, historical_data=None):
    """Basic employee pattern recognition"""
    
    if not historical_data or not historical_data.get(employee_id):
        return 1.0  # No adjustment for new employees or missing data
    
    employee_history = historical_data[employee_id]
    
    # === TYPICAL PATTERN ANALYSIS ===
    avg_trip_duration = employee_history.get('avg_duration', current_trip['duration'])
    avg_daily_receipts = employee_history.get('avg_daily_receipts', current_trip['daily_receipts'])
    avg_miles_per_day = employee_history.get('avg_miles_per_day', current_trip['daily_miles'])
    
    # Avoid division by zero
    if avg_trip_duration <= 0 or avg_daily_receipts <= 0 or avg_miles_per_day <= 0:
        return 1.0
    
    # === DEVIATION SCORING ===
    duration_deviation = abs(current_trip['duration'] - avg_trip_duration) / avg_trip_duration
    receipt_deviation = abs(current_trip['daily_receipts'] - avg_daily_receipts) / avg_daily_receipts
    mileage_deviation = abs(current_trip['daily_miles'] - avg_miles_per_day) / avg_miles_per_day
    
    # === ADJUSTMENT CALCULATION ===
    total_deviation = (duration_deviation + receipt_deviation + mileage_deviation) / 3
    
    # Pattern consistency bonus/penalty
    if total_deviation < 0.2:  # Very consistent with history
        return 1.02  # Small bonus for consistent patterns
    elif total_deviation < 0.5:  # Moderately consistent
        return 1.0   # No adjustment
    elif total_deviation < 1.0:  # Moderate deviation
        return 0.98  # Small penalty
    elif total_deviation < 2.0:  # Significant deviation
        return 0.95  # Moderate penalty for unusual pattern
    else:  # Very significant deviation
        return 0.90  # Larger penalty for highly unusual pattern


def build_employee_profile(trip_history):
    """Build basic employee profile from trip history"""
    
    if not trip_history:
        return {}
    
    # Calculate averages
    total_trips = len(trip_history)
    total_duration = sum(trip.get('duration', 0) for trip in trip_history)
    total_receipts = sum(trip.get('total_receipts', 0) for trip in trip_history)
    total_miles = sum(trip.get('miles_traveled', 0) for trip in trip_history)
    
    if total_trips == 0:
        return {}
    
    avg_duration = total_duration / total_trips
    avg_daily_receipts = total_receipts / max(total_duration, 1)
    avg_miles_per_day = total_miles / max(total_duration, 1)
    
    # Calculate consistency metrics
    duration_variance = sum((trip.get('duration', 0) - avg_duration) ** 2 for trip in trip_history) / total_trips
    receipt_variance = sum(((trip.get('total_receipts', 0) / max(trip.get('duration', 1), 1)) - avg_daily_receipts) ** 2 for trip in trip_history) / total_trips
    
    consistency_score = 1.0 / (1.0 + duration_variance + receipt_variance)
    
    return {
        'avg_duration': avg_duration,
        'avg_daily_receipts': avg_daily_receipts,
        'avg_miles_per_day': avg_miles_per_day,
        'total_trips': total_trips,
        'consistency_score': consistency_score,
        'risk_profile': 'low' if consistency_score > 0.8 else 'medium' if consistency_score > 0.5 else 'high'
    }


def detect_employee_patterns(employee_history):
    """Detect specific employee travel patterns"""
    
    patterns = []
    
    if not employee_history:
        return patterns
    
    avg_duration = employee_history.get('avg_duration', 0)
    avg_daily_receipts = employee_history.get('avg_daily_receipts', 0)
    total_trips = employee_history.get('total_trips', 0)
    
    # Pattern detection
    if avg_duration >= 7 and avg_daily_receipts < 75:
        patterns.append('long_low_cost_traveler')  # Possible vacation abuse
    elif avg_duration <= 2 and avg_daily_receipts > 200:
        patterns.append('short_high_cost_traveler')  # Possible entertainment abuse
    elif total_trips > 20 and avg_daily_receipts > 150:
        patterns.append('frequent_high_spender')  # High-volume business traveler
    elif avg_duration >= 5 and 100 <= avg_daily_receipts <= 180:
        patterns.append('legitimate_business_traveler')  # Standard business pattern
    
    return patterns
