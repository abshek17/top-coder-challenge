#!/usr/bin/env python3
"""
Targeted constant adjustments to reduce +$32.78 systematic over-prediction bias.
This script applies minimal adjustments to key constants in legacy_calculate.py.
"""

def apply_bias_reduction_fixes():
    """Apply targeted fixes to reduce systematic over-prediction bias."""
    
    # Read the current legacy_calculate.py
    with open('legacy_calculate.py', 'r') as f:
        content = f.read()
    
    # 1. Reduce base per diem from $100 to $97 (-3% reduction)
    content = content.replace(
        'base_per_diem = trip_duration_days * 100',
        'base_per_diem = trip_duration_days * 97  # Reduced from 100 to fix +$32 bias'
    )
    
    # 2. Reduce low-mileage compensation from $15 to $10 (-33% reduction)
    content = content.replace(
        'low_mileage_compensation = trip_duration_days * 15  # Small $15/day bonus',
        'low_mileage_compensation = trip_duration_days * 10  # Reduced from 15 to fix +$39 over-prediction'
    )
    
    # 3. Reduce mileage bonuses by ~15%
    content = content.replace(
        'mileage_bonus = 300  # Strong bonus for very high mileage',
        'mileage_bonus = 255  # Reduced from 300 to fix over-prediction bias'
    )
    content = content.replace(
        'mileage_bonus = 200  # Good mileage bonus',
        'mileage_bonus = 170  # Reduced from 200 to fix over-prediction bias'
    )
    content = content.replace(
        'mileage_bonus = 120  # Moderate mileage bonus',
        'mileage_bonus = 100  # Reduced from 120 to fix over-prediction bias'
    )
    content = content.replace(
        'mileage_bonus = 60   # Small mileage bonus',
        'mileage_bonus = 50   # Reduced from 60 to fix over-prediction bias'
    )
    
    # 4. Reduce rounding bonus from $10 to $5
    content = content.replace(
        'rounding_bonus = 10  # Small bonus for "lucky" receipt totals',
        'rounding_bonus = 5   # Reduced from 10 to fix over-prediction bias'
    )
    
    # 5. Reduce single-day high receipt constants by ~$50-100
    content = content.replace(
        'total_reimbursement = mileage_reimbursement + 1000  # Reduced from 1200',
        'total_reimbursement = mileage_reimbursement + 950   # Further reduced to fix bias'
    )
    content = content.replace(
        'total_reimbursement = mileage_reimbursement + 800   # Reduced from 1000',
        'total_reimbursement = mileage_reimbursement + 750   # Further reduced to fix bias'
    )
    content = content.replace(
        'total_reimbursement = mileage_reimbursement + 600   # Reduced from 800',
        'total_reimbursement = mileage_reimbursement + 550   # Further reduced to fix bias'
    )
    content = content.replace(
        'total_reimbursement = mileage_reimbursement + 400   # Reduced from 600',
        'total_reimbursement = mileage_reimbursement + 350   # Further reduced to fix bias'
    )
    
    # Save the updated algorithm
    with open('legacy_calculate_bias_fixed.py', 'w') as f:
        f.write(content)
    
    print("✅ Applied bias reduction fixes!")
    print("   • Base per diem: $100 → $97 (-3%)")
    print("   • Low-mileage compensation: $15 → $10 (-33%)")
    print("   • Mileage bonuses reduced by ~15%")
    print("   • Rounding bonus: $10 → $5 (-50%)")
    print("   • Single-day constants reduced by ~$50")
    print("\n📁 Saved as: legacy_calculate_bias_fixed.py")
    print("💡 Expected bias reduction: ~$25-35 per case")

def quick_test_bias_reduction():
    """Quick test to estimate bias reduction impact."""
    import json
    from legacy_calculate_bias_fixed import calculate_legacy_reimbursement
    
    # Load test cases
    with open('public_cases.json', 'r') as f:
        test_cases = json.load(f)
    
    # Test on first 100 cases for quick feedback
    total_error = 0
    total_abs_error = 0
    
    for i, case in enumerate(test_cases[:100]):
        trip_duration = case['input']['trip_duration_days']
        miles_traveled = case['input']['miles_traveled']
        receipts_amount = case['input']['total_receipts_amount']
        expected_output = case['expected_output']
        
        actual_output = calculate_legacy_reimbursement(
            trip_duration, miles_traveled, receipts_amount
        )
        
        error = actual_output - expected_output
        total_error += error
        total_abs_error += abs(error)
    
    mean_error = total_error / 100
    mean_abs_error = total_abs_error / 100
    
    print(f"\n📊 Quick Test Results (100 cases):")
    print(f"   Mean Error: ${mean_error:.2f} (was +$32.78)")
    print(f"   Mean Absolute Error: ${mean_abs_error:.2f}")
    print(f"   Bias Reduction: ${32.78 - mean_error:.2f}")

if __name__ == '__main__':
    print("🎯 Applying Targeted Bias Reduction Fixes...")
    apply_bias_reduction_fixes()
    
    print("\n🧪 Running quick test...")
    try:
        quick_test_bias_reduction()
    except ImportError:
        print("   (Run this after creating the fixed file)")
        print("   python quick_test_bias_reduction.py")
