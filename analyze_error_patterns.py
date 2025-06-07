#!/usr/bin/env python3
"""
Comprehensive Error Pattern Analysis
Analyzes high-error cases to identify systematic patterns before making changes
"""

import json
import math
from collections import defaultdict
from legacy_calculate import calculate_legacy_reimbursement

def load_test_cases():
    """Load test cases from public_cases.json"""
    with open('public_cases.json', 'r') as f:
        return json.load(f)

def analyze_errors():
    """Run predictions and analyze error patterns"""
    test_cases = load_test_cases()
    
    errors = []
    
    print("🔍 Running predictions and collecting error data...")
    
    for i, case in enumerate(test_cases):
        trip_duration = case['input']['trip_duration_days']
        miles = case['input']['miles_traveled']
        receipts = case['input']['total_receipts_amount']
        expected = case['expected_output']
        
        predicted = calculate_legacy_reimbursement(trip_duration, miles, receipts)
        error = abs(predicted - expected)
        
        receipts_per_day = receipts / trip_duration if trip_duration > 0 else 0
        miles_per_day = miles / trip_duration if trip_duration > 0 else 0
        
        errors.append({
            'case_id': i,
            'trip_duration': trip_duration,
            'miles_traveled': miles,
            'total_receipts': receipts,
            'receipts_per_day': receipts_per_day,
            'miles_per_day': miles_per_day,
            'expected': expected,
            'predicted': predicted,
            'error': error,
            'over_under': 'over' if predicted > expected else 'under'
        })
    
    return errors

def analyze_high_error_patterns(errors, threshold=500):
    """Analyze patterns in high-error cases"""
    
    high_errors = [e for e in errors if e['error'] >= threshold]
    print(f"\n📊 HIGH ERROR ANALYSIS (≥${threshold})")
    print(f"High error cases: {len(high_errors)}/{len(errors)} ({len(high_errors)/len(errors)*100:.1f}%)")
    
    # Group by trip duration
    duration_groups = defaultdict(list)
    for error in high_errors:
        duration_groups[error['trip_duration']].append(error)
    
    print(f"\n🗓️ HIGH ERRORS BY TRIP DURATION:")
    for duration in sorted(duration_groups.keys()):
        cases = duration_groups[duration]
        avg_error = sum(c['error'] for c in cases) / len(cases)
        over_count = sum(1 for c in cases if c['over_under'] == 'over')
        under_count = len(cases) - over_count
        
        print(f"  {duration}d trips: {len(cases)} cases, avg error: ${avg_error:.0f}")
        print(f"    Over-predictions: {over_count}, Under-predictions: {under_count}")
        
        # Show top 3 worst for this duration
        worst_cases = sorted(cases, key=lambda x: x['error'], reverse=True)[:3]
        for case in worst_cases:
            print(f"    Case {case['case_id']}: {case['receipts_per_day']:.0f}/day receipts, "
                  f"${case['predicted']:.0f} vs ${case['expected']:.0f}, {case['over_under']}")
    
    return duration_groups

def analyze_receipt_patterns(errors, threshold=500):
    """Analyze receipt spending patterns in high-error cases"""
    
    high_errors = [e for e in errors if e['error'] >= threshold]
    
    print(f"\n💰 RECEIPT SPENDING PATTERNS IN HIGH ERRORS:")
    
    # Group by receipts per day ranges
    receipt_ranges = [
        (0, 100, "Low ($0-100/day)"),
        (100, 200, "Medium ($100-200/day)"),
        (200, 300, "High ($200-300/day)"),
        (300, 400, "Very High ($300-400/day)"),
        (400, 500, "Extreme ($400-500/day)"),
        (500, float('inf'), "Ultra ($500+/day)")
    ]
    
    for min_range, max_range, label in receipt_ranges:
        range_cases = [e for e in high_errors if min_range <= e['receipts_per_day'] < max_range]
        if range_cases:
            avg_error = sum(c['error'] for c in range_cases) / len(range_cases)
            over_count = sum(1 for c in range_cases if c['over_under'] == 'over')
            under_count = len(range_cases) - over_count
            
            print(f"  {label}: {len(range_cases)} cases, avg error: ${avg_error:.0f}")
            print(f"    Over: {over_count}, Under: {under_count}")
            
            # Group by trip duration within this range
            duration_breakdown = defaultdict(int)
            for case in range_cases:
                duration_breakdown[case['trip_duration']] += 1
            
            duration_str = ", ".join([f"{d}d: {count}" for d, count in sorted(duration_breakdown.items())])
            print(f"    Trip durations: {duration_str}")

def analyze_specific_problem_cases(errors):
    """Analyze the specific cases mentioned in the evaluation"""
    
    problem_cases = [797, 976, 916, 284, 619]  # From the evaluation output
    
    print(f"\n🎯 ANALYSIS OF SPECIFIC PROBLEM CASES:")
    
    for case_id in problem_cases:
        if case_id < len(errors):
            case = errors[case_id]
            print(f"\nCase {case_id}:")
            print(f"  {case['trip_duration']}d, {case['miles_traveled']}mi, ${case['total_receipts']:.2f} (${case['receipts_per_day']:.0f}/day)")
            print(f"  Expected: ${case['expected']:.2f}, Predicted: ${case['predicted']:.2f}")
            print(f"  Error: ${case['error']:.2f} ({case['over_under']}-prediction)")
            
            # Find similar cases
            similar_cases = find_similar_cases(errors, case)
            if similar_cases:
                print(f"  Similar cases found: {len(similar_cases)}")
                avg_error = sum(c['error'] for c in similar_cases) / len(similar_cases)
                over_count = sum(1 for c in similar_cases if c['over_under'] == 'over')
                print(f"    Average error: ${avg_error:.0f}, Over-predictions: {over_count}/{len(similar_cases)}")

def find_similar_cases(errors, target_case, duration_tolerance=0, receipt_tolerance=50):
    """Find cases similar to the target case"""
    
    similar = []
    target_receipts_per_day = target_case['receipts_per_day']
    target_duration = target_case['trip_duration']
    
    for case in errors:
        if (abs(case['trip_duration'] - target_duration) <= duration_tolerance and
            abs(case['receipts_per_day'] - target_receipts_per_day) <= receipt_tolerance and
            case['case_id'] != target_case['case_id']):
            similar.append(case)
    
    return similar

def analyze_systematic_issues(errors, threshold=500):
    """Identify systematic over/under-prediction patterns"""
    
    high_errors = [e for e in errors if e['error'] >= threshold]
    
    print(f"\n⚠️ SYSTEMATIC PATTERN ANALYSIS:")
    
    # 1. Duration + Receipt Range Combinations
    combinations = defaultdict(lambda: {'cases': [], 'over': 0, 'under': 0})
    
    for case in high_errors:
        duration = case['trip_duration']
        
        # Categorize receipt spending
        receipts_per_day = case['receipts_per_day']
        if receipts_per_day < 100:
            receipt_cat = "low"
        elif receipts_per_day < 200:
            receipt_cat = "medium"
        elif receipts_per_day < 300:
            receipt_cat = "high"
        elif receipts_per_day < 400:
            receipt_cat = "very_high"
        else:
            receipt_cat = "extreme"
        
        key = f"{duration}d_{receipt_cat}"
        combinations[key]['cases'].append(case)
        if case['over_under'] == 'over':
            combinations[key]['over'] += 1
        else:
            combinations[key]['under'] += 1
    
    # Show systematic issues
    print("  Systematic over/under-prediction patterns:")
    for key, data in sorted(combinations.items()):
        if len(data['cases']) >= 3:  # Only show patterns with multiple cases
            avg_error = sum(c['error'] for c in data['cases']) / len(data['cases'])
            over_pct = data['over'] / len(data['cases']) * 100
            
            if over_pct > 80 or over_pct < 20:  # Strong bias one way
                bias = "OVER" if over_pct > 50 else "UNDER"
                print(f"    {key}: {len(data['cases'])} cases, {bias}-predicting {abs(over_pct-50):.0f}% of time, avg error: ${avg_error:.0f}")

def main():
    print("🔍 COMPREHENSIVE ERROR PATTERN ANALYSIS")
    print("=" * 50)
    
    # Run analysis
    errors = analyze_errors()
    
    # Calculate basic stats
    avg_error = sum(e['error'] for e in errors) / len(errors)
    high_error_count = sum(1 for e in errors if e['error'] >= 500)
    
    print(f"\n📈 OVERALL PERFORMANCE:")
    print(f"  Average error: ${avg_error:.2f}")
    print(f"  High error cases (≥$500): {high_error_count}/{len(errors)} ({high_error_count/len(errors)*100:.1f}%)")
    
    # Detailed pattern analysis
    duration_groups = analyze_high_error_patterns(errors)
    analyze_receipt_patterns(errors)
    analyze_specific_problem_cases(errors)
    analyze_systematic_issues(errors)
    
    print(f"\n✅ Analysis complete! Use these patterns to make targeted improvements.")

if __name__ == "__main__":
    main()
