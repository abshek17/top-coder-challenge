#!/usr/bin/env python3
"""
Full evaluation of bias-fixed algorithm on all 1000 cases.
"""

import json
from legacy_calculate_bias_fixed import calculate_legacy_reimbursement

def evaluate_bias_fixed_algorithm():
    """Evaluate the bias-fixed algorithm on all 1000 test cases."""
    
    # Load test cases
    with open('public_cases.json', 'r') as f:
        test_cases = json.load(f)
    
    print(f"📊 Evaluating bias-fixed algorithm on {len(test_cases)} cases...")
    
    total_error = 0
    total_abs_error = 0
    under_predictions = 0
    over_predictions = 0
    errors = []
    
    for i, case in enumerate(test_cases):
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
        errors.append(error)
        
        if error < 0:
            under_predictions += 1
        elif error > 0:
            over_predictions += 1
        
        # Progress indicator
        if (i + 1) % 200 == 0:
            print(f"   Processed {i + 1} cases...")
    
    # Calculate statistics
    mean_error = total_error / len(test_cases)
    mean_abs_error = total_abs_error / len(test_cases)
    
    # Calculate correlation
    expected_values = [case['expected_output'] for case in test_cases]
    actual_values = []
    
    for case in test_cases:
        trip_duration = case['input']['trip_duration_days']
        miles_traveled = case['input']['miles_traveled']
        receipts_amount = case['input']['total_receipts_amount']
        
        actual_output = calculate_legacy_reimbursement(
            trip_duration, miles_traveled, receipts_amount
        )
        actual_values.append(actual_output)
    
    # Simple correlation calculation
    n = len(expected_values)
    sum_expected = sum(expected_values)
    sum_actual = sum(actual_values)
    sum_exp_sq = sum(x**2 for x in expected_values)
    sum_act_sq = sum(x**2 for x in actual_values)
    sum_exp_act = sum(expected_values[i] * actual_values[i] for i in range(n))
    
    correlation = ((n * sum_exp_act - sum_expected * sum_actual) / 
                  ((n * sum_exp_sq - sum_expected**2) * (n * sum_act_sq - sum_actual**2))**0.5)
    
    # Error ranges
    within_25 = sum(1 for e in errors if abs(e) <= 25)
    within_50 = sum(1 for e in errors if abs(e) <= 50)
    within_100 = sum(1 for e in errors if abs(e) <= 100)
    
    print(f"\n{'='*60}")
    print(f"BIAS-FIXED ALGORITHM RESULTS")
    print(f"{'='*60}")
    
    print(f"\n📊 OVERALL PERFORMANCE:")
    print(f"   Total Cases: {len(test_cases):,}")
    print(f"   Mean Error: ${mean_error:.2f} (was +$32.78)")
    print(f"   Mean Absolute Error: ${mean_abs_error:.2f} (was $164.64)")
    print(f"   Correlation: {correlation:.4f} (was 0.9016)")
    
    print(f"\n🎯 BIAS IMPROVEMENT:")
    print(f"   Bias Reduction: ${32.78 - mean_error:.2f}")
    print(f"   Under-predictions: {under_predictions} ({under_predictions/len(test_cases)*100:.1f}%)")
    print(f"   Over-predictions: {over_predictions} ({over_predictions/len(test_cases)*100:.1f}%)")
    
    print(f"\n📈 ACCURACY DISTRIBUTION:")
    print(f"   Within ±$25: {within_25} ({within_25/len(test_cases)*100:.1f}%)")
    print(f"   Within ±$50: {within_50} ({within_50/len(test_cases)*100:.1f}%)")
    print(f"   Within ±$100: {within_100} ({within_100/len(test_cases)*100:.1f}%)")
    
    print(f"\n🏆 EXTREME CASES:")
    min_error = min(errors)
    max_error = max(errors)
    print(f"   Worst Under-prediction: ${min_error:.2f}")
    print(f"   Worst Over-prediction: ${max_error:.2f}")
    
    return {
        'mean_error': mean_error,
        'mean_abs_error': mean_abs_error,
        'correlation': correlation,
        'under_predictions': under_predictions,
        'over_predictions': over_predictions,
        'within_50': within_50,
        'within_100': within_100
    }

if __name__ == '__main__':
    results = evaluate_bias_fixed_algorithm()
    
    print(f"\n💡 SUMMARY OF IMPROVEMENTS:")
    print(f"   Mean Error: +$32.78 → ${results['mean_error']:.2f}")
    print(f"   Mean Absolute Error: $164.64 → ${results['mean_abs_error']:.2f}")
    print(f"   Correlation: 0.9016 → {results['correlation']:.4f}")
    print(f"   Within ±$50: 21.0% → {results['within_50']/1000*100:.1f}%")
    print(f"   Within ±$100: 40.6% → {results['within_100']/1000*100:.1f}%")
