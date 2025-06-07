import json
from legacy_calculate import calculate_legacy_reimbursement

# Load public test cases
with open('public_cases.json', 'r') as f:
    test_cases = json.load(f)

errors = []
exact_matches = 0
high_error_cases = []

for i, case in enumerate(test_cases):
    predicted = calculate_legacy_reimbursement(
        case['input']['trip_duration_days'],
        case['input']['miles_traveled'], 
        case['input']['total_receipts_amount']
    )
    actual = case['expected_output']
    error = abs(predicted - actual)
    errors.append(error)
    
    if error == 0:
        exact_matches += 1
    elif error > 500:
        high_error_cases.append({
            'case': i, 
            'inputs': case['input'],
            'predicted': predicted,
            'actual': actual, 
            'error': error
        })

avg_error = sum(errors) / len(errors)
print('Average Error: ${:.2f}'.format(avg_error))
print('Exact Matches: {}/{} ({:.1f}%)'.format(exact_matches, len(test_cases), exact_matches/len(test_cases)*100))
print('High Error Cases (>$500): {}'.format(len(high_error_cases)))

# Show a few high error cases
print()
print('Top high-error cases:')
high_error_cases.sort(key=lambda x: x['error'], reverse=True)
for case in high_error_cases[:5]:
    inp = case['inputs']
    print('Case {}: {}d, {}mi, ${:.2f} -> Predicted: ${:.2f}, Actual: ${:.2f}, Error: ${:.2f}'.format(
        case['case'], inp['trip_duration_days'], inp['miles_traveled'], inp['total_receipts_amount'],
        case['predicted'], case['actual'], case['error']))
