import json
from legacy_calculate import calculate_legacy_reimbursement

# Load test cases
with open('public_cases.json', 'r') as f:
    test_cases = json.load(f)

# High error cases from the results
high_error_cases = [684, 522, 973, 615, 349]

print("Analyzing top high-error cases:")
print("=" * 60)

for case_id in high_error_cases:
    case = test_cases[case_id]
    days = case['input']['trip_duration_days']
    miles = case['input']['miles_traveled']
    receipts = case['input']['total_receipts_amount']
    expected = case['expected_output']
    
    predicted = calculate_legacy_reimbursement(days, miles, receipts)
    error = abs(predicted - expected)
    
    receipts_per_day = receipts / days if days > 0 else 0
    
    print(f"Case {case_id}: {days}d, {miles}mi, ${receipts:.2f}")
    print(f"  Expected: ${expected:.2f}")
    print(f"  Predicted: ${predicted:.2f}")
    print(f"  Error: ${error:.2f}")
    print(f"  Receipts per day: ${receipts_per_day:.2f}")
    print()

# Let's look for patterns in all 10+ day trips with low receipts
print("\nAnalyzing all 10+ day trips with low receipts per day:")
print("=" * 60)

low_receipt_long_trips = []
for i, case in enumerate(test_cases):
    days = case['input']['trip_duration_days']
    miles = case['input']['miles_traveled']
    receipts = case['input']['total_receipts_amount']
    expected = case['expected_output']
    
    if days >= 10:
        receipts_per_day = receipts / days
        predicted = calculate_legacy_reimbursement(days, miles, receipts)
        error = abs(predicted - expected)
        
        if receipts_per_day < 75:  # Low receipts per day
            low_receipt_long_trips.append({
                'case': i,
                'days': days,
                'miles': miles,
                'receipts': receipts,
                'receipts_per_day': receipts_per_day,
                'expected': expected,
                'predicted': predicted,
                'error': error
            })

# Sort by error
low_receipt_long_trips.sort(key=lambda x: x['error'], reverse=True)

print(f"Found {len(low_receipt_long_trips)} cases with 10+ days and <$75/day receipts")
print("Top 10 by error:")
for trip in low_receipt_long_trips[:10]:
    print(f"Case {trip['case']}: {trip['days']}d, {trip['miles']}mi, ${trip['receipts']:.2f} (${trip['receipts_per_day']:.2f}/day)")
    print(f"  Expected: ${trip['expected']:.2f}, Predicted: ${trip['predicted']:.2f}, Error: ${trip['error']:.2f}")

# Check if Case 684 (8-day vacation) is being caught
print(f"\nCase 684 analysis:")
case = test_cases[684]
days = case['input']['trip_duration_days']
miles = case['input']['miles_traveled']
receipts = case['input']['total_receipts_amount']
expected = case['expected_output']
predicted = calculate_legacy_reimbursement(days, miles, receipts)

print(f"Case 684: {days}d, {miles}mi, ${receipts:.2f}")
print(f"Expected: ${expected:.2f}, Predicted: ${predicted:.2f}")
print(f"This looks like vacation with fake receipts (8 days, ~795 miles, ~$1645)")

# Let's also check for specific patterns in the high error cases
print(f"\nLooking for additional patterns in high error cases:")
print("=" * 60)

all_high_errors = []
for i, case in enumerate(test_cases):
    days = case['input']['trip_duration_days']
    miles = case['input']['miles_traveled']
    receipts = case['input']['total_receipts_amount']
    expected = case['expected_output']
    
    predicted = calculate_legacy_reimbursement(days, miles, receipts)
    error = abs(predicted - expected)
    
    if error > 500:  # High error threshold
        all_high_errors.append({
            'case': i,
            'days': days,
            'miles': miles,
            'receipts': receipts,
            'expected': expected,
            'predicted': predicted,
            'error': error,
            'receipts_per_day': receipts / days if days > 0 else 0
        })

# Sort by error and analyze patterns
all_high_errors.sort(key=lambda x: x['error'], reverse=True)

print(f"Total high error cases (>$500): {len(all_high_errors)}")
print("Top 15 by error:")
for i, case in enumerate(all_high_errors[:15]):
    print(f"{i+1}. Case {case['case']}: {case['days']}d, {case['miles']}mi, ${case['receipts']:.2f}")
    print(f"   Expected: ${case['expected']:.2f}, Predicted: ${case['predicted']:.2f}, Error: ${case['error']:.2f}")
    print(f"   ${case['receipts_per_day']:.2f}/day")
