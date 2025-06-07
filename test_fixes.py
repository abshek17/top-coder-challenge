from legacy_calculate import calculate_legacy_reimbursement

# Test the fraud case
print('Case 995 (fraud): 1082mi, $1809.49')
result = calculate_legacy_reimbursement(1, 1082, 1809.49)
print('Predicted: ${:.2f}, Actual: $446.94'.format(result))

# Test some long trips
print('\nLong trip tests:')
print('10d, 793mi, $1422.29 -> Predicted: ${:.2f}, Actual: $2007.62'.format(calculate_legacy_reimbursement(10, 793, 1422.29)))
print('12d, 398mi, $2481.44 -> Predicted: ${:.2f}, Actual: $1755.18'.format(calculate_legacy_reimbursement(12, 398, 2481.44)))
print('11d, 667mi, $2221.67 -> Predicted: ${:.2f}, Actual: $1872.89'.format(calculate_legacy_reimbursement(11, 667, 2221.67)))
