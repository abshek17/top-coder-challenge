import json
from legacy_calculate import calculate_legacy_reimbursement

# Load public test cases
with open('public_cases.json', 'r') as f:
    test_cases = json.load(f)

# Analyze 14-day trips specifically
fourteen_day_cases = []
for i, case in enumerate(test_cases):
    if case['input']['trip_duration_days'] == 14:
        predicted = calculate_legacy_reimbursement(
            case['input']['trip_duration_days'],
            case['input']['miles_traveled'], 
            case['input']['total_receipts_amount']
        )
        fourteen_day_cases.append({
            'case': i,
            'miles': case['input']['miles_traveled'],
            'receipts': case['input']['total_receipts_amount'],
            'actual': case['expected_output'],
            'predicted': predicted,
            'error': abs(predicted - case['expected_output'])
        })

# Sort by receipts to see the pattern
fourteen_day_cases.sort(key=lambda x: x['receipts'])

print("14-day trip patterns (sorted by receipts):")
print("Miles\tReceipts\tActual\t\tPredicted\tError")
for case in fourteen_day_cases:
    print(f"{case['miles']}\t${case['receipts']:.2f}\t\t${case['actual']:.2f}\t\t${case['predicted']:.2f}\t\t${case['error']:.2f}")

# Also check 8-9 day trips that are still over-predicted
print("\n" + "="*60)
print("8-9 day high-error cases:")
eight_nine_day_cases = []
for i, case in enumerate(test_cases):
    if case['input']['trip_duration_days'] in [8, 9]:
        predicted = calculate_legacy_reimbursement(
            case['input']['trip_duration_days'],
            case['input']['miles_traveled'], 
            case['input']['total_receipts_amount']
        )
        error = abs(predicted - case['expected_output'])
        if error > 500:
            eight_nine_day_cases.append({
                'case': i,
                'days': case['input']['trip_duration_days'],
                'miles': case['input']['miles_traveled'],
                'receipts': case['input']['total_receipts_amount'],
                'actual': case['expected_output'],
                'predicted': predicted,
                'error': error
            })

eight_nine_day_cases.sort(key=lambda x: x['error'], reverse=True)
for case in eight_nine_day_cases[:10]:
    print(f"{case['days']}d\t{case['miles']}\t${case['receipts']:.2f}\t\t${case['actual']:.2f}\t\t${case['predicted']:.2f}\t\t${case['error']:.2f}")
