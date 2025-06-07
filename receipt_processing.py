# Context-Aware Receipt Processing System
# Based on validated dimensions showing dynamic sweet spots

def calculate_dynamic_receipt_reimbursement(total_receipts, trip_duration, context=None):
    """Dynamic receipt processing based on trip context"""
    
    if trip_duration <= 0:
        return 0
    
    daily_receipts = total_receipts / trip_duration
    
    # === DYNAMIC SWEET SPOTS based on trip duration ===
    if trip_duration == 1:
        sweet_spot_min, sweet_spot_max = 80, 150    # Single-day range
    elif trip_duration <= 3:
        sweet_spot_min, sweet_spot_max = 100, 180   # Short trip range  
    elif trip_duration <= 7:
        sweet_spot_min, sweet_spot_max = 120, 200   # Standard business
    else:
        sweet_spot_min, sweet_spot_max = 140, 220   # Extended business
    
    # === REGIONAL ADJUSTMENTS (if context available) ===
    if context:
        if context.get('high_cost_region'):
            sweet_spot_min *= 1.3
            sweet_spot_max *= 1.3
        elif context.get('low_cost_region'):
            sweet_spot_min *= 0.8
            sweet_spot_max *= 0.8
    
    # === REIMBURSEMENT CALCULATION ===
    if daily_receipts < 50:
        # Penalty for very low receipts
        return total_receipts * 0.40
    elif sweet_spot_min <= daily_receipts <= sweet_spot_max:
        # Sweet spot rate - best treatment
        return total_receipts * 0.85
    elif daily_receipts > 400:
        # CRITICAL FIX: Very high daily spending (>$400/day) - stronger penalty
        # Pattern analysis shows these should get significantly lower reimbursements
        if trip_duration <= 5:
            # Short/medium trips with extreme spending - major penalty
            return total_receipts * 0.35  # Reduced from 0.45
        else:
            # Longer trips might be legitimate high-cost business
            return total_receipts * 0.50  # Reduced from 0.55
    elif daily_receipts > sweet_spot_max * 2:
        # Very high daily spending - graduated penalty
        excess_factor = daily_receipts / (sweet_spot_max * 2)
        penalty_rate = max(0.30, 0.85 - (excess_factor - 1) * 0.15)
        return total_receipts * penalty_rate
    elif daily_receipts > sweet_spot_max:
        # Above sweet spot but not extreme - moderate penalty
        excess_factor = daily_receipts / sweet_spot_max
        penalty_rate = max(0.60, 0.85 - (excess_factor - 1) * 0.10)
        return total_receipts * penalty_rate
    else:
        # Below sweet spot but above minimum - standard rate
        return total_receipts * 0.75


def get_regional_multiplier(destination_info=None):
    """Regional cost-of-living adjustments"""
    
    if not destination_info:
        return {'receipt_multiplier': 1.0, 'lodging_multiplier': 1.0}
    
    # === BASIC REGIONAL CATEGORIES ===
    high_cost_cities = ['NYC', 'SF', 'LA', 'DC', 'Boston', 'Seattle', 'Chicago']
    medium_cost_cities = ['Austin', 'Denver', 'Portland', 'Miami', 'Atlanta']
    low_cost_regions = ['Rural', 'Small_Town', 'Midwest_Rural', 'South_Rural']
    
    city = destination_info.get('city', '')
    region_type = destination_info.get('region_type', '')
    
    if city in high_cost_cities:
        return {'receipt_multiplier': 1.3, 'lodging_multiplier': 1.4}
    elif city in medium_cost_cities:
        return {'receipt_multiplier': 1.1, 'lodging_multiplier': 1.15}
    elif region_type in low_cost_regions:
        return {'receipt_multiplier': 0.8, 'lodging_multiplier': 0.7}
    else:
        return {'receipt_multiplier': 1.0, 'lodging_multiplier': 1.0}


def calculate_context_aware_minimum(trip_duration, miles_traveled, context=None):
    """Context-aware minimum reimbursement calculation"""
    
    # === BASE MINIMUM varies by trip type ===
    if trip_duration == 1:
        base_minimum = 100  # Single-day minimum
    elif trip_duration <= 3:
        base_minimum = trip_duration * 75  # Short trip minimum
    else:
        base_minimum = trip_duration * 60  # Standard minimum
    
    # === MILEAGE ADJUSTMENT to minimum ===
    if miles_traveled > 500:
        mileage_adjustment = min(200, miles_traveled * 0.1)
        base_minimum += mileage_adjustment
    
    # === REGIONAL ADJUSTMENT to minimum ===
    if context:
        regional_multiplier = context.get('cost_multiplier', 1.0)
        base_minimum *= regional_multiplier
    
    return base_minimum
