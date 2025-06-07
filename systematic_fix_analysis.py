#!/usr/bin/env python3
"""
Systematic Fixes Based on Pattern Analysis
"""

from legacy_calculate import calculate_legacy_reimbursement
import json

def test_systematic_fixes():
    """Test the current systematic issues and validate fix directions"""
    
    with open('public_cases.json', 'r') as f:
        test_cases = json.load(f)
    
    # Define problem patterns identified
    problem_patterns = {
        '4d_extreme': [],  # 4-day trips with 400+/day receipts
        '5d_extreme': [],  # 5-day trips with 400+/day receipts  
        '6d_high': [],     # 6-day trips with 200-300/day receipts
        '10d_medium': [],  # 10-day trips with 100-200/day receipts
        '11d_medium': []   # 11-day trips with 100-200/day receipts
    }
    
    # Categorize cases
    for i, case in enumerate(test_cases):
        duration = case['input']['trip_duration_days']
        receipts = case['input']['total_receipts_amount']
        receipts_per_day = receipts / duration
        
        expected = case['expected_output']
        predicted = calculate_legacy_reimbursement(duration, case['input']['miles_traveled'], receipts)
        error = predicted - expected
        
        case_data = {
            'case_id': i,
            'duration': duration,
            'receipts_per_day': receipts_per_day,
            'expected': expected,
            'predicted': predicted,
            'error': error,
            'abs_error': abs(error)
        }
        
        # Categorize into problem patterns
        if duration == 4 and receipts_per_day >= 400:
            problem_patterns['4d_extreme'].append(case_data)
        elif duration == 5 and receipts_per_day >= 400:
            problem_patterns['5d_extreme'].append(case_data)
        elif duration == 6 and 200 <= receipts_per_day < 300:
            problem_patterns['6d_high'].append(case_data)
        elif duration == 10 and 100 <= receipts_per_day < 200:
            problem_patterns['10d_medium'].append(case_data)
        elif duration == 11 and 100 <= receipts_per_day < 200:
            problem_patterns['11d_medium'].append(case_data)
    
    # Analyze each pattern
    print("🔍 SYSTEMATIC PATTERN ANALYSIS:")
    print("=" * 50)
    
    total_high_error_cases = 0
    
    for pattern_name, cases in problem_patterns.items():
        if cases:
            avg_error = sum(c['error'] for c in cases) / len(cases)
            avg_abs_error = sum(c['abs_error'] for c in cases) / len(cases)
            under_predictions = sum(1 for c in cases if c['error'] < 0)
            high_error_cases = sum(1 for c in cases if c['abs_error'] > 500)
            
            total_high_error_cases += high_error_cases
            
            print(f"\n📊 {pattern_name.upper()}:")
            print(f"  Cases: {len(cases)}")
            print(f"  Average error: ${avg_error:.2f} (negative = under-prediction)")
            print(f"  Average absolute error: ${avg_abs_error:.2f}")
            print(f"  Under-predictions: {under_predictions}/{len(cases)} ({under_predictions/len(cases)*100:.0f}%)")
            print(f"  High error cases (>$500): {high_error_cases}")
            
            # Show worst cases
            worst_cases = sorted(cases, key=lambda x: x['abs_error'], reverse=True)[:3]
            print(f"  Worst cases:")
            for case in worst_cases:
                direction = "under" if case['error'] < 0 else "over"
                print(f"    Case {case['case_id']}: ${case['receipts_per_day']:.0f}/day, "
                      f"${case['predicted']:.0f} vs ${case['expected']:.0f} ({direction})")
    
    print(f"\n📈 SUMMARY:")
    print(f"Total high-error cases in systematic patterns: {total_high_error_cases}")
    
    return problem_patterns

def suggest_fixes(problem_patterns):
    """Suggest specific fixes based on the analysis"""
    
    print(f"\n🛠️ SUGGESTED SYSTEMATIC FIXES:")
    print("=" * 40)
    
    for pattern_name, cases in problem_patterns.items():
        if cases and len(cases) >= 3:  # Only suggest fixes for patterns with multiple cases
            avg_error = sum(c['error'] for c in cases) / len(cases)
            under_pct = sum(1 for c in cases if c['error'] < 0) / len(cases)
            
            if abs(avg_error) > 100:  # Significant systematic bias
                if pattern_name == '4d_extreme':
                    print(f"\n1. 4-DAY EXTREME RECEIPTS (400+/day):")
                    print(f"   Current: {under_pct*100:.0f}% under-predicted by avg ${abs(avg_error):.0f}")
                    print(f"   Fix: Reduce penalty from 0.8 to 0.9-0.95 for 4d trips with 400+/day")
                    
                elif pattern_name == '5d_extreme':
                    print(f"\n2. 5-DAY EXTREME RECEIPTS (400+/day):")
                    print(f"   Current: {under_pct*100:.0f}% under-predicted by avg ${abs(avg_error):.0f}")
                    print(f"   Fix: Increase reimbursement rate from 0.75-0.85 to 0.9-1.0 for 5d extreme")
                    
                elif pattern_name == '6d_high':
                    print(f"\n3. 6-DAY HIGH RECEIPTS (200-300/day):")
                    print(f"   Current: {under_pct*100:.0f}% under-predicted by avg ${abs(avg_error):.0f}")
                    print(f"   Fix: Add positive adjustment for 6d trips with 200-300/day (currently no bonus)")
                    
                elif pattern_name == '10d_medium':
                    print(f"\n4. 10-DAY MEDIUM RECEIPTS (100-200/day):")
                    print(f"   Current: {under_pct*100:.0f}% under-predicted by avg ${abs(avg_error):.0f}")
                    print(f"   Fix: Increase bonus from 1.1 to 1.2-1.3 for 10d reasonable spending")
                    
                elif pattern_name == '11d_medium':
                    print(f"\n5. 11-DAY MEDIUM RECEIPTS (100-200/day):")
                    print(f"   Current: {under_pct*100:.0f}% under-predicted by avg ${abs(avg_error):.0f}")
                    print(f"   Fix: Increase bonus from 1.05 to 1.15-1.2 for 11d reasonable spending")

if __name__ == "__main__":
    problem_patterns = test_systematic_fixes()
    suggest_fixes(problem_patterns)
