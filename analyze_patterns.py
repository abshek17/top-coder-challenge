import json
from legacy_calculate import calculate_legacy_reimbursement

# Load test cases
with open('public_cases.json', 'r') as f:
    test_cases = json.load(f)

print("Analyzing specific patterns:")
print("=" * 60)

# 1. Analyze 14-day trips with high receipts
print("1. 14-day trips with high receipts:")
fourteen_day_high = []
for i, case in enumerate(test_cases):
    days = case['input']['trip_duration_days']
    miles = case['input']['miles_traveled']
    receipts = case['input']['total_receipts_amount']
    expected = case['expected_output']
    
    if days == 14 and receipts > 1500:
        predicted = calculate_legacy_reimbursement(days, miles, receipts)
        error = abs(predicted - expected)
        fourteen_day_high.append({
            'case': i,
            'miles': miles,
            'receipts': receipts,
            'expected': expected,
            'predicted': predicted,
            'error': error,
            'receipts_per_day': receipts / days
        })

fourteen_day_high.sort(key=lambda x: x['error'], reverse=True)
print(f"Found {len(fourteen_day_high)} cases")
for case in fourteen_day_high[:10]:
    print(f"Case {case['case']}: {case['miles']}mi, ${case['receipts']:.2f} (${case['receipts_per_day']:.2f}/day)")
    print(f"  Expected: ${case['expected']:.2f}, Predicted: ${case['predicted']:.2f}, Error: ${case['error']:.2f}")

print()

# 2. Analyze single-day trips with high receipts
print("2. Single-day trips with high receipts:")
single_day_high = []
for i, case in enumerate(test_cases):
    days = case['input']['trip_duration_days']
    miles = case['input']['miles_traveled']
    receipts = case['input']['total_receipts_amount']
    expected = case['expected_output']
    
    if days == 1 and receipts > 400:
        predicted = calculate_legacy_reimbursement(days, miles, receipts)
        error = abs(predicted - expected)
        single_day_high.append({
            'case': i,
            'miles': miles,
            'receipts': receipts,
            'expected': expected,
            'predicted': predicted,
            'error': error
        })

single_day_high.sort(key=lambda x: x['error'], reverse=True)
print(f"Found {len(single_day_high)} cases")
for case in single_day_high[:10]:
    print(f"Case {case['case']}: {case['miles']}mi, ${case['receipts']:.2f}")
    print(f"  Expected: ${case['expected']:.2f}, Predicted: ${case['predicted']:.2f}, Error: ${case['error']:.2f}")

print()

# 3. Analyze 4-5 day trips with very high receipts per day
print("3. Short trips (4-5 days) with very high receipts per day:")
short_high = []
for i, case in enumerate(test_cases):
    days = case['input']['trip_duration_days']
    miles = case['input']['miles_traveled']
    receipts = case['input']['total_receipts_amount']
    expected = case['expected_output']
    
    if days in [4, 5] and receipts/days > 400:
        predicted = calculate_legacy_reimbursement(days, miles, receipts)
        error = abs(predicted - expected)
        short_high.append({
            'case': i,
            'days': days,
            'miles': miles,
            'receipts': receipts,
            'expected': expected,
            'predicted': predicted,
            'error': error,
            'receipts_per_day': receipts / days
        })

short_high.sort(key=lambda x: x['error'], reverse=True)
print(f"Found {len(short_high)} cases")
for case in short_high[:10]:
    print(f"Case {case['case']}: {case['days']}d, {case['miles']}mi, ${case['receipts']:.2f} (${case['receipts_per_day']:.2f}/day)")
    print(f"  Expected: ${case['expected']:.2f}, Predicted: ${case['predicted']:.2f}, Error: ${case['error']:.2f}")

print()

# 4. Analyze 11-day trips that are being over-predicted
print("4. 11-day trips with high errors:")
eleven_day = []
for i, case in enumerate(test_cases):
    days = case['input']['trip_duration_days']
    miles = case['input']['miles_traveled']
    receipts = case['input']['total_receipts_amount']
    expected = case['expected_output']
    
    if days == 11:
        predicted = calculate_legacy_reimbursement(days, miles, receipts)
        error = abs(predicted - expected)
        if error > 200:
            eleven_day.append({
                'case': i,
                'miles': miles,
                'receipts': receipts,
                'expected': expected,
                'predicted': predicted,
                'error': error,
                'receipts_per_day': receipts / days,
                'over_predicted': predicted > expected
            })

eleven_day.sort(key=lambda x: x['error'], reverse=True)
print(f"Found {len(eleven_day)} cases with error > $200")
for case in eleven_day[:5]:
    over_under = "OVER" if case['over_predicted'] else "UNDER"
    print(f"Case {case['case']}: {case['miles']}mi, ${case['receipts']:.2f} (${case['receipts_per_day']:.2f}/day)")
    print(f"  Expected: ${case['expected']:.2f}, Predicted: ${case['predicted']:.2f}, Error: ${case['error']:.2f} ({over_under})")
