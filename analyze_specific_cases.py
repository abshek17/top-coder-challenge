#!/usr/bin/env python3
"""
Analyze Specific High-Error Cases from Latest Evaluation
"""

import json
from legacy_calculate import calculate_legacy_reimbursement

def analyze_specific_cases():
    """Analyze the specific high-error cases mentioned"""
    
    with open('public_cases.json', 'r') as f:
        test_cases = json.load(f)
    
    # Cases from latest evaluation with high errors
    target_cases = [152, 367, 711, 84, 797]
    
    print("🔍 ANALYZING SPECIFIC HIGH-ERROR CASES")
    print("=" * 60)
    
    case_patterns = []
    
    for case_id in target_cases:
        if case_id < len(test_cases):
            case = test_cases[case_id]
            
            trip_duration = case['input']['trip_duration_days']
            miles = case['input']['miles_traveled']
            receipts = case['input']['total_receipts_amount']
            expected = case['expected_output']
            
            predicted = calculate_legacy_reimbursement(trip_duration, miles, receipts)
            error = abs(predicted - expected)
            
            receipts_per_day = receipts / trip_duration if trip_duration > 0 else 0
            
            # Categorize receipt level
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
            
            pattern = f"{trip_duration}d_{receipt_cat}"
            over_under = "OVER" if predicted > expected else "UNDER"
            
            print(f"\nCase {case_id}: {pattern}")
            print(f"  Trip: {trip_duration} days, {miles} miles")
            print(f"  Receipts: ${receipts:.2f} (${receipts_per_day:.0f}/day)")
            print(f"  Expected: ${expected:.2f}")
            print(f"  Predicted: ${predicted:.2f}")
            print(f"  Error: ${error:.2f} ({over_under}-prediction)")
            
            case_patterns.append({
                'case_id': case_id,
                'pattern': pattern,
                'duration': trip_duration,
                'receipts_per_day': receipts_per_day,
                'error': error,
                'over_under': over_under,
                'predicted': predicted,
                'expected': expected
            })
    
    return case_patterns

def find_similar_patterns(target_cases):
    """Find other cases with similar patterns"""
    
    with open('public_cases.json', 'r') as f:
        test_cases = json.load(f)
    
    print(f"\n🔎 FINDING SIMILAR PATTERN CASES")
    print("=" * 60)
    
    # Group similar patterns
    pattern_groups = {}
    
    for target in target_cases:
        pattern = target['pattern']
        if pattern not in pattern_groups:
            pattern_groups[pattern] = []
    
    # Find all cases matching these patterns
    for i, case in enumerate(test_cases):
        trip_duration = case['input']['trip_duration_days']
        receipts = case['input']['total_receipts_amount']
        expected = case['expected_output']
        
        predicted = calculate_legacy_reimbursement(trip_duration, case['input']['miles_traveled'], receipts)
        error = abs(predicted - expected)
        
        receipts_per_day = receipts / trip_duration if trip_duration > 0 else 0
        
        # Categorize
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
        
        pattern = f"{trip_duration}d_{receipt_cat}"
        
        if pattern in pattern_groups:
            pattern_groups[pattern].append({
                'case_id': i,
                'receipts_per_day': receipts_per_day,
                'error': error,
                'predicted': predicted,
                'expected': expected,
                'over_under': "OVER" if predicted > expected else "UNDER"
            })
    
    # Analyze each pattern group
    for pattern, cases in pattern_groups.items():
        if cases:
            cases.sort(key=lambda x: x['error'], reverse=True)
            avg_error = sum(c['error'] for c in cases) / len(cases)
            over_count = sum(1 for c in cases if c['over_under'] == 'OVER')
            high_errors = sum(1 for c in cases if c['error'] >= 500)
            
            print(f"\n📊 {pattern}:")
            print(f"  Total cases: {len(cases)}")
            print(f"  Average error: ${avg_error:.0f}")
            print(f"  Over-predictions: {over_count}/{len(cases)} ({over_count/len(cases)*100:.0f}%)")
            print(f"  High errors (≥$500): {high_errors}/{len(cases)} ({high_errors/len(cases)*100:.0f}%)")
            
            print(f"  Top error cases:")
            for case in cases[:5]:
                print(f"    Case {case['case_id']}: ${case['predicted']:.0f} vs ${case['expected']:.0f} "
                      f"(error: ${case['error']:.0f}, {case['over_under']})")

def suggest_targeted_fixes(case_patterns):
    """Suggest specific fixes for these patterns"""
    
    print(f"\n🛠️ TARGETED FIX SUGGESTIONS")
    print("=" * 60)
    
    pattern_analysis = {}
    
    for case in case_patterns:
        pattern = case['pattern']
        if pattern not in pattern_analysis:
            pattern_analysis[pattern] = {
                'cases': [],
                'over_count': 0,
                'under_count': 0,
                'total_error': 0
            }
        
        pattern_analysis[pattern]['cases'].append(case)
        pattern_analysis[pattern]['total_error'] += case['error']
        
        if case['over_under'] == 'OVER':
            pattern_analysis[pattern]['over_count'] += 1
        else:
            pattern_analysis[pattern]['under_count'] += 1
    
    for pattern, data in pattern_analysis.items():
        avg_error = data['total_error'] / len(data['cases'])
        over_pct = data['over_count'] / len(data['cases']) * 100
        
        print(f"\n🔧 {pattern}:")
        print(f"  Cases in evaluation: {len(data['cases'])}")
        print(f"  Average error: ${avg_error:.0f}")
        print(f"  Over-prediction rate: {over_pct:.0f}%")
        
        # Suggest specific fixes
        duration = int(pattern.split('d_')[0])
        receipt_level = pattern.split('d_')[1]
        
        if over_pct > 70:  # Systematic over-prediction
            if receipt_level == "extreme":
                print(f"  💡 RECOMMENDATION: Add penalty for {duration}-day extreme receipt trips")
                print(f"     Suggested: Add 0.75-0.85x multiplier to reduce over-prediction")
            elif receipt_level == "very_high":
                print(f"  💡 RECOMMENDATION: Add penalty for {duration}-day very high receipt trips")
                print(f"     Suggested: Add 0.8-0.9x multiplier to reduce over-prediction")
        elif over_pct < 30:  # Systematic under-prediction
            if receipt_level == "extreme":
                print(f"  💡 RECOMMENDATION: Add bonus for {duration}-day extreme receipt trips")
                print(f"     Suggested: Add 1.1-1.2x multiplier to increase reimbursement")
            elif receipt_level == "high":
                print(f"  💡 RECOMMENDATION: Add bonus for {duration}-day high receipt trips")
                print(f"     Suggested: Add 1.05-1.15x multiplier to increase reimbursement")

if __name__ == "__main__":
    # Analyze the specific cases
    target_cases = analyze_specific_cases()
    
    # Find similar pattern cases
    find_similar_patterns(target_cases)
    
    # Suggest targeted fixes
    suggest_targeted_fixes(target_cases)
