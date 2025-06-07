#!/usr/bin/env python3
"""
CLI:
    python3 calculate_reimbursement.py <trip_duration_days> <miles_traveled> <total_receipts_amount>
Prints the predicted reimbursement using a pre‑trained decision‑tree model.
"""
import sys, joblib, numpy as np, pathlib

MODEL_PATH = pathlib.Path(__file__).with_name("reimbursement_model.joblib")
_model = joblib.load(MODEL_PATH)

def predict(days: float, miles: float, receipts: float) -> float:
    X = np.array([[days, miles, receipts]], dtype=float)
    return round(float(_model.predict(X)[0]), 2)

if __name__ == "__main__":
    if len(sys.argv) != 4:
        sys.exit("Usage: calculate_reimbursement.py <days> <miles> <receipts>")
    d, m, r = map(float, sys.argv[1:])
    print(predict(d, m, r))
