import json
from legacy_calculate import calculate_legacy_reimbursement

# Load public test cases
with open('public_cases.json', 'r') as f:
    test_cases = json.load(f)

# Find single-day cases with high mileage + high receipts
single_day_high_both = []
for i, case in enumerate(test_cases):
    if case['input']['trip_duration_days'] == 1:
        miles = case['input']['miles_traveled']
        receipts = case['input']['total_receipts_amount']
        if miles > 1000 and receipts > 1500:
            predicted = calculate_legacy_reimbursement(1, miles, receipts)
            single_day_high_both.append({
                'case': i,
                'miles': miles,
                'receipts': receipts,
                'actual': case['expected_output'],
                'predicted': predicted,
                'error': abs(predicted - case['expected_output'])
            })

print("Single-day trips with >1000 miles AND >$1500 receipts:")
print("Miles\tReceipts\tActual\t\tPredicted\tError")
for case in single_day_high_both:
    print(f"{case['miles']}\t${case['receipts']:.2f}\t\t${case['actual']:.2f}\t\t${case['predicted']:.2f}\t\t${case['error']:.2f}")

# Check the one known fraud case
print("\n" + "="*60)
print("Known fraud case:")
case_995 = None
for i, case in enumerate(test_cases):
    if i == 995:
        miles = case['input']['miles_traveled']
        receipts = case['input']['total_receipts_amount']
        actual = case['expected_output']
        predicted = calculate_legacy_reimbursement(1, miles, receipts)
        print(f"Case 995: {miles}mi, ${receipts:.2f} -> Actual: ${actual:.2f}, Predicted: ${predicted:.2f}")
        break
