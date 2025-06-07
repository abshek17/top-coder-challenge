#!/usr/bin/env python3
"""
Compare original vs bias-fixed algorithm performance.
"""

import json
import matplotlib.pyplot as plt
import numpy as np
from legacy_calculate import calculate_legacy_reimbursement as original_calc
from legacy_calculate_bias_fixed import calculate_legacy_reimbursement as fixed_calc

def compare_algorithms():
    """Compare original vs bias-fixed algorithm."""
    
    # Load test cases
    with open('public_cases.json', 'r') as f:
        test_cases = json.load(f)
    
    print("📊 Comparing original vs bias-fixed algorithms...")
    
    original_errors = []
    fixed_errors = []
    expected_values = []
    
    for case in test_cases:
        trip_duration = case['input']['trip_duration_days']
        miles_traveled = case['input']['miles_traveled']
        receipts_amount = case['input']['total_receipts_amount']
        expected_output = case['expected_output']
        
        # Original algorithm
        original_output = original_calc(trip_duration, miles_traveled, receipts_amount)
        original_error = original_output - expected_output
        original_errors.append(original_error)
        
        # Fixed algorithm
        fixed_output = fixed_calc(trip_duration, miles_traveled, receipts_amount)
        fixed_error = fixed_output - expected_output
        fixed_errors.append(fixed_error)
        
        expected_values.append(expected_output)
    
    # Create comparison visualization
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    
    # 1. Error distribution comparison
    ax1 = axes[0, 0]
    ax1.hist(original_errors, bins=50, alpha=0.6, label='Original', color='red')
    ax1.hist(fixed_errors, bins=50, alpha=0.6, label='Bias-Fixed', color='blue')
    ax1.axvline(np.mean(original_errors), color='red', linestyle='--', 
                label=f'Original Mean: ${np.mean(original_errors):.2f}')
    ax1.axvline(np.mean(fixed_errors), color='blue', linestyle='--', 
                label=f'Fixed Mean: ${np.mean(fixed_errors):.2f}')
    ax1.axvline(0, color='black', linestyle='-', alpha=0.3, label='Perfect Prediction')
    ax1.set_xlabel('Prediction Error ($)')
    ax1.set_ylabel('Frequency')
    ax1.set_title('Error Distribution Comparison')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 2. Absolute error comparison
    ax2 = axes[0, 1]
    original_abs_errors = [abs(e) for e in original_errors]
    fixed_abs_errors = [abs(e) for e in fixed_errors]
    
    ax2.hist(original_abs_errors, bins=50, alpha=0.6, label='Original', color='red')
    ax2.hist(fixed_abs_errors, bins=50, alpha=0.6, label='Bias-Fixed', color='blue')
    ax2.axvline(np.mean(original_abs_errors), color='red', linestyle='--', 
                label=f'Original MAE: ${np.mean(original_abs_errors):.2f}')
    ax2.axvline(np.mean(fixed_abs_errors), color='blue', linestyle='--', 
                label=f'Fixed MAE: ${np.mean(fixed_abs_errors):.2f}')
    ax2.set_xlabel('Absolute Error ($)')
    ax2.set_ylabel('Frequency')
    ax2.set_title('Absolute Error Distribution')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # 3. Scatter plot comparison
    ax3 = axes[1, 0]
    ax3.scatter(expected_values, [e + exp for e, exp in zip(original_errors, expected_values)], 
               alpha=0.5, s=20, label='Original', color='red')
    ax3.scatter(expected_values, [e + exp for e, exp in zip(fixed_errors, expected_values)], 
               alpha=0.5, s=20, label='Bias-Fixed', color='blue')
    
    min_val = min(expected_values)
    max_val = max(expected_values)
    ax3.plot([min_val, max_val], [min_val, max_val], 'k--', alpha=0.8, label='Perfect Prediction')
    ax3.set_xlabel('Expected Output ($)')
    ax3.set_ylabel('Actual Output ($)')
    ax3.set_title('Prediction Accuracy Comparison')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # 4. Error improvement by expected value
    ax4 = axes[1, 1]
    # Bin by expected value and show improvement
    bins = np.percentile(expected_values, [0, 20, 40, 60, 80, 100])
    bin_labels = ['0-20%', '20-40%', '40-60%', '60-80%', '80-100%']
    
    original_binned = []
    fixed_binned = []
    
    for i in range(len(bins)-1):
        mask = (np.array(expected_values) >= bins[i]) & (np.array(expected_values) < bins[i+1])
        if i == len(bins)-2:  # Last bin includes the maximum
            mask = (np.array(expected_values) >= bins[i]) & (np.array(expected_values) <= bins[i+1])
        
        original_binned.append(np.mean([abs(e) for e, m in zip(original_errors, mask) if m]))
        fixed_binned.append(np.mean([abs(e) for e, m in zip(fixed_errors, mask) if m]))
    
    x = np.arange(len(bin_labels))
    width = 0.35
    
    ax4.bar(x - width/2, original_binned, width, label='Original', alpha=0.8, color='red')
    ax4.bar(x + width/2, fixed_binned, width, label='Bias-Fixed', alpha=0.8, color='blue')
    ax4.set_xlabel('Expected Value Percentile')
    ax4.set_ylabel('Mean Absolute Error ($)')
    ax4.set_title('Error Improvement by Value Range')
    ax4.set_xticks(x)
    ax4.set_xticklabels(bin_labels)
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.suptitle('Algorithm Bias Reduction: Original vs Fixed Comparison', 
                 fontsize=16, fontweight='bold', y=0.98)
    
    plt.savefig('bias_reduction_comparison.png', dpi=300, bbox_inches='tight')
    print("📈 Comparison visualization saved as 'bias_reduction_comparison.png'")
    
    # Print summary statistics
    print(f"\n{'='*60}")
    print(f"ALGORITHM COMPARISON SUMMARY")
    print(f"{'='*60}")
    
    print(f"\n📊 BIAS REDUCTION:")
    print(f"   Original Mean Error: ${np.mean(original_errors):.2f}")
    print(f"   Fixed Mean Error: ${np.mean(fixed_errors):.2f}")
    print(f"   Improvement: ${np.mean(original_errors) - np.mean(fixed_errors):.2f}")
    
    print(f"\n📈 ACCURACY IMPROVEMENT:")
    print(f"   Original MAE: ${np.mean(original_abs_errors):.2f}")
    print(f"   Fixed MAE: ${np.mean(fixed_abs_errors):.2f}")
    print(f"   Improvement: ${np.mean(original_abs_errors) - np.mean(fixed_abs_errors):.2f}")
    
    # Accuracy ranges
    original_within_50 = sum(1 for e in original_abs_errors if e <= 50)
    fixed_within_50 = sum(1 for e in fixed_abs_errors if e <= 50)
    
    original_within_100 = sum(1 for e in original_abs_errors if e <= 100)
    fixed_within_100 = sum(1 for e in fixed_abs_errors if e <= 100)
    
    print(f"\n🎯 PREDICTION ACCURACY:")
    print(f"   Within ±$50:")
    print(f"     Original: {original_within_50} ({original_within_50/len(test_cases)*100:.1f}%)")
    print(f"     Fixed: {fixed_within_50} ({fixed_within_50/len(test_cases)*100:.1f}%)")
    print(f"   Within ±$100:")
    print(f"     Original: {original_within_100} ({original_within_100/len(test_cases)*100:.1f}%)")
    print(f"     Fixed: {fixed_within_100} ({fixed_within_100/len(test_cases)*100:.1f}%)")
    
    return {
        'bias_improvement': np.mean(original_errors) - np.mean(fixed_errors),
        'mae_improvement': np.mean(original_abs_errors) - np.mean(fixed_abs_errors),
        'accuracy_50_improvement': fixed_within_50 - original_within_50,
        'accuracy_100_improvement': fixed_within_100 - original_within_100
    }

if __name__ == '__main__':
    improvements = compare_algorithms()
    
    print(f"\n✅ BIAS REDUCTION SUCCESS!")
    print(f"   🎯 Bias eliminated: ${improvements['bias_improvement']:.2f}")
    print(f"   📈 MAE improved: ${improvements['mae_improvement']:.2f}")
    print(f"   🏆 More accurate predictions: +{improvements['accuracy_50_improvement']} within ±$50")
