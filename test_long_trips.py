from legacy_calculate import calculate_legacy_reimbursement

# Test 14-day trips
print('14-day trip tests:')
print('14d, 1100mi, $237.69 -> Predicted: ${:.2f}, Actual: $1265.57'.format(calculate_legacy_reimbursement(14, 1100, 237.69)))
print('14d, 1153mi, $346.58 -> Predicted: ${:.2f}, Actual: $1292.93'.format(calculate_legacy_reimbursement(14, 1153, 346.58)))

# Test 8-day high-mileage trips
print('\n8-day high-mileage tests:')
print('8d, 1090mi, $419.76 -> Predicted: ${:.2f}, Actual: $1189.47'.format(calculate_legacy_reimbursement(8, 1090, 419.76)))
print('8d, 1166mi, $99.47 -> Predicted: ${:.2f}, Actual: $1149.07'.format(calculate_legacy_reimbursement(8, 1166, 99.47)))

# Test 10-12 day trips (should still be good)
print('\n10-12 day tests:')
print('10d, 793mi, $1422.29 -> Predicted: ${:.2f}, Actual: $2007.62'.format(calculate_legacy_reimbursement(10, 793, 1422.29)))
print('12d, 398mi, $2481.44 -> Predicted: ${:.2f}, Actual: $1755.18'.format(calculate_legacy_reimbursement(12, 398, 2481.44)))
