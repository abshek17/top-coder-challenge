from legacy_calculate import calculate_legacy_reimbursement

# Test that Case 684 still works
result = calculate_legacy_reimbursement(8, 795, 1645.99)
print('Case 684: ${:.2f} (target: $644.69)'.format(result))

# Test that we fixed the over-penalized cases
print('\nTesting previously over-penalized cases:')
print('Case 656 (9d, 1165mi, $1868.79): ${:.2f} (target: ~$1946)'.format(calculate_legacy_reimbursement(9, 1165, 1868.79)))
print('Case 280 (9d, 938mi, $2224.29): ${:.2f} (target: ~$1914)'.format(calculate_legacy_reimbursement(9, 938, 2224.29)))
print('Case 513 (9d, 1064mi, $2016.76): ${:.2f} (target: ~$1811)'.format(calculate_legacy_reimbursement(9, 1064, 2016.76)))
