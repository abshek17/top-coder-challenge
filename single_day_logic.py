# Enhanced Single-Day Trip Logic
# Based on validation showing completely different calculation method

def calculate_single_day_reimbursement(miles_traveled, total_receipts_amount, context=None):
    """Enhanced single-day calculation with better fraud detection"""
    
    # === BASE MILEAGE CALCULATION ===
    # Use tiered mileage structure but with single-day adjustments
    if miles_traveled <= 100:
        mileage_reimbursement = miles_traveled * 0.58
    elif miles_traveled <= 500:
        mileage_reimbursement = 100 * 0.58 + (miles_traveled - 100) * 0.40
    else:
        mileage_reimbursement = 100 * 0.58 + 400 * 0.40 + (miles_traveled - 500) * 0.25
    
    # === FRAUD DETECTION: Impossible travel scenarios ===
    max_reasonable_miles = 800  # 10 hours driving at highway speeds
    if miles_traveled > max_reasonable_miles:
        fraud_score = (miles_traveled - max_reasonable_miles) / 100
        penalty_multiplier = max(0.3, 1.0 - fraud_score * 0.1)
        mileage_reimbursement *= penalty_multiplier
    
    # === RECEIPT REASONABLENESS for single-day ===
    if total_receipts_amount > 500:
        # High receipts on single day - validate reasonableness
        if total_receipts_amount > 1500:
            # Very high - major scrutiny (Case 995 territory)
            receipt_reimbursement = min(800, total_receipts_amount * 0.4)
        elif total_receipts_amount > 1000:
            # High but possibly legitimate (business dinner, hotel)
            receipt_reimbursement = min(1000, total_receipts_amount * 0.65)
        else:
            # Moderate high receipts - reasonable for business day
            receipt_reimbursement = total_receipts_amount * 0.75
    else:
        # Standard receipt processing for reasonable amounts
        receipt_reimbursement = total_receipts_amount * 0.80
    
    # === SINGLE-DAY SPECIFIC LOGIC ===
    # Based on validation: single-day trips plateau around $1400-1500
    
    # Choose better of per diem vs receipts (legacy logic)
    base_per_diem = 100  # Single day base
    lodging_component = max(base_per_diem, receipt_reimbursement)
    
    # === CAP SYSTEM: Prevent extreme single-day reimbursements ===
    base_amount = mileage_reimbursement + lodging_component
    
    # Apply progressive cap based on total amount
    if base_amount > 1500:
        # Hard cap with graduated reduction
        excess = base_amount - 1500
        capped_amount = 1500 + (excess * 0.2)  # Only 20% of excess allowed
        return min(1600, capped_amount)  # Absolute maximum $1600
    else:
        return base_amount


def get_single_day_context(miles_traveled, total_receipts_amount):
    """Analyze single-day trip context for legitimacy"""
    
    context = {
        'legitimacy_score': 1.0,
        'flags': [],
        'risk_level': 'low'
    }
    
    # === LEGITIMACY INDICATORS ===
    
    # Reasonable business day patterns
    if 100 <= miles_traveled <= 400 and 50 <= total_receipts_amount <= 300:
        context['legitimacy_score'] = 1.1  # Slight bonus for typical business day
        context['flags'].append('typical_business_day')
    
    # High-mileage day trip (could be legitimate site visits)
    elif 400 < miles_traveled <= 600 and total_receipts_amount <= 200:
        context['legitimacy_score'] = 1.0  # Neutral - could be legitimate
        context['flags'].append('high_mileage_day_trip')
    
    # === RISK INDICATORS ===
    
    # Extremely high expenses for one day
    if total_receipts_amount > 800:
        context['legitimacy_score'] *= 0.8
        context['risk_level'] = 'medium'
        context['flags'].append('high_single_day_expenses')
    
    # Impossible daily travel
    if miles_traveled > 800:
        context['legitimacy_score'] *= 0.6
        context['risk_level'] = 'high'
        context['flags'].append('impossible_daily_travel')
    
    # Luxury pattern (high expenses, low mileage)
    if total_receipts_amount > 400 and miles_traveled < 100:
        context['legitimacy_score'] *= 0.9
        context['flags'].append('luxury_pattern')
    
    return context
