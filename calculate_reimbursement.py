#!/usr/bin/env python3
"""
Wrapper script for the legacy reimbursement calculation
Usage: python3 calculate_reimbursement.py <trip_duration_days> <miles_traveled> <total_receipts_amount>
"""

import sys
from legacy_calculate import calculate_legacy_reimbursement

def main():
    if len(sys.argv) != 4:
        print("Usage: python3 calculate_reimbursement.py <trip_duration_days> <miles_traveled> <total_receipts_amount>", file=sys.stderr)
        sys.exit(1)
    
    try:
        trip_duration_days = int(sys.argv[1])
        miles_traveled = float(sys.argv[2])
        total_receipts_amount = float(sys.argv[3])
        
        result = calculate_legacy_reimbursement(trip_duration_days, miles_traveled, total_receipts_amount)
        print(result)
        
    except ValueError as e:
        print(f"Error: Invalid input format - {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
