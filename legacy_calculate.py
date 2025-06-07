import math
from datetime import datetime

def calculate_legacy_reimbursement(trip_duration_days, miles_traveled, total_receipts_amount):
    """
    Initial rule set based on employee interviews
    """
    
    # Base calculations
    miles_per_day = miles_traveled / trip_duration_days if trip_duration_days > 0 else 0
    receipts_per_day = total_receipts_amount / trip_duration_days if trip_duration_days > 0 else 0
    
    # === MILEAGE CALCULATION (Tiered) ===
    # Lisa: "First 100 miles or so, you get the full rate—like 58 cents per mile. After that, it drops"
    mileage_reimbursement = 0
    if miles_traveled <= 100:
        mileage_reimbursement = miles_traveled * 0.58
    elif miles_traveled <= 500:
        # Full rate for first 100 miles, then reduced rate
        mileage_reimbursement = 100 * 0.58 + (miles_traveled - 100) * 0.40
    else:
        # Tiered structure: 100 @ 0.58, 400 @ 0.40, remainder @ 0.25
        mileage_reimbursement = 100 * 0.58 + 400 * 0.40 + (miles_traveled - 500) * 0.25
    
    # === PER DIEM BASE ===
    # Lisa: "$100 a day seems to be the base"
    base_per_diem = trip_duration_days * 100
    
    # === RECEIPT PROCESSING (Non-linear) ===
    # Lisa: "Medium-high amounts—like $600-800—seem to get really good treatment"
    receipt_reimbursement = 0
    
    if total_receipts_amount < 50:
        # Penalty for very small receipts - Dave: "better off submitting nothing"
        receipt_reimbursement = total_receipts_amount * 0.50  # Harsh penalty
    elif total_receipts_amount <= 600:
        # Standard reimbursement
        receipt_reimbursement = total_receipts_amount * 0.80
    elif total_receipts_amount <= 800:
        # Sweet spot - best treatment
        receipt_reimbursement = total_receipts_amount * 0.90
    elif total_receipts_amount <= 1200:
        # Good but declining returns
        receipt_reimbursement = 800 * 0.90 + (total_receipts_amount - 800) * 0.75
    else:
        # Strong diminishing returns for very high amounts
        receipt_reimbursement = 800 * 0.90 + 400 * 0.75 + (total_receipts_amount - 1200) * 0.50
    
    # === EFFICIENCY BONUS ===
    # Kevin: "sweet spot around 180-220 miles per day where the bonuses are maximized"
    efficiency_multiplier = 1.0
    if 180 <= miles_per_day <= 220:
        efficiency_multiplier = 1.10  # 10% bonus for optimal efficiency
    elif 120 <= miles_per_day < 180:
        efficiency_multiplier = 1.02  # Small bonus
    elif miles_per_day > 300:
        efficiency_multiplier = 0.95  # Penalty for excessive driving
    elif miles_per_day < 100:
        efficiency_multiplier = 0.95  # Penalty for low efficiency
    
    # === TRIP LENGTH BONUSES/PENALTIES ===
    length_multiplier = 1.0
    
    if trip_duration_days == 5:
        # Lisa: "5-day trips almost always get a bonus"
        length_multiplier = 1.10  # Strong 5-day bonus
    elif trip_duration_days in [4, 6]:
        # Slight bonus for optimal range
        length_multiplier = 1.05
    elif trip_duration_days < 3:
        # Penalty for very short trips
        length_multiplier = 0.95
    elif trip_duration_days > 7:
        # Penalty for very long trips
        length_multiplier = 0.95
    
    # === SPENDING PER DAY ADJUSTMENTS ===
    # Simplified approach - focus on per-day spending reasonableness
    daily_spending_multiplier = 1.0
    if receipts_per_day > 150:  # Very high daily spending
        daily_spending_multiplier = 0.90
    elif receipts_per_day < 30:  # Very low daily spending
        daily_spending_multiplier = 0.95
    
    # === ROUNDING BUG BONUS ===
    # Lisa: "If your receipts end in 49 or 99 cents, you often get a little extra money"
    rounding_bonus = 0
    cents = int((total_receipts_amount * 100) % 100)
    if cents in [49, 99]:
        rounding_bonus = 10  # Small bonus for "lucky" receipt totals
    
    # === FINAL CALCULATION ===
    # Simplified approach: combine base calculations with multipliers
    base_reimbursement = mileage_reimbursement + base_per_diem + receipt_reimbursement
    
    # Apply all multipliers
    total_reimbursement = (base_reimbursement * efficiency_multiplier * 
                          length_multiplier * daily_spending_multiplier) + rounding_bonus
    
    # Ensure minimum reimbursement
    minimum_reimbursement = trip_duration_days * 50  # At least $50/day
    total_reimbursement = max(total_reimbursement, minimum_reimbursement)
    
    return round(total_reimbursement, 2)

# === TEST CASES BASED ON INTERVIEW EXAMPLES ===
if __name__ == "__main__":
    # Marcus's examples
    print("Marcus's Cleveland-Detroit trips:")
    print(f"Trip 1: {calculate_legacy_reimbursement(3, 180, 200)}")  # Should be around $847
    print(f"Trip 2: {calculate_legacy_reimbursement(3, 180, 200)}")  # Should be around $623
    
    # Marcus's 8-day hustle trip
    print(f"\nMarcus's 8-day Ohio/Indiana trip: {calculate_legacy_reimbursement(8, 2400, 800)}")
    
    # Kevin's sweet spot combo
    print(f"\nKevin's sweet spot (5 days, 900 miles, $450): {calculate_legacy_reimbursement(5, 900, 450)}")
    
    # High mileage examples
    print(f"\nMarcus's Nashville trip (600 miles): {calculate_legacy_reimbursement(3, 600, 300)}")
    print(f"Dave's 800-mile trip: {calculate_legacy_reimbursement(4, 800, 400)}")
    
    # Small receipt penalties
    print(f"\nSmall receipt penalty: {calculate_legacy_reimbursement(2, 100, 30)}")
    print(f"No receipts: {calculate_legacy_reimbursement(2, 100, 0)}")