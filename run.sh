#!/bin/bash

# Black Box Challenge - Your Implementation
# This script should take three parameters and output the reimbursement amount
# Usage: ./run.sh <trip_duration_days> <miles_traveled> <total_receipts_amount>

# Check if we have the correct number of arguments
if [ $# -ne 3 ]; then
    echo "Usage: $0 <trip_duration_days> <miles_traveled> <total_receipts_amount>" >&2
    exit 1
fi

# Use Python implementation with legacy calculation rules
python3 calculate_reimbursement.py "$1" "$2" "$3" 