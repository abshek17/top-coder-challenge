import json
from legacy_calculate import calculate_legacy_reimbursement

# Load public test cases
with open('public_cases.json', 'r') as f:
    test_cases = json.load(f)

# Analyze single-day trip patterns
single_day_cases = []
for i, case in enumerate(test_cases):
    if case['input']['trip_duration_days'] == 1:
        predicted = calculate_legacy_reimbursement(
            case['input']['trip_duration_days'],
            case['input']['miles_traveled'], 
            case['input']['total_receipts_amount']
        )
        single_day_cases.append({
            'case': i,
            'miles': case['input']['miles_traveled'],
            'receipts': case['input']['total_receipts_amount'],
            'actual': case['expected_output'],
            'predicted': predicted,
            'error': abs(predicted - case['expected_output'])
        })

# Sort by receipts to see the pattern
single_day_cases.sort(key=lambda x: x['receipts'])

print("Single-day trip patterns (sorted by receipts):")
print("Miles\tReceipts\tActual\tPredicted\tError")
for case in single_day_cases[:20]:  # First 20 cases
    print(f"{case['miles']}\t${case['receipts']:.2f}\t\t${case['actual']:.2f}\t${case['predicted']:.2f}\t\t${case['error']:.2f}")

print("\n" + "="*60)
print("High receipt single-day cases:")
high_receipt_cases = [c for c in single_day_cases if c['receipts'] > 1000]
high_receipt_cases.sort(key=lambda x: x['receipts'])
for case in high_receipt_cases:
    print(f"{case['miles']}\t${case['receipts']:.2f}\t\t${case['actual']:.2f}\t${case['predicted']:.2f}\t\t${case['error']:.2f}")
