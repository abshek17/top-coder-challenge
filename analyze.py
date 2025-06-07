import json
import pandas as pd
import matplotlib.pyplot as plt

# Load and explore the data
with open('public_cases.json') as f:
    data = json.load(f)

df = pd.DataFrame(data)
print(df.describe())
print(df.head(20))

# Look for correlations
df.plot.scatter(x='trip_duration_days', y='reimbursement')
df.plot.scatter(x='miles_traveled', y='reimbursement')
df.plot.scatter(x='total_receipts_amount', y='reimbursement')