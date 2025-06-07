#!/usr/bin/env python3
"""
Comprehensive Pattern Validation
Validates that systematic fixes are working and identifies remaining patterns to fix
"""

import json
import math
from collections import defaultdict
from legacy_calculate import calculate_legacy_reimbursement

def load_test_cases():
    """Load test cases from public_cases.json"""
    with open('public_cases.json', 'r') as f:
        return json.load(f)

def categorize_receipts(receipts_per_day):
    """Categorize receipt spending levels"""
    if receipts_per_day < 100:
        return "low"
    elif receipts_per_day < 200:
        return "medium"
    elif receipts_per_day < 300:
        return "high"
    elif receipts_per_day < 400:
        return "very_high"
    elif receipts_per_day < 500:
        return "extreme"
    else:
        return "ultra"

def analyze_systematic_patterns():
    """Analyze all cases to identify systematic patterns that need fixing"""
    test_cases = load_test_cases()
    
    # Collect all predictions and organize by patterns
    pattern_data = defaultdict(lambda: {
        'cases': [],
        'over': 0,
        'under': 0,
        'total_error': 0,
        'high_errors': 0
    })
    
    all_errors = []
    
    print("🔍 SYSTEMATIC PATTERN VALIDATION")
    print("=" * 60)
    print("Analyzing all 1000 test cases for systematic patterns...")
    
    for i, case in enumerate(test_cases):
        trip_duration = case['input']['trip_duration_days']
        miles = case['input']['miles_traveled']
        receipts = case['input']['total_receipts_amount']
        expected = case['expected_output']
        
        predicted = calculate_legacy_reimbursement(trip_duration, miles, receipts)
        error = abs(predicted - expected)
        
        receipts_per_day = receipts / trip_duration if trip_duration > 0 else 0
        receipt_cat = categorize_receipts(receipts_per_day)
        
        # Create pattern key
        pattern_key = f"{trip_duration}d_{receipt_cat}"
        
        # Store case data
        case_data = {
            'case_id': i,
            'trip_duration': trip_duration,
            'miles': miles,
            'receipts': receipts,
            'receipts_per_day': receipts_per_day,
            'expected': expected,
            'predicted': predicted,
            'error': error,
            'over_under': 'over' if predicted > expected else 'under'
        }
        
        all_errors.append(case_data)
        pattern_data[pattern_key]['cases'].append(case_data)
        pattern_data[pattern_key]['total_error'] += error
        
        if case_data['over_under'] == 'over':
            pattern_data[pattern_key]['over'] += 1
        else:
            pattern_data[pattern_key]['under'] += 1
            
        if error >= 500:
            pattern_data[pattern_key]['high_errors'] += 1
    
    return all_errors, pattern_data

def print_overall_metrics(all_errors):
    """Print overall performance metrics"""
    avg_error = sum(e['error'] for e in all_errors) / len(all_errors)
    high_error_count = sum(1 for e in all_errors if e['error'] >= 500)
    over_predictions = sum(1 for e in all_errors if e['over_under'] == 'over')
    under_predictions = sum(1 for e in all_errors if e['over_under'] == 'under')
    
    print(f"\n📈 CURRENT OVERALL PERFORMANCE:")
    print(f"  Average error: ${avg_error:.2f}")
    print(f"  High error cases (≥$500): {high_error_count}/{len(all_errors)} ({high_error_count/len(all_errors)*100:.1f}%)")
    print(f"  Over-predictions: {over_predictions} ({over_predictions/len(all_errors)*100:.1f}%)")
    print(f"  Under-predictions: {under_predictions} ({under_predictions/len(all_errors)*100:.1f}%)")
    
    return avg_error, high_error_count

def identify_problematic_patterns(pattern_data):
    """Identify patterns that still need systematic fixes"""
    print(f"\n🎯 SYSTEMATIC PATTERN ANALYSIS:")
    print("=" * 60)
    
    problematic_patterns = []
    
    for pattern_key, data in sorted(pattern_data.items()):
        if len(data['cases']) < 3:  # Skip patterns with too few cases
            continue
            
        avg_error = data['total_error'] / len(data['cases'])
        over_pct = data['over'] / len(data['cases']) * 100
        under_pct = data['under'] / len(data['cases']) * 100
        high_error_pct = data['high_errors'] / len(data['cases']) * 100
        
        # Identify problematic patterns
        is_problematic = False
        issues = []
        
        if avg_error > 300:
            is_problematic = True
            issues.append(f"high avg error (${avg_error:.0f})")
            
        if high_error_pct > 30:
            is_problematic = True
            issues.append(f"high error rate ({high_error_pct:.0f}%)")
            
        if over_pct > 80:
            is_problematic = True
            issues.append(f"systematic over-prediction ({over_pct:.0f}%)")
            
        if under_pct > 80:
            is_problematic = True
            issues.append(f"systematic under-prediction ({under_pct:.0f}%)")
        
        # Print pattern summary
        status = "⚠️ NEEDS FIX" if is_problematic else "✅"
        print(f"{status} {pattern_key:12} | {len(data['cases']):2d} cases | "
              f"Avg error: ${avg_error:3.0f} | "
              f"Over: {over_pct:2.0f}% | "
              f"High errors: {data['high_errors']:2d} ({high_error_pct:2.0f}%)")
        
        if is_problematic:
            problematic_patterns.append({
                'pattern': pattern_key,
                'data': data,
                'avg_error': avg_error,
                'issues': issues,
                'bias': 'over' if over_pct > under_pct else 'under'
            })
    
    return problematic_patterns

def analyze_specific_high_error_cases(all_errors, limit=10):
    """Analyze specific high-error cases for patterns"""
    high_errors = [e for e in all_errors if e['error'] >= 500]
    high_errors.sort(key=lambda x: x['error'], reverse=True)
    
    print(f"\n🔍 TOP {limit} HIGH-ERROR CASES:")
    print("=" * 60)
    
    for i, case in enumerate(high_errors[:limit]):
        receipt_cat = categorize_receipts(case['receipts_per_day'])
        pattern_key = f"{case['trip_duration']}d_{receipt_cat}"
        
        print(f"Case {case['case_id']:3d}: {pattern_key:12} | "
              f"${case['receipts_per_day']:3.0f}/day | "
              f"${case['expected']:4.0f} vs ${case['predicted']:4.0f} | "
              f"Error: ${case['error']:3.0f} ({case['over_under']})")

def provide_fix_recommendations(problematic_patterns):
    """Provide specific recommendations for fixing problematic patterns"""
    print(f"\n💡 SPECIFIC FIX RECOMMENDATIONS:")
    print("=" * 60)
    
    if not problematic_patterns:
        print("✅ No major systematic patterns identified that need immediate fixes!")
        return
    
    for pattern_info in problematic_patterns:
        pattern = pattern_info['pattern']
        data = pattern_info['data']
        avg_error = pattern_info['avg_error']
        bias = pattern_info['bias']
        
        print(f"\n🔧 {pattern}:")
        print(f"   Cases: {len(data['cases'])}")
        print(f"   Avg error: ${avg_error:.0f}")
        print(f"   Bias: {bias}-prediction")
        
        # Analyze specific cases for this pattern
        cases = data['cases']
        cases.sort(key=lambda x: x['error'], reverse=True)
        
        # Show worst cases
        print(f"   Worst cases:")
        for case in cases[:3]:
            print(f"     Case {case['case_id']}: ${case['expected']:.0f} vs ${case['predicted']:.0f} (${case['error']:.0f} {case['over_under']})")
        
        # Provide specific recommendation
        duration = int(pattern.split('d_')[0])
        receipt_level = pattern.split('d_')[1]
        
        if bias == 'under' and avg_error > 300:
            if duration >= 10:
                print(f"   💡 RECOMMENDATION: Increase bonus multiplier for {duration}-day {receipt_level} receipt trips")
                if receipt_level == 'medium':
                    print(f"      Suggested: Increase bonus from current to 1.2-1.3x")
                elif receipt_level == 'high':
                    print(f"      Suggested: Add positive adjustment of 1.1-1.15x")
            elif duration == 6 and receipt_level == 'high':
                print(f"   💡 RECOMMENDATION: Replace penalty with bonus for 6-day high-receipt trips")
                print(f"      Suggested: Change from 0.9x penalty to 1.05x bonus")
        elif bias == 'over' and avg_error > 300:
            print(f"   💡 RECOMMENDATION: Increase penalty for {duration}-day {receipt_level} receipt trips")

def main():
    # Run comprehensive analysis
    all_errors, pattern_data = analyze_systematic_patterns()
    
    # Print overall metrics
    avg_error, high_error_count = print_overall_metrics(all_errors)
    
    # Identify and analyze problematic patterns
    problematic_patterns = identify_problematic_patterns(pattern_data)
    
    # Show specific high-error cases
    analyze_specific_high_error_cases(all_errors)
    
    # Provide fix recommendations
    provide_fix_recommendations(problematic_patterns)
    
    print(f"\n📊 SUMMARY:")
    print(f"   Current average error: ${avg_error:.2f}")
    print(f"   High-error cases: {high_error_count}/1000")
    print(f"   Patterns needing fixes: {len(problematic_patterns)}")
    
    if problematic_patterns:
        print(f"\n🎯 PRIORITY FIXES:")
        for pattern_info in sorted(problematic_patterns, key=lambda x: x['avg_error'], reverse=True)[:3]:
            print(f"   1. {pattern_info['pattern']} (${pattern_info['avg_error']:.0f} avg error)")
    
    print(f"\n✅ Validation complete!")

if __name__ == "__main__":
    main()
