import math
from datetime import datetime

def calculate_legacy_reimbursement(trip_duration_days, miles_traveled, total_receipts_amount):
    """
    Initial rule set based on employee in        elif receipts_per_day > 450:
            # Very high receipts per day - SYSTEMATIC FIX based on pattern analysis
            if trip_duration_days == 5:
                # 5-day trips with very high receipts - LESS HARSH PENALTIES
                # Pattern analysis: 95% under-predicted by avg $339
                if receipts_per_day > 500:
                    # Extremely high - need much less harsh penalty 
                    total_reimbursement *= 0.95  # Increased from 0.85
                else:
                    # Very high but not extreme - light penalty only
                    total_reimbursement *= 1.0  # Increased from 0.75 (no penalty now)
            else:
                # 4-day trips with extreme receipts - SYSTEMATIC FIX
                # Pattern analysis: 97% under-predicted by avg $381
                total_reimbursement *= 0.95  # Increased from 0.8"""
    
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
    
    # TARGETED FIX: Small compensation for low-mileage trips (<50 mi/day had -$125 error)
    if miles_per_day < 50:
        low_mileage_compensation = trip_duration_days * 10  # Reduced from 15 to fix +$39 over-prediction
        mileage_reimbursement += low_mileage_compensation
    
    # === PER DIEM BASE ===
    # Lisa: "$100 a day seems to be the base"
    base_per_diem = trip_duration_days * 97  # Reduced from 100 to fix +$32 bias
    
    # === RECEIPT PROCESSING (Non-linear) ===
    # Lisa: "Medium-high amounts—like $600-800—seem to get really good treatment"
    # Marcus: "$2,000 expense weeks that got me less than $1,200 weeks"
    receipt_reimbursement = 0
    
    if total_receipts_amount < 50:
        # Penalty for very small receipts - Dave: "better off submitting nothing"
        receipt_reimbursement = total_receipts_amount * 0.40  # Harsh penalty
    elif total_receipts_amount <= 600:
        # Standard reimbursement
        receipt_reimbursement = total_receipts_amount * 0.75
    elif total_receipts_amount <= 800:
        # Sweet spot - best treatment
        receipt_reimbursement = total_receipts_amount * 0.85
    elif total_receipts_amount <= 1200:
        # Declining returns
        receipt_reimbursement = 800 * 0.85 + (total_receipts_amount - 800) * 0.60
    elif total_receipts_amount <= 2000:
        # Strong diminishing returns  
        receipt_reimbursement = 800 * 0.85 + 400 * 0.60 + (total_receipts_amount - 1200) * 0.30
    else:
        # Marcus: "2000 expense weeks get less than 1200 weeks" - extreme penalty
        receipt_reimbursement = 800 * 0.85 + 400 * 0.60 + 800 * 0.30 + (total_receipts_amount - 2000) * 0.10
    
    # === RECOMMENDATION #4: CONSOLIDATE COMPETING MULTIPLIERS ===
    # Previously had 5+ multipliers that competed: efficiency, length, daily_spending, weekend, sweet_spot, tier-specific
    # Now consolidating to 2 CORE ADJUSTMENTS that don't conflict
    
    # CORE ADJUSTMENT 1: TRIP EFFICIENCY (combines efficiency + trip length)
    # Kevin: "sweet spot around 180-220 miles per day" + Lisa: "5-day trips almost always get a bonus"
    trip_efficiency_multiplier = 1.0
    
    # First apply efficiency bonus/penalty based on miles per day
    if 180 <= miles_per_day <= 220:
        base_efficiency = 1.10  # Optimal efficiency range
    elif 120 <= miles_per_day < 180:
        base_efficiency = 1.02  # Good efficiency  
    elif 50 <= miles_per_day < 120:
        base_efficiency = 1.08  # BIAS FIX: boost this problematic range
    elif 200 <= miles_per_day < 250:
        base_efficiency = 1.01  # Cap excessive efficiency bonuses
    elif miles_per_day > 300:
        base_efficiency = 0.95  # Penalty for excessive driving
    else:  # miles_per_day < 50
        base_efficiency = 1.0   # No penalty for low efficiency
    
    # Then apply trip duration modifier (instead of separate length_multiplier)
    if trip_duration_days == 5:
        # 5-day sweet spot bonus
        trip_efficiency_multiplier = base_efficiency * 1.05  # Combine efficiency with 5-day bonus
    elif trip_duration_days in [4, 6]:
        # Optimal business trip range  
        trip_efficiency_multiplier = base_efficiency * 1.02  # Small bonus for good duration
    elif trip_duration_days in [2, 3]:
        # Short trips get reduced efficiency bonuses
        trip_efficiency_multiplier = base_efficiency * 0.98  # Slight penalty for very short
    elif trip_duration_days > 7:
        # Long trips get capped efficiency bonuses
        if trip_duration_days <= 14:
            trip_efficiency_multiplier = base_efficiency * 0.95  # Reduce efficiency bonus for long trips
        else:
            trip_efficiency_multiplier = base_efficiency * 0.90  # Further reduce for very long trips
    else:  # Single day trips
        trip_efficiency_multiplier = base_efficiency * 0.92  # Single-day gets limited efficiency bonus
    
    # CORE ADJUSTMENT 2: SPENDING REASONABLENESS
    # Consolidates daily_spending + receipt tier adjustments into one coherent system
    spending_reasonableness_multiplier = 1.0
    
    if receipts_per_day > 200:  # Very high daily spending
        spending_reasonableness_multiplier = 0.88  # Strong penalty for excessive spending
    elif receipts_per_day > 150:  # High daily spending  
        spending_reasonableness_multiplier = 0.92  # Moderate penalty
    elif receipts_per_day < 30:  # Very low daily spending
        spending_reasonableness_multiplier = 0.96  # Small penalty for suspiciously low spending
    # else: reasonable spending (30-150/day) gets no adjustment (1.0)
    
    # === ROUNDING BUG BONUS ===
    # Lisa: "If your receipts end in 49 or 99 cents, you often get a little extra money"
    rounding_bonus = 0
    cents = int((total_receipts_amount * 100) % 100)
    if cents in [49, 99]:
        rounding_bonus = 5   # Reduced from 10 to fix over-prediction bias
    
    # === FINAL CALCULATION ===
    # Key insight: Use EITHER per diem OR receipts, not both (Lisa's insight)
    # Plus mileage reimbursement
    
    # Choose better of per diem vs receipt reimbursement
    lodging_reimbursement = max(base_per_diem, receipt_reimbursement)
    
    base_reimbursement = mileage_reimbursement + lodging_reimbursement
     # Apply the 2 CORE ADJUSTMENTS (no more competing multipliers)
    total_reimbursement = (base_reimbursement * trip_efficiency_multiplier * 
                          spending_reasonableness_multiplier) + rounding_bonus
    
    # === MILEAGE BONUSES (for all trip lengths) ===
    # High mileage should be rewarded regardless of trip duration
    # BUT single-day trips are suspicious and should be limited
    mileage_bonus = 0
    if trip_duration_days == 1:
        # Single-day trips get limited mileage bonuses
        if miles_traveled > 800:
            mileage_bonus = 50  # Very limited bonus for single-day high mileage
        elif miles_traveled > 600:
            mileage_bonus = 30
    else:
        # Multi-day trips get full mileage bonuses
        if miles_traveled > 1000:
            mileage_bonus = 255  # Reduced from 300 to fix over-prediction bias
        elif miles_traveled > 800:
            mileage_bonus = 170  # Reduced from 200 to fix over-prediction bias
        elif miles_traveled > 600:
            mileage_bonus = 100  # Reduced from 120 to fix over-prediction bias
        elif miles_traveled > 400:
            mileage_bonus = 50   # Reduced from 60 to fix over-prediction bias
    
    total_reimbursement += mileage_bonus

    # Weekend penalty for 6-7 day trips (days 6 and 7 roll into weekend)
    # TARGETED FIX: Reduce weekend penalty from 10% to 8% (6-7 days had -$128 error)
    if trip_duration_days in [6, 7]:
        total_reimbursement *= 0.92  # 8% penalty for weekend days (was 0.90/10%)

    # === SWEET SPOT COMBO BONUS ===
    # Marcus's incredible 8-day trip: optimal duration + high mileage + reasonable spending
    if 6 <= trip_duration_days <= 8 and miles_traveled > 800 and receipts_per_day < 200:
        # This is the "incredible" business travel pattern
        if miles_traveled > 1000:
            total_reimbursement *= 1.35  # Major bonus for extreme business hustle
        else:
            total_reimbursement *= 1.25  # Strong bonus for business travel
    elif 6 <= trip_duration_days <= 8 and miles_traveled > 600:
        total_reimbursement *= 1.15  # Good bonus for decent business travel
    
    # === TRIP DURATION TIER SYSTEM ===
    # SIMPLIFIED SINGLE-DAY CALCULATION
    # Recommendation #1: Consolidate complex branching to 3-4 clear tiers
    
    if trip_duration_days == 1:
        # SINGLE-DAY SIMPLIFIED CALCULATION
        # Consolidate 50+ conditions into 4 clear receipt tiers
        
        if total_receipts_amount >= 1000:
            # Tier 1: Very High Receipts ($1000+) - BIAS FIX
            single_day_bonus = 1000  # Increased from 800 to fix -$119.75 bias
        elif total_receipts_amount >= 300:
            # Tier 2: Medium-High Receipts ($300-999) - BIAS FIX
            single_day_bonus = 500   # Increased from 400 to fix under-prediction
        elif total_receipts_amount >= 100:
            # Tier 3: Medium Receipts ($100-299) - BIAS FIX
            single_day_bonus = 300   # Increased from 200 to fix under-prediction
        else:
            # Tier 4: Low Receipts (under $100) - BIAS FIX
            if miles_traveled > 800:
                single_day_bonus = 400  # Increased from 300 for high-mileage
            else:
                single_day_bonus = 200  # Increased from 100 for base rate
        
        total_reimbursement = mileage_reimbursement + single_day_bonus
            
    elif trip_duration_days in [2, 3]:
        # SHORT TRIP TIER - Simplified adjustments with BIAS FIXES
        if receipts_per_day > 400:  # Ultra/extreme receipts
            # High receipt short trips generally under-predicted
            total_reimbursement *= 1.2   # Increased from 1.15 for bias fix
        elif receipts_per_day > 200:
            # Medium-high receipts
            total_reimbursement *= 1.15  # Increased from 1.1 for bias fix
        elif receipts_per_day < 100:
            # Low receipts - need improvement
            total_reimbursement *= 1.1   # Increased from 1.05 for bias fix
        else:
            # Standard/medium receipts
            total_reimbursement *= 1.1   # Increased from 1.05 for bias fix
            
    elif trip_duration_days in [4, 5]:
        # 4-5 DAY TRIPS - Simplified systematic adjustments
        if receipts_per_day > 450:
            # Very high receipts per day
            if trip_duration_days == 5:
                # 5-day trips with very high receipts
                total_reimbursement *= 1.1   # Moderate bonus
            else:
                # 4-day trips with very high receipts
                total_reimbursement *= 1.2   # Higher bonus for 4-day high receipts
        elif receipts_per_day > 300:
            # High receipts per day
            if trip_duration_days == 4:
                total_reimbursement *= 1.15  # Good bonus for 4-day high receipts
            else:
                total_reimbursement *= 1.1   # Standard bonus for 5-day high receipts
        else:
            # Standard handling for reasonable spending
            if trip_duration_days == 5:
                if receipts_per_day < 50:  # Very low receipts
                    total_reimbursement *= 0.9   # Penalty for very low spending
                else:
                    total_reimbursement *= 1.1   # Good bonus for normal 5-day trips
            else:
                total_reimbursement *= 1.05  # Standard bonus for 4-day trips
    
    elif trip_duration_days == 6:
        # 6-day trips - BIAS FIX: Was severely under-predicting by -$200.43
        if receipts_per_day < 50:
            total_reimbursement *= 1.0   # Remove harsh penalty (was 0.8)
        elif receipts_per_day >= 300:
            total_reimbursement *= 1.15  # Boost high receipts (was 0.9 penalty!)
        elif receipts_per_day >= 150:
            total_reimbursement *= 1.25  # Increase medium-high bonus (was 1.1)
        else:
            total_reimbursement *= 1.2   # Increase standard bonus (was 1.05)
            
    elif trip_duration_days == 7:
        # 7-day trips - BIAS FIX: Was under-predicting by -$81.37
        if receipts_per_day >= 200:
            total_reimbursement *= 1.35  # Increase high receipts bonus (was 1.25)
        elif receipts_per_day >= 100:
            total_reimbursement *= 1.25  # Increase medium receipts bonus (was 1.15)
        elif receipts_per_day < 50:
            total_reimbursement *= 1.0   # Remove low receipts penalty (was 0.85)
        else:
            total_reimbursement *= 1.2   # Increase standard bonus (was 1.1)
            
    elif trip_duration_days >= 8:
        # Long trips (8+ days) - Simplified approach
        if trip_duration_days >= 14:
            # Very long trips (14+ days)
            if receipts_per_day >= 150:
                total_reimbursement *= 1.25  # High spending bonus
            elif receipts_per_day < 75:
                total_reimbursement *= 1.15  # Low spending adjustment
            else:
                total_reimbursement *= 1.2   # Medium spending bonus
        elif trip_duration_days >= 11:
            # 11-13 day trips
            if receipts_per_day >= 150:
                total_reimbursement *= 1.3   # High receipts bonus
            elif receipts_per_day >= 100:
                total_reimbursement *= 1.25  # Medium receipts bonus
            else:
                total_reimbursement *= 1.15  # Low receipts bonus
        elif trip_duration_days >= 9:
            # 9-10 day trips  
            if receipts_per_day >= 150:
                total_reimbursement *= 1.2   # High receipts bonus
            elif receipts_per_day >= 100:
                total_reimbursement *= 1.25  # Medium receipts bonus
            else:
                total_reimbursement *= 1.1   # Low receipts bonus
        else:  # 8 days
            # 8-day trips
            if receipts_per_day >= 150:
                total_reimbursement *= 1.15  # High receipts bonus
            elif receipts_per_day >= 100:
                total_reimbursement *= 1.2   # Medium receipts bonus
            elif receipts_per_day < 75:
                total_reimbursement *= 0.95  # Low receipts penalty
            else:
                total_reimbursement *= 1.1   # Standard bonus
        
        # General long-trip adjustments
        if receipts_per_day < 50:
            total_reimbursement *= 0.75  # Penalty for very low spending on long trips
        
        # Additional bonuses for legitimate long business travel patterns (but limited)
        if trip_duration_days <= 11 and miles_traveled > 800 and receipts_per_day >= 50:
            total_reimbursement *= 1.05  # Small high-mileage bonus (only if spending is reasonable)
    
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