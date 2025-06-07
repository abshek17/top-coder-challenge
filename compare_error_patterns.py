#!/usr/bin/env python3
"""
Compare our current error patterns with Figure_1.png patterns
"""

import json
import matplotlib.pyplot as plt
import numpy as np
from legacy_calculate import calculate_legacy_reimbursement

def load_and_analyze():
    """Load test cases and create error analysis plots"""
    
    with open('public_cases.json', 'r') as f:
        test_cases = json.load(f)
    
    # Collect data for analysis
    trip_durations = []
    receipt_amounts = []
    errors = []
    over_under = []
    
    for i, case in enumerate(test_cases):
        trip_duration = case['input']['trip_duration_days']
        miles = case['input']['miles_traveled']
        receipts = case['input']['total_receipts_amount']
        expected = case['expected_output']
        
        predicted = calculate_legacy_reimbursement(trip_duration, miles, receipts)
        error = predicted - expected  # Positive = over-prediction, Negative = under-prediction
        
        trip_durations.append(trip_duration)
        receipt_amounts.append(receipts)
        errors.append(error)
        over_under.append('over' if error > 0 else 'under')
    
    # Create plots similar to Figure_1 style
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
    
    # Plot 1: Error vs Trip Duration
    ax1.scatter(trip_durations, errors, alpha=0.6, s=20)
    ax1.axhline(y=0, color='red', linestyle='--', alpha=0.7)
    ax1.set_xlabel('Trip Duration (days)')
    ax1.set_ylabel('Error (Predicted - Expected)')
    ax1.set_title('Prediction Error vs Trip Duration')
    ax1.grid(True, alpha=0.3)
    
    # Plot 2: Error vs Receipt Amount  
    ax2.scatter(receipt_amounts, errors, alpha=0.6, s=20)
    ax2.axhline(y=0, color='red', linestyle='--', alpha=0.7)
    ax2.set_xlabel('Receipt Amount ($)')
    ax2.set_ylabel('Error (Predicted - Expected)')
    ax2.set_title('Prediction Error vs Receipt Amount')
    ax2.grid(True, alpha=0.3)
    ax2.set_xlim(0, 3000)  # Focus on reasonable range
    
    # Plot 3: Error distribution by trip duration
    duration_bins = range(1, 16)  # 1-15 days
    error_by_duration = {d: [] for d in duration_bins}
    
    for duration, error in zip(trip_durations, errors):
        if duration in error_by_duration:
            error_by_duration[duration].append(error)
    
    # Box plot for error distribution
    durations_with_data = []
    error_distributions = []
    for duration in duration_bins:
        if error_by_duration[duration]:
            durations_with_data.append(duration)
            error_distributions.append(error_by_duration[duration])
    
    ax3.boxplot(error_distributions, positions=durations_with_data)
    ax3.axhline(y=0, color='red', linestyle='--', alpha=0.7)
    ax3.set_xlabel('Trip Duration (days)')
    ax3.set_ylabel('Error Distribution')
    ax3.set_title('Error Distribution by Trip Duration')
    ax3.grid(True, alpha=0.3)
    
    # Plot 4: High error cases analysis
    high_error_indices = [i for i, e in enumerate(errors) if abs(e) > 500]
    high_error_durations = [trip_durations[i] for i in high_error_indices]
    high_error_receipts = [receipt_amounts[i] for i in high_error_indices]
    high_error_values = [errors[i] for i in high_error_indices]
    
    colors = ['red' if e > 0 else 'blue' for e in high_error_values]
    ax4.scatter(high_error_durations, high_error_receipts, c=colors, s=60, alpha=0.7)
    ax4.set_xlabel('Trip Duration (days)')
    ax4.set_ylabel('Receipt Amount ($)')
    ax4.set_title('High Error Cases (>$500)\nRed=Over-prediction, Blue=Under-prediction')
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('current_error_patterns.png', dpi=150, bbox_inches='tight')
    plt.show()
    
    # Print summary statistics
    print("📊 CURRENT ERROR PATTERN SUMMARY:")
    print(f"Total cases: {len(errors)}")
    print(f"Average error: ${np.mean(np.abs(errors)):.2f}")
    print(f"High error cases (>$500): {len(high_error_indices)} ({len(high_error_indices)/len(errors)*100:.1f}%)")
    
    # Over/under prediction analysis
    over_predictions = sum(1 for e in errors if e > 100)
    under_predictions = sum(1 for e in errors if e < -100)
    print(f"Over-predictions (>$100): {over_predictions}")
    print(f"Under-predictions (<-$100): {under_predictions}")
    
    # Duration-specific analysis
    print(f"\n📈 HIGH ERRORS BY DURATION:")
    duration_high_errors = {}
    for i in high_error_indices:
        duration = trip_durations[i]
        if duration not in duration_high_errors:
            duration_high_errors[duration] = []
        duration_high_errors[duration].append(errors[i])
    
    for duration in sorted(duration_high_errors.keys()):
        error_list = duration_high_errors[duration]
        avg_error = np.mean(np.abs(error_list))
        over_count = sum(1 for e in error_list if e > 0)
        under_count = len(error_list) - over_count
        print(f"  {duration}d: {len(error_list)} cases, avg error: ${avg_error:.0f}, over: {over_count}, under: {under_count}")

if __name__ == "__main__":
    load_and_analyze()
