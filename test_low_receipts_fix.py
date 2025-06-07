from legacy_calculate import calculate_legacy_reimbursement

# Test the top high-error cases from the evaluation
print("Testing high-error cases with low daily spending penalty:")
print("Days\tMiles\tReceipts\tR/Day\tActual\t\tOld Pred\tNew Pred\tNew Error")

test_cases = [
    (8, 795, 1645.99, 644.69),  # Case 684 - Wait, this has HIGH receipts! Different issue
    (10, 1192, 23.47, 1157.87),  # Case 522
    (11, 1149, 270.81, 1284.51), # Case 973  
    (11, 816, 544.99, 1077.12),  # Case 615
    (11, 1004, 167.15, 1175.65), # Case 349
]

for days, miles, receipts, actual in test_cases:
    receipts_per_day = receipts / days
    new_pred = calculate_legacy_reimbursement(days, miles, receipts)
    new_error = abs(new_pred - actual)
    
    # Estimate old prediction (before this fix) - approximate
    if days >= 10 and receipts_per_day < 50:
        old_pred_estimate = new_pred / 0.7  # Reverse the penalty to estimate old value
    else:
        old_pred_estimate = new_pred
    
    print(f"{days}\t{miles}\t${receipts:.2f}\t\t${receipts_per_day:.2f}\t${actual:.2f}\t\t${old_pred_estimate:.2f}\t${new_pred:.2f}\t\t${new_error:.2f}")

# Special analysis for Case 684 (8d, 795mi, $1645.99) - this is different!
print("\n" + "="*60)
print("Case 684 analysis (8d, 795mi, $1645.99 receipts -> $644.69 actual):")
print("This has HIGH receipts ($205/day) but low reimbursement - different pattern!")
print("This might be 'vacation with fake receipts' - high spending but rejected as personal travel")

case_684_pred = calculate_legacy_reimbursement(8, 795, 1645.99)
print(f"Current prediction: ${case_684_pred:.2f} vs actual $644.69")
