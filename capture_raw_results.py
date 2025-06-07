#!/usr/bin/env python3
"""
Capture raw results from legacy_evaluate function for all 1000 cases.
Saves expected vs actual values to results.json for detailed analysis.
"""

import json
from legacy_calculate import calculate_legacy_reimbursement

def capture_raw_results():
    """
    Load all test cases and capture raw evaluation results.
    Returns a list of dictionaries with case details and predictions.
    """
    print("Loading test cases...")
    
    # Load the test cases
    with open('public_cases.json', 'r') as f:
        test_cases = json.load(f)
    
    print(f"Processing {len(test_cases)} test cases...")
    
    raw_results = []
    
    for i, case in enumerate(test_cases):
        # Extract case parameters
        trip_duration = case['input']['trip_duration_days']
        miles_traveled = case['input']['miles_traveled']
        receipts_amount = case['input']['total_receipts_amount']
        expected_output = case['expected_output']
        
        # Calculate actual output using legacy algorithm
        actual_output = calculate_legacy_reimbursement(
            trip_duration, 
            miles_traveled, 
            receipts_amount
        )
        
        # Calculate error metrics
        error = actual_output - expected_output
        absolute_error = abs(error)
        percentage_error = (error / expected_output * 100) if expected_output != 0 else 0
        
        # Calculate derived metrics for analysis
        miles_per_day = miles_traveled / trip_duration if trip_duration > 0 else 0
        receipts_per_day = receipts_amount / trip_duration if trip_duration > 0 else 0
        
        # Store comprehensive result
        result = {
            'case_id': i + 1,
            'trip_duration_days': trip_duration,
            'miles_traveled': miles_traveled,
            'total_receipts_amount': receipts_amount,
            'expected_output': expected_output,
            'actual_output': round(actual_output, 2),
            'error': round(error, 2),
            'absolute_error': round(absolute_error, 2),
            'percentage_error': round(percentage_error, 2),
            'miles_per_day': round(miles_per_day, 2),
            'receipts_per_day': round(receipts_per_day, 2),
            'under_predicted': error < 0,
            'over_predicted': error > 0
        }
        
        raw_results.append(result)
        
        # Progress indicator
        if (i + 1) % 100 == 0:
            print(f"Processed {i + 1} cases...")
    
    return raw_results

def save_results_to_json(results, filename='results.json'):
    """
    Save raw results to JSON file with proper formatting.
    """
    print(f"Saving results to {filename}...")
    
    # Create summary statistics
    total_cases = len(results)
    under_predicted_cases = sum(1 for r in results if r['under_predicted'])
    over_predicted_cases = sum(1 for r in results if r['over_predicted'])
    mean_absolute_error = sum(r['absolute_error'] for r in results) / total_cases
    total_error = sum(r['error'] for r in results)
    
    # Calculate correlation coefficient
    expected_values = [r['expected_output'] for r in results]
    actual_values = [r['actual_output'] for r in results]
    
    # Simple correlation calculation
    n = len(expected_values)
    sum_expected = sum(expected_values)
    sum_actual = sum(actual_values)
    sum_exp_sq = sum(x**2 for x in expected_values)
    sum_act_sq = sum(x**2 for x in actual_values)
    sum_exp_act = sum(expected_values[i] * actual_values[i] for i in range(n))
    
    correlation = ((n * sum_exp_act - sum_expected * sum_actual) / 
                  ((n * sum_exp_sq - sum_expected**2) * (n * sum_act_sq - sum_actual**2))**0.5)
    
    # Prepare output data
    output_data = {
        'metadata': {
            'total_cases': total_cases,
            'algorithm_version': 'legacy_calculate_v2_targeted_fixes',
            'generation_timestamp': '2025-06-07',
            'description': 'Raw evaluation results for all 1000 test cases'
        },
        'summary_statistics': {
            'mean_absolute_error': round(mean_absolute_error, 2),
            'total_error': round(total_error, 2),
            'correlation_coefficient': round(correlation, 4),
            'under_predicted_cases': under_predicted_cases,
            'over_predicted_cases': over_predicted_cases,
            'under_prediction_rate': round(under_predicted_cases / total_cases * 100, 1),
            'over_prediction_rate': round(over_predicted_cases / total_cases * 100, 1)
        },
        'raw_results': results
    }
    
    # Save to JSON file
    with open(filename, 'w') as f:
        json.dump(output_data, f, indent=2)
    
    print(f"Results saved to {filename}")
    print(f"Summary:")
    print(f"  Total cases: {total_cases}")
    print(f"  Mean absolute error: ${mean_absolute_error:.2f}")
    print(f"  Correlation: {correlation:.4f}")
    print(f"  Under-predicted: {under_predicted_cases} ({under_predicted_cases/total_cases*100:.1f}%)")
    print(f"  Over-predicted: {over_predicted_cases} ({over_predicted_cases/total_cases*100:.1f}%)")

def main():
    """
    Main execution function to capture and save raw results.
    """
    print("=== Capturing Raw Legacy Evaluation Results ===")
    
    # Capture raw results
    results = capture_raw_results()
    
    # Save to JSON
    save_results_to_json(results, 'results.json')
    
    print("\n=== Raw Results Capture Complete ===")
    print("Results saved to results.json")
    print("File contains:")
    print("- Metadata and summary statistics")
    print("- All 1000 cases with expected vs actual values")
    print("- Error metrics and derived features")
    print("- Ready for detailed analysis and pattern detection")

if __name__ == '__main__':
    main()
