import json
from legacy_calculate import calculate_legacy_reimbursement

# Load public test cases
with open('public_cases.json', 'r') as f:
    test_cases = json.load(f)

# Analyze long trip patterns (8+ days)
long_trip_cases = []
for i, case in enumerate(test_cases):
    if case['input']['trip_duration_days'] >= 8:
        predicted = calculate_legacy_reimbursement(
            case['input']['trip_duration_days'],
            case['input']['miles_traveled'], 
            case['input']['total_receipts_amount']
        )
        long_trip_cases.append({
            'case': i,
            'days': case['input']['trip_duration_days'],
            'miles': case['input']['miles_traveled'],
            'receipts': case['input']['total_receipts_amount'],
            'actual': case['expected_output'],
            'predicted': predicted,
            'error': abs(predicted - case['expected_output'])
        })

# Sort by error to see the worst cases
long_trip_cases.sort(key=lambda x: x['error'], reverse=True)

print("Long trip patterns (8+ days, sorted by error):")
print("Days\tMiles\tReceipts\tActual\t\tPredicted\tError")
for case in long_trip_cases[:15]:  # Top 15 worst cases
    print(f"{case['days']}\t{case['miles']}\t${case['receipts']:.2f}\t\t${case['actual']:.2f}\t\t${case['predicted']:.2f}\t\t${case['error']:.2f}")

print("\n" + "="*60)
print("Specific patterns:")

# Look for patterns in the long trips
print("\n10-day trips:")
ten_day_cases = [c for c in long_trip_cases if c['days'] == 10]
ten_day_cases.sort(key=lambda x: x['receipts'])
for case in ten_day_cases[:10]:
    print(f"{case['days']}\t{case['miles']}\t${case['receipts']:.2f}\t\t${case['actual']:.2f}\t\t${case['predicted']:.2f}\t\t${case['error']:.2f}")

print("\n12-day trips:")
twelve_day_cases = [c for c in long_trip_cases if c['days'] == 12]
twelve_day_cases.sort(key=lambda x: x['receipts'])
for case in twelve_day_cases[:10]:
    print(f"{case['days']}\t{case['miles']}\t${case['receipts']:.2f}\t\t${case['actual']:.2f}\t\t${case['predicted']:.2f}\t\t${case['error']:.2f}")

# Analyze the single-day anomaly
print("\n" + "="*60)
print("Single-day anomalies (high mileage + high receipts with low reimbursement):")
single_day_cases = []
for i, case in enumerate(test_cases):
    if case['input']['trip_duration_days'] == 1:
        predicted = calculate_legacy_reimbursement(
            case['input']['trip_duration_days'],
            case['input']['miles_traveled'], 
            case['input']['total_receipts_amount']
        )
        if case['expected_output'] < 600 and case['input']['total_receipts_amount'] > 1000:
            single_day_cases.append({
                'case': i,
                'miles': case['input']['miles_traveled'],
                'receipts': case['input']['total_receipts_amount'],
                'actual': case['expected_output'],
                'predicted': predicted,
                'error': abs(predicted - case['expected_output'])
            })

for case in single_day_cases:
    print(f"Case {case['case']}: {case['miles']}mi, ${case['receipts']:.2f} -> Actual: ${case['actual']:.2f}, Predicted: ${case['predicted']:.2f}")
