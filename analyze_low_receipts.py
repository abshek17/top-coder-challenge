import json
from legacy_calculate import calculate_legacy_reimbursement

# Load public test cases
with open('public_cases.json', 'r') as f:
    test_cases = json.load(f)

# Analyze long trips with low receipts
low_receipt_long_trips = []
for i, case in enumerate(test_cases):
    days = case['input']['trip_duration_days']
    miles = case['input']['miles_traveled']
    receipts = case['input']['total_receipts_amount']
    
    if days >= 8 and receipts < 1000:  # Long trips with low receipts
        predicted = calculate_legacy_reimbursement(days, miles, receipts)
        actual = case['expected_output']
        error = abs(predicted - actual)
        
        low_receipt_long_trips.append({
            'case': i,
            'days': days,
            'miles': miles,
            'receipts': receipts,
            'receipts_per_day': receipts / days,
            'actual': actual,
            'predicted': predicted,
            'error': error
        })

# Sort by error to see the worst cases
low_receipt_long_trips.sort(key=lambda x: x['error'], reverse=True)

print("Long trips (8+ days) with low receipts (<$1000), sorted by error:")
print("Days\tMiles\tReceipts\tR/Day\tActual\t\tPredicted\tError")
for case in low_receipt_long_trips[:20]:
    print(f"{case['days']}\t{case['miles']}\t${case['receipts']:.2f}\t\t${case['receipts_per_day']:.2f}\t${case['actual']:.2f}\t\t${case['predicted']:.2f}\t\t${case['error']:.2f}")

print("\n" + "="*80)
print("Pattern analysis:")

# Group by receipts per day to see pattern
very_low_per_day = [c for c in low_receipt_long_trips if c['receipts_per_day'] < 50]
print(f"\nVery low receipts per day (<$50): {len(very_low_per_day)} cases")
if very_low_per_day:
    avg_actual = sum(c['actual'] for c in very_low_per_day) / len(very_low_per_day)
    avg_predicted = sum(c['predicted'] for c in very_low_per_day) / len(very_low_per_day)
    print(f"Average actual: ${avg_actual:.2f}, Average predicted: ${avg_predicted:.2f}")

medium_per_day = [c for c in low_receipt_long_trips if 50 <= c['receipts_per_day'] < 100]
print(f"\nMedium receipts per day ($50-100): {len(medium_per_day)} cases")
if medium_per_day:
    avg_actual = sum(c['actual'] for c in medium_per_day) / len(medium_per_day)
    avg_predicted = sum(c['predicted'] for c in medium_per_day) / len(medium_per_day)
    print(f"Average actual: ${avg_actual:.2f}, Average predicted: ${avg_predicted:.2f}")
