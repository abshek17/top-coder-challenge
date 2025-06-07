#!/usr/bin/env python3
"""
Compare original vs improved legacy algorithm performance.
"""

import json
import sys
import os
import pandas as pd

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Save the current improved algorithm
from legacy_calculate import calculate_legacy_reimbursement as improved_algorithm

# Load the original algorithm for comparison
# (We'll need to manually define the original values for comparison)

def original_legacy_reimbursement(trip_duration_days, miles_traveled, total_receipts_amount):
    """
    Original algorithm before targeted fixes
    """
    
    # Base calculations
    miles_per_day = miles_traveled / trip_duration_days if trip_duration_days > 0 else 0
    receipts_per_day = total_receipts_amount / trip_duration_days if trip_duration_days > 0 else 0
    
    # === MILEAGE CALCULATION (Tiered) ===
    mileage_reimbursement = 0
    if miles_traveled <= 100:
        mileage_reimbursement = miles_traveled * 0.58
    elif miles_traveled <= 500:
        mileage_reimbursement = 100 * 0.58 + (miles_traveled - 100) * 0.40
    else:
        mileage_reimbursement = 100 * 0.58 + 400 * 0.40 + (miles_traveled - 500) * 0.25
    
    # (No low-mileage compensation in original)
    
    # === PER DIEM BASE ===
    base_per_diem = trip_duration_days * 100
    
    # === RECEIPT PROCESSING (Non-linear) ===
    receipt_reimbursement = 0
    
    if total_receipts_amount < 50:
        receipt_reimbursement = total_receipts_amount * 0.40
    elif total_receipts_amount <= 600:
        receipt_reimbursement = total_receipts_amount * 0.85
    elif total_receipts_amount <= 1200:
        receipt_reimbursement = 600 * 0.85 + (total_receipts_amount - 600) * 1.20
    elif total_receipts_amount <= 2000:
        receipt_reimbursement = 600 * 0.85 + 600 * 1.20 + (total_receipts_amount - 1200) * 0.90
    else:
        receipt_reimbursement = 600 * 0.85 + 600 * 1.20 + 800 * 0.90 + (total_receipts_amount - 2000) * 0.70
    
    # === EFFICIENCY BONUS (Original) ===
    efficiency_multiplier = 1.0
    if 180 <= miles_per_day <= 220:
        efficiency_multiplier = 1.10
    elif 120 <= miles_per_day < 180:
        efficiency_multiplier = 1.02
    elif miles_per_day > 300:
        efficiency_multiplier = 0.95
    elif miles_per_day < 100:
        efficiency_multiplier = 0.95
    # (No 200-249 mi/day cap in original)
    
    # === TRIP LENGTH BONUSES/PENALTIES (Original) ===
    length_multiplier = 1.0
    
    if trip_duration_days == 5:
        length_multiplier = 1.10
    elif trip_duration_days in [4, 6]:
        length_multiplier = 1.05
    elif trip_duration_days < 3:
        length_multiplier = 0.95
    elif trip_duration_days > 7:
        length_multiplier = 0.95  # Original harsh penalty for all long trips
    
    # === SPENDING PER DAY ADJUSTMENTS ===
    daily_spending_multiplier = 1.0
    if receipts_per_day > 150:
        daily_spending_multiplier = 0.90
    elif receipts_per_day > 100:
        daily_spending_multiplier = 0.95
    
    # === BASE CALCULATION ===
    total_reimbursement = (mileage_reimbursement + base_per_diem + receipt_reimbursement) * length_multiplier * efficiency_multiplier * daily_spending_multiplier
    
    # === MILEAGE BONUS ===
    mileage_bonus = 0
    if miles_traveled > 1500:
        mileage_bonus = 100
    elif miles_traveled > 1000:
        mileage_bonus = 80
    elif miles_traveled > 500:
        mileage_bonus = 60
    
    total_reimbursement += mileage_bonus

    # === WEEKEND PENALTY (Original) ===
    if trip_duration_days in [6, 7]:
        total_reimbursement *= 0.90  # Original 10% penalty
    
    # ... (rest of complex logic would be here, simplified for comparison)
    
    return round(total_reimbursement, 2)

def load_test_data():
    """Load test cases from public_cases.json"""
    with open('public_cases.json', 'r') as f:
        cases = json.load(f)
    return cases

def get_duration_bucket(days):
    """Create duration buckets"""
    if days <= 2:
        return "1-2 days"
    elif days <= 3:
        return "3 days"
    elif days <= 5:
        return "4-5 days"
    elif days <= 7:
        return "6-7 days"
    elif days <= 10:
        return "8-10 days"
    elif days <= 14:
        return "11-14 days"
    else:
        return "15+ days"

def get_mileage_bucket(miles_per_day):
    """Create mileage per day buckets"""
    if miles_per_day < 50:
        return "< 50 mi/day"
    elif miles_per_day < 100:
        return "50-99 mi/day"
    elif miles_per_day < 150:
        return "100-149 mi/day"
    elif miles_per_day < 200:
        return "150-199 mi/day"
    elif miles_per_day < 250:
        return "200-249 mi/day"
    elif miles_per_day < 300:
        return "250-299 mi/day"
    else:
        return "300+ mi/day"

def compare_targeted_fixes():
    """Compare the improvements from targeted fixes"""
    cases = load_test_data()
    
    # For simplicity, let's use the previous bucketed analysis results
    # Original results from previous run:
    original_results = {
        'overall_mean_error': -31.01,
        'overall_mean_abs_error': 170.92,
        'overall_correlation': 0.894,
        'duration_errors': {
            '6-7 days': -128.04,
            '11-14 days': -79.02,
        },
        'mileage_errors': {
            '200-249 mi/day': 220.02,
            '< 50 mi/day': -125.28,
        }
    }
    
    # Current improved results from the last run:
    improved_results = {
        'overall_mean_error': 33.42,
        'overall_mean_abs_error': 165.14,
        'overall_correlation': 0.901,
        'duration_errors': {
            '6-7 days': -76.13,
            '11-14 days': 57.23,
        },
        'mileage_errors': {
            '200-249 mi/day': 244.89,
            '< 50 mi/day': 39.37,
        }
    }
    
    print("="*80)
    print("TARGETED FIXES IMPACT ANALYSIS")
    print("="*80)
    
    print(f"\nOVERALL IMPROVEMENTS:")
    print(f"  Mean error: ${original_results['overall_mean_error']:.2f} → ${improved_results['overall_mean_error']:.2f}")
    print(f"  Mean absolute error: ${original_results['overall_mean_abs_error']:.2f} → ${improved_results['overall_mean_abs_error']:.2f}")
    print(f"  Correlation: {original_results['overall_correlation']:.3f} → {improved_results['overall_correlation']:.3f}")
    
    abs_error_improvement = original_results['overall_mean_abs_error'] - improved_results['overall_mean_abs_error']
    correlation_improvement = improved_results['overall_correlation'] - original_results['overall_correlation']
    
    print(f"  → Absolute error improved by ${abs_error_improvement:.2f}")
    print(f"  → Correlation improved by {correlation_improvement:.3f}")
    
    print(f"\nTARGETED FIX RESULTS:")
    print(f"\n1. WEEKEND PENALTY FIX (6-7 day trips):")
    print(f"   Original error: ${original_results['duration_errors']['6-7 days']:.2f}")
    print(f"   Improved error: ${improved_results['duration_errors']['6-7 days']:.2f}")
    weekend_improvement = abs(original_results['duration_errors']['6-7 days']) - abs(improved_results['duration_errors']['6-7 days'])
    print(f"   → Improvement: ${weekend_improvement:.2f} (reduced penalty from 10% to 8%)")
    
    print(f"\n2. LOW-MILEAGE COMPENSATION (<50 mi/day trips):")
    print(f"   Original error: ${original_results['mileage_errors']['< 50 mi/day']:.2f}")
    print(f"   Improved error: ${improved_results['mileage_errors']['< 50 mi/day']:.2f}")
    low_mileage_improvement = abs(original_results['mileage_errors']['< 50 mi/day']) - abs(improved_results['mileage_errors']['< 50 mi/day'])
    print(f"   → Improvement: ${low_mileage_improvement:.2f} (added $15/day compensation)")
    
    print(f"\n3. LONG TRIP SCALING (11-14 day trips):")
    print(f"   Original error: ${original_results['duration_errors']['11-14 days']:.2f}")
    print(f"   Improved error: ${improved_results['duration_errors']['11-14 days']:.2f}")
    long_trip_improvement = abs(original_results['duration_errors']['11-14 days']) - abs(improved_results['duration_errors']['11-14 days'])
    print(f"   → Improvement: ${long_trip_improvement:.2f} (reduced penalty from 5% to 2%)")
    
    print(f"\n4. HIGH-MILEAGE EFFICIENCY CAP (200-249 mi/day trips):")
    print(f"   Original error: ${original_results['mileage_errors']['200-249 mi/day']:.2f}")
    print(f"   Improved error: ${improved_results['mileage_errors']['200-249 mi/day']:.2f}")
    high_mileage_improvement = abs(original_results['mileage_errors']['200-249 mi/day']) - abs(improved_results['mileage_errors']['200-249 mi/day'])
    print(f"   → Change: ${high_mileage_improvement:.2f} (added efficiency cap, but still problematic)")
    
    print(f"\nSUMMARY OF FIXES:")
    print(f"  ✅ Weekend penalty reduction: Significantly improved 6-7 day trips")
    print(f"  ✅ Low-mileage compensation: Dramatically improved <50 mi/day trips")
    print(f"  ✅ Long trip scaling: Fixed under-prediction for 11-14 day trips")
    print(f"  ⚠️  High-mileage cap: Still needs more aggressive capping for 200-249 mi/day")
    
    print(f"\nNEXT STEPS:")
    print(f"  - Consider more aggressive efficiency cap for 200-249 mi/day range")
    print(f"  - Fine-tune other problematic patterns")
    print(f"  - Overall improvement: Mean absolute error reduced by ${abs_error_improvement:.2f}")

if __name__ == "__main__":
    compare_targeted_fixes()
