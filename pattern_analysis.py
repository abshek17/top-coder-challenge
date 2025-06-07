#!/usr/bin/env python3
"""
Comprehensive analysis of the reimbursement patterns in public_cases.json
"""

import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from legacy_calculate import calculate_legacy_reimbursement

# Load the data
print("Loading public cases...")
with open('public_cases.json', 'r') as f:
    data = json.load(f)

# Convert to DataFrame
cases = []
for i, case in enumerate(data):
    inp = case['input']
    expected = case['expected_output']
    
    # Calculate our prediction
    predicted = calculate_legacy_reimbursement(
        inp['trip_duration_days'], 
        inp['miles_traveled'], 
        inp['total_receipts_amount']
    )
    
    cases.append({
        'case_id': i + 1,
        'trip_duration_days': inp['trip_duration_days'],
        'miles_traveled': inp['miles_traveled'],
        'total_receipts_amount': inp['total_receipts_amount'],
        'expected_reimbursement': expected,
        'predicted_reimbursement': predicted,
        'error': abs(predicted - expected),
        'miles_per_day': inp['miles_traveled'] / inp['trip_duration_days'] if inp['trip_duration_days'] > 0 else 0,
        'receipts_per_day': inp['total_receipts_amount'] / inp['trip_duration_days'] if inp['trip_duration_days'] > 0 else 0
    })

df = pd.DataFrame(cases)

print(f"Loaded {len(df)} cases")
print(f"Average error: ${df['error'].mean():.2f}")
print(f"Max error: ${df['error'].max():.2f}")

# Basic statistics
print("\n=== BASIC STATISTICS ===")
print(df[['trip_duration_days', 'miles_traveled', 'total_receipts_amount', 'expected_reimbursement']].describe())

# Create comprehensive visualizations
plt.style.use('default')
fig = plt.figure(figsize=(20, 16))

# 1. Expected vs Predicted scatter plot
plt.subplot(3, 4, 1)
plt.scatter(df['expected_reimbursement'], df['predicted_reimbursement'], alpha=0.6, s=20)
plt.plot([0, df['expected_reimbursement'].max()], [0, df['expected_reimbursement'].max()], 'r--', label='Perfect prediction')
plt.xlabel('Expected Reimbursement')
plt.ylabel('Predicted Reimbursement')
plt.title('Expected vs Predicted')
plt.legend()

# 2. Error by trip duration
plt.subplot(3, 4, 2)
df.boxplot(column='error', by='trip_duration_days', ax=plt.gca())
plt.title('Error by Trip Duration')
plt.suptitle('')

# 3. Expected reimbursement by trip duration
plt.subplot(3, 4, 3)
df.boxplot(column='expected_reimbursement', by='trip_duration_days', ax=plt.gca())
plt.title('Expected Reimbursement by Trip Duration')
plt.suptitle('')

# 4. Miles vs Expected Reimbursement colored by trip duration
plt.subplot(3, 4, 4)
scatter = plt.scatter(df['miles_traveled'], df['expected_reimbursement'], 
                     c=df['trip_duration_days'], cmap='viridis', alpha=0.6, s=20)
plt.colorbar(scatter, label='Trip Duration (days)')
plt.xlabel('Miles Traveled')
plt.ylabel('Expected Reimbursement')
plt.title('Miles vs Expected (colored by duration)')

# 5. Receipts vs Expected Reimbursement colored by trip duration
plt.subplot(3, 4, 5)
scatter = plt.scatter(df['total_receipts_amount'], df['expected_reimbursement'], 
                     c=df['trip_duration_days'], cmap='viridis', alpha=0.6, s=20)
plt.colorbar(scatter, label='Trip Duration (days)')
plt.xlabel('Total Receipts Amount')
plt.ylabel('Expected Reimbursement')
plt.title('Receipts vs Expected (colored by duration)')

# 6. Miles per day vs Expected
plt.subplot(3, 4, 6)
scatter = plt.scatter(df['miles_per_day'], df['expected_reimbursement'], 
                     c=df['trip_duration_days'], cmap='viridis', alpha=0.6, s=20)
plt.colorbar(scatter, label='Trip Duration (days)')
plt.xlabel('Miles per Day')
plt.ylabel('Expected Reimbursement')
plt.title('Miles/Day vs Expected')

# 7. Receipts per day vs Expected
plt.subplot(3, 4, 7)
scatter = plt.scatter(df['receipts_per_day'], df['expected_reimbursement'], 
                     c=df['trip_duration_days'], cmap='viridis', alpha=0.6, s=20)
plt.colorbar(scatter, label='Trip Duration (days)')
plt.xlabel('Receipts per Day')
plt.ylabel('Expected Reimbursement')
plt.title('Receipts/Day vs Expected')

# 8. Error heatmap by trip duration and miles bins
plt.subplot(3, 4, 8)
df['miles_bin'] = pd.cut(df['miles_traveled'], bins=10, labels=False)
error_heatmap = df.groupby(['trip_duration_days', 'miles_bin'])['error'].mean().unstack()
sns.heatmap(error_heatmap, annot=True, fmt='.0f', cmap='Reds')
plt.title('Average Error by Duration & Miles')
plt.xlabel('Miles Bin')
plt.ylabel('Trip Duration')

# 9. High error cases analysis
plt.subplot(3, 4, 9)
high_error = df.nlargest(20, 'error')
colors = ['red' if x == 1 else 'blue' for x in high_error['trip_duration_days']]
plt.scatter(high_error['miles_traveled'], high_error['expected_reimbursement'], 
           c=colors, s=60, alpha=0.7)
plt.xlabel('Miles Traveled')
plt.ylabel('Expected Reimbursement')
plt.title('Top 20 High Error Cases\n(Red=1 day, Blue=Multi-day)')

# 10. Single-day trip analysis
plt.subplot(3, 4, 10)
single_day = df[df['trip_duration_days'] == 1]
plt.scatter(single_day['miles_traveled'], single_day['expected_reimbursement'], 
           c=single_day['total_receipts_amount'], cmap='plasma', alpha=0.7, s=30)
plt.colorbar(label='Receipt Amount')
plt.xlabel('Miles Traveled')
plt.ylabel('Expected Reimbursement')
plt.title('Single-Day Trips\n(colored by receipts)')

# 11. Predicted vs Expected for single-day trips
plt.subplot(3, 4, 11)
plt.scatter(single_day['expected_reimbursement'], single_day['predicted_reimbursement'], 
           alpha=0.7, s=30, color='red')
plt.plot([0, single_day['expected_reimbursement'].max()], 
         [0, single_day['expected_reimbursement'].max()], 'k--', alpha=0.5)
plt.xlabel('Expected Reimbursement')
plt.ylabel('Predicted Reimbursement')
plt.title('Single-Day: Expected vs Predicted')

# 12. Error distribution
plt.subplot(3, 4, 12)
plt.hist(df['error'], bins=50, alpha=0.7, edgecolor='black')
plt.xlabel('Error Amount')
plt.ylabel('Frequency')
plt.title('Error Distribution')
plt.axvline(df['error'].mean(), color='red', linestyle='--', label=f'Mean: ${df["error"].mean():.0f}')
plt.legend()

plt.tight_layout()
plt.savefig('reimbursement_patterns.png', dpi=150, bbox_inches='tight')
plt.show()

# Detailed analysis of problematic patterns
print("\n=== SINGLE-DAY TRIP ANALYSIS ===")
single_day_df = df[df['trip_duration_days'] == 1].copy()
print(f"Number of single-day trips: {len(single_day_df)}")
print(f"Average expected reimbursement: ${single_day_df['expected_reimbursement'].mean():.2f}")
print(f"Average predicted reimbursement: ${single_day_df['predicted_reimbursement'].mean():.2f}")
print(f"Average error: ${single_day_df['error'].mean():.2f}")

print("\nTop 10 worst single-day predictions:")
worst_single = single_day_df.nlargest(10, 'error')
for _, row in worst_single.iterrows():
    print(f"Case {row['case_id']}: {row['miles_traveled']} miles, ${row['total_receipts_amount']:.2f} receipts")
    print(f"  Expected: ${row['expected_reimbursement']:.2f}, Got: ${row['predicted_reimbursement']:.2f}, Error: ${row['error']:.2f}")

print("\n=== MULTI-DAY HIGH-MILEAGE ANALYSIS ===")
multi_day_high_miles = df[(df['trip_duration_days'] >= 6) & (df['miles_traveled'] > 800)].copy()
print(f"Number of 6+ day, 800+ mile trips: {len(multi_day_high_miles)}")
print(f"Average expected reimbursement: ${multi_day_high_miles['expected_reimbursement'].mean():.2f}")
print(f"Average predicted reimbursement: ${multi_day_high_miles['predicted_reimbursement'].mean():.2f}")
print(f"Average error: ${multi_day_high_miles['error'].mean():.2f}")

print("\n=== TRIP DURATION PATTERNS ===")
duration_stats = df.groupby('trip_duration_days').agg({
    'expected_reimbursement': ['count', 'mean', 'std'],
    'predicted_reimbursement': 'mean',
    'error': 'mean'
}).round(2)
print(duration_stats)

print("\n=== CORRELATION ANALYSIS ===")
correlations = df[['trip_duration_days', 'miles_traveled', 'total_receipts_amount', 
                   'expected_reimbursement', 'miles_per_day', 'receipts_per_day']].corr()
print("Correlation with expected_reimbursement:")
print(correlations['expected_reimbursement'].sort_values(ascending=False))

# Save detailed analysis
df.to_csv('reimbursement_analysis.csv', index=False)
print(f"\nDetailed analysis saved to reimbursement_analysis.csv")
print(f"Visualization saved to reimbursement_patterns.png")
