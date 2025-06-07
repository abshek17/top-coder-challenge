from legacy_calculate import calculate_legacy_reimbursement

# Test Case 684 specifically
result = calculate_legacy_reimbursement(8, 795, 1645.99)
print('Case 684 (8d, 795mi, $1645.99): Predicted ${:.2f}, Actual $644.69, Error ${:.2f}'.format(result, abs(result - 644.69)))

# Make sure we didn't break the other fixes
print('\nRetesting other cases:')
print('Case 522: ${:.2f} (target: ~$1158)'.format(calculate_legacy_reimbursement(10, 1192, 23.47)))
print('Case 973: ${:.2f} (target: ~$1285)'.format(calculate_legacy_reimbursement(11, 1149, 270.81)))
