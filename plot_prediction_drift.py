#!/usr/bin/env python3
"""
Plot legacy_calculate.py predictions vs expected results to identify drift patterns.
"""

import json
import matplotlib.pyplot as plt
import numpy as np
import sys
import os

# Add current directory to path for import
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from legacy_calculate import calculate_legacy_reimbursement
except ImportError as e:
    print(f"Could not import calculate_legacy_reimbursement: {e}")
    sys.exit(1)

def load_test_cases():
    """Load test cases from public_cases.json"""
    with open('public_cases.json', 'r') as f:
        cases = json.load(f)
    return cases

def calculate_predictions(cases):
    """Calculate predictions for all test cases"""
    predictions = []
    expected = []
    errors = []
    
    for i, case in enumerate(cases):
        try:
            # Handle nested input structure
            input_data = case.get('input', case)  # Support both nested and flat structures
            
            pred = calculate_legacy_reimbursement(
                input_data['trip_duration_days'],
                input_data['miles_traveled'], 
                input_data['total_receipts_amount']
            )
            exp = case['expected_output']
            error = pred - exp
            
            predictions.append(pred)
            expected.append(exp)
            errors.append(error)
            
        except Exception as e:
            print(f"Error processing case {i}: {e}")
            print(f"Case data: {case}")
            predictions.append(0)
            expected.append(case['expected_output'])
            errors.append(-case['expected_output'])
    
    return predictions, expected, errors

def create_drift_plots(cases, predictions, expected, errors):
    """Create comprehensive drift analysis plots"""
    
    # Create figure with subplots
    fig = plt.figure(figsize=(20, 15))
    
    # 1. Scatter plot: Predicted vs Expected
    ax1 = plt.subplot(2, 3, 1)
    plt.scatter(expected, predictions, alpha=0.6, s=30)
    
    # Perfect prediction line
    min_val = min(min(expected), min(predictions))
    max_val = max(max(expected), max(predictions))
    plt.plot([min_val, max_val], [min_val, max_val], 'r--', alpha=0.8, label='Perfect Prediction')
    
    plt.xlabel('Expected Reimbursement ($)')
    plt.ylabel('Predicted Reimbursement ($)')
    plt.title('Predicted vs Expected Reimbursements')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # Add correlation coefficient
    correlation = np.corrcoef(expected, predictions)[0, 1]
    plt.text(0.05, 0.95, f'Correlation: {correlation:.3f}', 
             transform=ax1.transAxes, bbox=dict(boxstyle="round", facecolor='wheat'))
    
    # 2. Error distribution histogram
    ax2 = plt.subplot(2, 3, 2)
    plt.hist(errors, bins=30, alpha=0.7, edgecolor='black')
    plt.xlabel('Prediction Error ($)')
    plt.ylabel('Frequency')
    plt.title('Distribution of Prediction Errors')
    plt.axvline(x=0, color='red', linestyle='--', alpha=0.8, label='Perfect Prediction')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # Add statistics
    mean_error = np.mean(errors)
    std_error = np.std(errors)
    plt.text(0.05, 0.95, f'Mean Error: ${mean_error:.2f}\nStd Dev: ${std_error:.2f}', 
             transform=ax2.transAxes, bbox=dict(boxstyle="round", facecolor='wheat'))
    
    # 3. Error vs Trip Duration
    ax3 = plt.subplot(2, 3, 3)
    trip_durations = [case.get('input', case)['trip_duration_days'] for case in cases]
    plt.scatter(trip_durations, errors, alpha=0.6, s=30)
    plt.xlabel('Trip Duration (days)')
    plt.ylabel('Prediction Error ($)')
    plt.title('Prediction Error vs Trip Duration')
    plt.axhline(y=0, color='red', linestyle='--', alpha=0.8)
    plt.grid(True, alpha=0.3)
    
    # 4. Error vs Miles Traveled
    ax4 = plt.subplot(2, 3, 4)
    miles = [case.get('input', case)['miles_traveled'] for case in cases]
    plt.scatter(miles, errors, alpha=0.6, s=30)
    plt.xlabel('Miles Traveled')
    plt.ylabel('Prediction Error ($)')
    plt.title('Prediction Error vs Miles Traveled')
    plt.axhline(y=0, color='red', linestyle='--', alpha=0.8)
    plt.grid(True, alpha=0.3)
    
    # 5. Error vs Receipt Amount
    ax5 = plt.subplot(2, 3, 5)
    receipts = [case.get('input', case)['total_receipts_amount'] for case in cases]
    plt.scatter(receipts, errors, alpha=0.6, s=30)
    plt.xlabel('Total Receipt Amount ($)')
    plt.ylabel('Prediction Error ($)')
    plt.title('Prediction Error vs Receipt Amount')
    plt.axhline(y=0, color='red', linestyle='--', alpha=0.8)
    plt.grid(True, alpha=0.3)
    
    # 6. Largest errors identification
    ax6 = plt.subplot(2, 3, 6)
    abs_errors = [abs(e) for e in errors]
    case_indices = list(range(len(cases)))
    
    # Color code by error magnitude
    colors = ['red' if abs(e) > 200 else 'orange' if abs(e) > 100 else 'green' for e in errors]
    plt.scatter(case_indices, errors, c=colors, alpha=0.6, s=30)
    plt.xlabel('Case Index')
    plt.ylabel('Prediction Error ($)')
    plt.title('Prediction Errors by Case (Red: >$200, Orange: >$100)')
    plt.axhline(y=0, color='black', linestyle='--', alpha=0.8)
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('prediction_drift_analysis.png', dpi=300, bbox_inches='tight')
    plt.show()

def analyze_worst_cases(cases, predictions, expected, errors, top_n=10):
    """Analyze the worst prediction cases"""
    
    # Create list of (case_index, error, case_data, prediction, expected)
    case_analysis = []
    for i, (case, pred, exp, err) in enumerate(zip(cases, predictions, expected, errors)):
        case_analysis.append({
            'index': i,
            'error': err,
            'abs_error': abs(err),
            'case': case,
            'prediction': pred,
            'expected': exp,
            'error_percent': (err / exp * 100) if exp != 0 else float('inf')
        })
    
    # Sort by absolute error
    worst_cases = sorted(case_analysis, key=lambda x: x['abs_error'], reverse=True)
    
    print("\n" + "="*80)
    print(f"TOP {top_n} WORST PREDICTION CASES")
    print("="*80)
    
    for i, case_info in enumerate(worst_cases[:top_n]):
        case = case_info['case']
        input_data = case.get('input', case)  # Handle nested structure
        print(f"\nCase #{case_info['index']} (Rank {i+1}):")
        print(f"  Trip Duration: {input_data['trip_duration_days']} days")
        print(f"  Miles: {input_data['miles_traveled']}")
        print(f"  Receipts: ${input_data['total_receipts_amount']}")
        print(f"  Expected: ${case_info['expected']}")
        print(f"  Predicted: ${case_info['prediction']}")
        print(f"  Error: ${case_info['error']:.2f} ({case_info['error_percent']:.1f}%)")
        
        # Categorize the error type
        if case_info['error'] > 0:
            print(f"  >> OVER-PREDICTION by ${case_info['error']:.2f}")
        else:
            print(f"  >> UNDER-PREDICTION by ${abs(case_info['error']):.2f}")

def analyze_systematic_patterns(cases, predictions, expected, errors):
    """Analyze systematic drift patterns"""
    
    print("\n" + "="*80)
    print("SYSTEMATIC PATTERN ANALYSIS")
    print("="*80)
    
    # Group by trip duration
    duration_stats = {}
    for case, pred, exp, err in zip(cases, predictions, expected, errors):
        input_data = case.get('input', case)  # Handle nested structure
        duration = input_data['trip_duration_days']
        if duration not in duration_stats:
            duration_stats[duration] = {'errors': [], 'cases': []}
        duration_stats[duration]['errors'].append(err)
        duration_stats[duration]['cases'].append(case)
    
    print("\nERROR PATTERNS BY TRIP DURATION:")
    for duration in sorted(duration_stats.keys()):
        errors_list = duration_stats[duration]['errors']
        mean_error = np.mean(errors_list)
        std_error = np.std(errors_list)
        over_pred = sum(1 for e in errors_list if e > 0)
        under_pred = sum(1 for e in errors_list if e < 0)
        total = len(errors_list)
        
        print(f"  {duration:2d} days: {total:3d} cases, Mean Error: ${mean_error:6.2f}, "
              f"Over: {over_pred:2d} ({over_pred/total*100:4.1f}%), "
              f"Under: {under_pred:2d} ({under_pred/total*100:4.1f}%)")
    
    # Analyze by receipt amount ranges
    receipt_ranges = [
        (0, 100, "Very Low"),
        (100, 300, "Low"), 
        (300, 600, "Medium"),
        (600, 1000, "High"),
        (1000, float('inf'), "Very High")
    ]
    
    print("\nERROR PATTERNS BY RECEIPT AMOUNT:")
    for min_r, max_r, label in receipt_ranges:
        range_errors = []
        for case, err in zip(cases, errors):
            input_data = case.get('input', case)  # Handle nested structure
            if min_r <= input_data['total_receipts_amount'] < max_r:
                range_errors.append(err)
        
        if range_errors:
            mean_error = np.mean(range_errors)
            over_pred = sum(1 for e in range_errors if e > 0)
            under_pred = sum(1 for e in range_errors if e < 0)
            total = len(range_errors)
            
            max_str = "∞" if max_r == float('inf') else f"{max_r:.0f}"
            print(f"  {label:9s} (${min_r:4.0f}-{max_str:>4s}): "
                  f"{total:3d} cases, Mean Error: ${mean_error:6.2f}, "
                  f"Over: {over_pred:2d} ({over_pred/total*100:4.1f}%), "
                  f"Under: {under_pred:2d} ({under_pred/total*100:4.1f}%)")

def main():
    """Main function to run drift analysis"""
    print("Loading test cases...")
    cases = load_test_cases()
    print(f"Loaded {len(cases)} test cases")
    
    print("Calculating predictions...")
    predictions, expected, errors = calculate_predictions(cases)
    
    print("Creating drift analysis plots...")
    create_drift_plots(cases, predictions, expected, errors)
    
    print("Analyzing worst cases...")
    analyze_worst_cases(cases, predictions, expected, errors)
    
    print("Analyzing systematic patterns...")
    analyze_systematic_patterns(cases, predictions, expected, errors)
    
    # Overall statistics
    mean_error = np.mean(errors)
    std_error = np.std(errors)
    mae = np.mean([abs(e) for e in errors])
    rmse = np.sqrt(np.mean([e**2 for e in errors]))
    
    print("\n" + "="*80)
    print("OVERALL PERFORMANCE METRICS")
    print("="*80)
    print(f"Mean Error: ${mean_error:.2f}")
    print(f"Mean Absolute Error: ${mae:.2f}")
    print(f"Root Mean Square Error: ${rmse:.2f}")
    print(f"Standard Deviation: ${std_error:.2f}")
    
    over_predictions = sum(1 for e in errors if e > 0)
    under_predictions = sum(1 for e in errors if e < 0)
    perfect_predictions = sum(1 for e in errors if abs(e) < 1)
    
    print(f"\nPrediction Distribution:")
    print(f"  Over-predictions: {over_predictions} ({over_predictions/len(errors)*100:.1f}%)")
    print(f"  Under-predictions: {under_predictions} ({under_predictions/len(errors)*100:.1f}%)")
    print(f"  Nearly perfect (±$1): {perfect_predictions} ({perfect_predictions/len(errors)*100:.1f}%)")
    
    print(f"\nPlot saved as: prediction_drift_analysis.png")

if __name__ == "__main__":
    main()
