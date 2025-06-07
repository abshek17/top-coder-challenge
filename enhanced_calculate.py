# Enhanced Reimbursement Calculation System
# Implementing recommendations based on validated dimensions and raw data analysis

import math
from datetime import datetime

# Import helper modules
from anomaly_detection import detect_anomalies, apply_graduated_response
from receipt_processing import calculate_dynamic_receipt_reimbursement, get_regional_multiplier, calculate_context_aware_minimum
from single_day_logic import calculate_single_day_reimbursement, get_single_day_context
from employee_patterns import get_employee_adjustment, build_employee_profile


def calculate_enhanced_reimbursement(trip_duration_days, miles_traveled, total_receipts_amount, 
                                   context=None, employee_id=None, employee_history=None):
    """
    Enhanced reimbursement calculation implementing all recommendations
    
    Args:
        trip_duration_days (int): Number of days for the trip
        miles_traveled (float): Total miles traveled
        total_receipts_amount (float): Total receipt amount
        context (dict, optional): Additional context (region, etc.)
        employee_id (str, optional): Employee identifier for pattern learning
        employee_history (dict, optional): Employee historical data
    
    Returns:
        float: Calculated reimbursement amount
    """
    
    # Initialize context if not provided
    if context is None:
        context = {}
    
    # === PHASE 1: ANOMALY DETECTION ===
    anomaly_result = detect_anomalies(trip_duration_days, miles_traveled, total_receipts_amount)
    
    # === PHASE 2: SINGLE-DAY SPECIAL HANDLING ===
    if trip_duration_days == 1:
        base_reimbursement = calculate_single_day_reimbursement(
            miles_traveled, total_receipts_amount, context
        )
        
        # Apply anomaly adjustments for single-day trips
        final_reimbursement = apply_graduated_response(base_reimbursement, anomaly_result, context)
        
        # Apply employee pattern adjustment if available
        if employee_id and employee_history:
            current_trip = {
                'duration': trip_duration_days,
                'daily_receipts': total_receipts_amount,
                'daily_miles': miles_traveled
            }
            employee_adjustment = get_employee_adjustment(employee_id, current_trip, employee_history)
            final_reimbursement *= employee_adjustment
        
        # Ensure minimum reimbursement
        minimum = calculate_context_aware_minimum(trip_duration_days, miles_traveled, context)
        return max(final_reimbursement, minimum)
    
    # === PHASE 3: MULTI-DAY TRIP CALCULATION ===
    
    # Base calculations
    miles_per_day = miles_traveled / trip_duration_days if trip_duration_days > 0 else 0
    receipts_per_day = total_receipts_amount / trip_duration_days if trip_duration_days > 0 else 0
    
    # === MILEAGE CALCULATION (Enhanced Tiered) ===
    mileage_reimbursement = calculate_mileage_reimbursement(miles_traveled, trip_duration_days, context)
    
    # === RECEIPT PROCESSING (Context-Aware) ===
    receipt_reimbursement = calculate_dynamic_receipt_reimbursement(
        total_receipts_amount, trip_duration_days, context
    )
    
    # === PER DIEM BASE ===
    base_per_diem = trip_duration_days * 100
    
    # Apply regional adjustments
    regional_multipliers = get_regional_multiplier(context.get('destination'))
    base_per_diem *= regional_multipliers['lodging_multiplier']
    receipt_reimbursement *= regional_multipliers['receipt_multiplier']
    
    # Choose better of per diem vs receipts (legacy insight)
    lodging_reimbursement = max(base_per_diem, receipt_reimbursement)
    
    # === BASE REIMBURSEMENT ===
    base_reimbursement = mileage_reimbursement + lodging_reimbursement
    
    # === EFFICIENCY AND LENGTH BONUSES ===
    efficiency_multiplier = calculate_efficiency_multiplier(miles_per_day)
    length_multiplier = calculate_length_multiplier(trip_duration_days)
    daily_spending_multiplier = calculate_daily_spending_multiplier(receipts_per_day, trip_duration_days)
    
    # Apply multipliers
    total_reimbursement = base_reimbursement * efficiency_multiplier * length_multiplier * daily_spending_multiplier
    
    # === MILEAGE BONUSES (Flat bonuses separate from per-mile rate) ===
    mileage_bonus = calculate_mileage_bonus(miles_traveled, trip_duration_days)
    total_reimbursement += mileage_bonus
    
    # === SWEET SPOT COMBO BONUSES ===
    combo_bonus = calculate_combo_bonus(trip_duration_days, miles_traveled, receipts_per_day)
    total_reimbursement *= combo_bonus
    
    # === ROUNDING BUG BONUS (Legacy feature) ===
    rounding_bonus = 0
    cents = int((total_receipts_amount * 100) % 100)
    if cents in [49, 99]:
        rounding_bonus = 10
    total_reimbursement += rounding_bonus
    
    # === PHASE 4: ANOMALY ADJUSTMENTS ===
    total_reimbursement = apply_graduated_response(total_reimbursement, anomaly_result, context)
    
    # === PHASE 5: EMPLOYEE PATTERN LEARNING ===
    if employee_id and employee_history:
        current_trip = {
            'duration': trip_duration_days,
            'daily_receipts': receipts_per_day,
            'daily_miles': miles_per_day
        }
        employee_adjustment = get_employee_adjustment(employee_id, current_trip, employee_history)
        total_reimbursement *= employee_adjustment
    
    # === ENSURE MINIMUM REIMBURSEMENT ===
    minimum_reimbursement = calculate_context_aware_minimum(trip_duration_days, miles_traveled, context)
    total_reimbursement = max(total_reimbursement, minimum_reimbursement)
    
    return round(total_reimbursement, 2)


def calculate_mileage_reimbursement(miles_traveled, trip_duration, context=None):
    """Enhanced mileage calculation with context awareness"""
    
    # Base tiered structure (from legacy)
    if miles_traveled <= 100:
        base_mileage = miles_traveled * 0.58
    elif miles_traveled <= 500:
        base_mileage = 100 * 0.58 + (miles_traveled - 100) * 0.40
    else:
        base_mileage = 100 * 0.58 + 400 * 0.40 + (miles_traveled - 500) * 0.25
    
    # Context adjustments
    if context and context.get('high_cost_region'):
        base_mileage *= 1.1  # Higher mileage rates in expensive areas
    
    return base_mileage


def calculate_efficiency_multiplier(miles_per_day):
    """Calculate efficiency bonus based on daily mileage"""
    
    if 180 <= miles_per_day <= 220:
        return 1.10  # Sweet spot bonus
    elif 120 <= miles_per_day < 180:
        return 1.02  # Small bonus
    elif miles_per_day > 300:
        return 0.95  # Penalty for excessive driving
    elif miles_per_day < 100:
        return 0.96  # Small penalty for low efficiency
    else:
        return 1.0


def calculate_length_multiplier(trip_duration_days):
    """Calculate trip length bonus/penalty"""
    
    if trip_duration_days == 5:
        return 1.10  # Strong 5-day bonus (validated pattern)
    elif trip_duration_days in [4, 6]:
        return 1.05  # Slight bonus for optimal range
    elif trip_duration_days < 3:
        return 0.97  # Small penalty for very short trips
    elif trip_duration_days > 7:
        return 0.96  # Small penalty for very long trips
    else:
        return 1.0


def calculate_daily_spending_multiplier(receipts_per_day, trip_duration):
    """Calculate daily spending adjustment"""
    
    # Graduated response based on trip length
    if trip_duration == 1:
        # Single-day handled separately
        return 1.0
    elif trip_duration <= 3:
        # Short trips - stricter on high spending
        if receipts_per_day > 200:
            return 0.90
        elif receipts_per_day < 50:
            return 0.95
    elif trip_duration <= 7:
        # Standard trips
        if receipts_per_day > 250:
            return 0.92
        elif receipts_per_day < 40:
            return 0.94
    else:
        # Long trips - more tolerance for business expenses
        if receipts_per_day > 300:
            return 0.94
        elif receipts_per_day < 30:
            return 0.90  # Low spending on long trips is suspicious
    
    return 1.0


def calculate_mileage_bonus(miles_traveled, trip_duration):
    """Calculate flat mileage bonuses (separate from per-mile rate)"""
    
    if trip_duration == 1:
        # Limited bonuses for single-day trips
        if miles_traveled > 800:
            return 50
        elif miles_traveled > 600:
            return 30
        else:
            return 0
    else:
        # Full bonuses for multi-day trips
        if miles_traveled > 1200:
            return 350  # Very high mileage bonus
        elif miles_traveled > 1000:
            return 300  # High mileage bonus
        elif miles_traveled > 800:
            return 200  # Good mileage bonus
        elif miles_traveled > 600:
            return 120  # Moderate bonus
        elif miles_traveled > 400:
            return 60   # Small bonus
        else:
            return 0


def calculate_combo_bonus(trip_duration_days, miles_traveled, receipts_per_day):
    """Calculate sweet spot combination bonuses"""
    
    # Marcus's incredible 8-day trip pattern
    if 6 <= trip_duration_days <= 8 and miles_traveled > 800 and receipts_per_day < 200:
        if miles_traveled > 1000:
            return 1.35  # Major bonus for extreme business hustle
        else:
            return 1.25  # Strong bonus for business travel
    elif 6 <= trip_duration_days <= 8 and miles_traveled > 600:
        return 1.15  # Good bonus for decent business travel
    
    # Kevin's sweet spot (5-day, high mileage, reasonable spending)
    elif trip_duration_days == 5 and miles_traveled > 600 and 100 <= receipts_per_day <= 150:
        return 1.20  # Strong 5-day combo bonus
    
    return 1.0


# Legacy compatibility function
def calculate_legacy_reimbursement(trip_duration_days, miles_traveled, total_receipts_amount):
    """
    Legacy function maintained for backward compatibility
    Now calls the enhanced system with default parameters
    """
    return calculate_enhanced_reimbursement(
        trip_duration_days, miles_traveled, total_receipts_amount
    )


# === TEST CASES ===
if __name__ == "__main__":
    print("=== Enhanced Reimbursement System Tests ===")
    
    # Marcus's examples
    print("\nMarcus's Cleveland-Detroit trips:")
    print(f"Trip 1: ${calculate_enhanced_reimbursement(3, 180, 200)}")
    print(f"Trip 2: ${calculate_enhanced_reimbursement(3, 180, 200)}")
    
    # Marcus's 8-day hustle trip
    print(f"\nMarcus's 8-day Ohio/Indiana trip: ${calculate_enhanced_reimbursement(8, 2400, 800)}")
    
    # Kevin's sweet spot combo
    print(f"\nKevin's sweet spot (5 days, 900 miles, $450): ${calculate_enhanced_reimbursement(5, 900, 450)}")
    
    # Single-day trip tests
    print(f"\nSingle-day reasonable: ${calculate_enhanced_reimbursement(1, 300, 150)}")
    print(f"Single-day suspicious: ${calculate_enhanced_reimbursement(1, 1082, 1809)}")
    
    # Anomaly tests
    print(f"\nVacation pattern: ${calculate_enhanced_reimbursement(10, 1200, 300)}")
    print(f"High cost business: ${calculate_enhanced_reimbursement(5, 600, 1000)}")
    
    # Employee pattern test (with mock history)
    employee_history = {
        'emp123': {
            'avg_duration': 4,
            'avg_daily_receipts': 120,
            'avg_miles_per_day': 150
        }
    }
    print(f"\nEmployee pattern consistent: ${calculate_enhanced_reimbursement(4, 600, 480, employee_id='emp123', employee_history=employee_history)}")
    print(f"Employee pattern deviation: ${calculate_enhanced_reimbursement(10, 1500, 2000, employee_id='emp123', employee_history=employee_history)}")
