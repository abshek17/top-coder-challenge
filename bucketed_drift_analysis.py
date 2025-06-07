#!/usr/bin/env python3
"""
Bucketed analysis of prediction drift patterns by trip duration and mileage per day.
"""

import json
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import sys
import os
from collections import defaultdict

# Add current directory to path for import
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from legacy_calculate import calculate_legacy_reimbursement
except ImportError as e:
    print(f"Could not import calculate_legacy_reimbursement: {e}")
    sys.exit(1)

def load_and_process_data():
    """Load test cases and calculate predictions with bucketing"""
    with open('public_cases.json', 'r') as f:
        cases = json.load(f)
    
    results = []
    
    for i, case in enumerate(cases):
        try:
            # Handle nested input structure
            input_data = case.get('input', case)
            
            trip_days = input_data['trip_duration_days']
            miles = input_data['miles_traveled']
            receipts = input_data['total_receipts_amount']
            
            pred = calculate_legacy_reimbursement(trip_days, miles, receipts)
            exp = case['expected_output']
            error = pred - exp
            
            # Calculate mileage per day
            miles_per_day = miles / trip_days if trip_days > 0 else 0
            
            # Create buckets
            duration_bucket = get_duration_bucket(trip_days)
            mileage_bucket = get_mileage_bucket(miles_per_day)
            
            results.append({
                'trip_days': trip_days,
                'miles': miles,
                'receipts': receipts,
                'miles_per_day': miles_per_day,
                'predicted': pred,
                'expected': exp,
                'error': error,
                'abs_error': abs(error),
                'percent_error': (error / exp * 100) if exp != 0 else 0,
                'duration_bucket': duration_bucket,
                'mileage_bucket': mileage_bucket
            })
            
        except Exception as e:
            print(f"Error processing case {i}: {e}")
    
    return pd.DataFrame(results)

def get_duration_bucket(days):
    """Create duration buckets"""
    if days <= 2:
        return "1-2 days"
    elif days <= 3:
        return "3 days"
    elif days <= 5:
        return "4-5 days"
    elif days <= 7:
        return "6-7 days"
    elif days <= 10:
        return "8-10 days"
    elif days <= 14:
        return "11-14 days"
    else:
        return "15+ days"

def get_mileage_bucket(miles_per_day):
    """Create mileage per day buckets"""
    if miles_per_day < 50:
        return "< 50 mi/day"
    elif miles_per_day < 100:
        return "50-99 mi/day"
    elif miles_per_day < 150:
        return "100-149 mi/day"
    elif miles_per_day < 200:
        return "150-199 mi/day"
    elif miles_per_day < 250:
        return "200-249 mi/day"
    elif miles_per_day < 300:
        return "250-299 mi/day"
    else:
        return "300+ mi/day"

def plot_bucketed_analysis(df):
    """Create comprehensive bucketed analysis plots"""
    
    # Set up the figure with subplots
    fig = plt.figure(figsize=(20, 16))
    
    # 1. Error distribution by trip duration buckets
    plt.subplot(3, 3, 1)
    duration_buckets = ["1-2 days", "3 days", "4-5 days", "6-7 days", "8-10 days", "11-14 days", "15+ days"]
    duration_errors = [df[df['duration_bucket'] == bucket]['error'].values for bucket in duration_buckets if len(df[df['duration_bucket'] == bucket]) > 0]
    duration_labels = [bucket for bucket in duration_buckets if len(df[df['duration_bucket'] == bucket]) > 0]
    
    plt.boxplot(duration_errors, labels=duration_labels)
    plt.title('Error Distribution by Trip Duration')
    plt.ylabel('Prediction Error ($)')
    plt.xticks(rotation=45)
    plt.grid(True, alpha=0.3)
    
    # 2. Error distribution by mileage buckets
    plt.subplot(3, 3, 2)
    mileage_buckets = ["< 50 mi/day", "50-99 mi/day", "100-149 mi/day", "150-199 mi/day", 
                      "200-249 mi/day", "250-299 mi/day", "300+ mi/day"]
    mileage_errors = [df[df['mileage_bucket'] == bucket]['error'].values for bucket in mileage_buckets if len(df[df['mileage_bucket'] == bucket]) > 0]
    mileage_labels = [bucket for bucket in mileage_buckets if len(df[df['mileage_bucket'] == bucket]) > 0]
    
    plt.boxplot(mileage_errors, labels=mileage_labels)
    plt.title('Error Distribution by Mileage per Day')
    plt.ylabel('Prediction Error ($)')
    plt.xticks(rotation=45)
    plt.grid(True, alpha=0.3)
    
    # 3. Mean error by duration bucket
    plt.subplot(3, 3, 3)
    duration_stats = df.groupby('duration_bucket')['error'].agg(['mean', 'count', 'std']).reset_index()
    duration_stats = duration_stats.sort_values('count', ascending=False)
    
    bars = plt.bar(range(len(duration_stats)), duration_stats['mean'], 
                   color=['red' if x > 0 else 'blue' for x in duration_stats['mean']])
    plt.title('Mean Error by Trip Duration')
    plt.ylabel('Mean Error ($)')
    plt.xlabel('Trip Duration Bucket')
    plt.xticks(range(len(duration_stats)), duration_stats['duration_bucket'], rotation=45)
    plt.grid(True, alpha=0.3)
    plt.axhline(y=0, color='black', linestyle='-', alpha=0.5)
    
    # Add count labels on bars
    for i, (bar, count) in enumerate(zip(bars, duration_stats['count'])):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + (5 if bar.get_height() >= 0 else -15), 
                f'n={count}', ha='center', va='bottom' if bar.get_height() >= 0 else 'top', fontsize=8)
    
    # 4. Mean error by mileage bucket
    plt.subplot(3, 3, 4)
    mileage_stats = df.groupby('mileage_bucket')['error'].agg(['mean', 'count', 'std']).reset_index()
    # Sort by logical order
    mileage_order = ["< 50 mi/day", "50-99 mi/day", "100-149 mi/day", "150-199 mi/day", 
                    "200-249 mi/day", "250-299 mi/day", "300+ mi/day"]
    mileage_stats['order'] = mileage_stats['mileage_bucket'].map({bucket: i for i, bucket in enumerate(mileage_order)})
    mileage_stats = mileage_stats.sort_values('order')
    
    bars = plt.bar(range(len(mileage_stats)), mileage_stats['mean'],
                   color=['red' if x > 0 else 'blue' for x in mileage_stats['mean']])
    plt.title('Mean Error by Mileage per Day')
    plt.ylabel('Mean Error ($)')
    plt.xlabel('Mileage per Day Bucket')
    plt.xticks(range(len(mileage_stats)), mileage_stats['mileage_bucket'], rotation=45)
    plt.grid(True, alpha=0.3)
    plt.axhline(y=0, color='black', linestyle='-', alpha=0.5)
    
    # Add count labels on bars
    for i, (bar, count) in enumerate(zip(bars, mileage_stats['count'])):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + (5 if bar.get_height() >= 0 else -15), 
                f'n={count}', ha='center', va='bottom' if bar.get_height() >= 0 else 'top', fontsize=8)
    
    # 5. Scatter plot: Expected vs Predicted by Duration
    plt.subplot(3, 3, 5)
    duration_colors = plt.cm.tab10(np.linspace(0, 1, len(duration_stats)))
    for i, bucket in enumerate(duration_stats['duration_bucket']):
        subset = df[df['duration_bucket'] == bucket]
        plt.scatter(subset['expected'], subset['predicted'], 
                   alpha=0.6, label=f"{bucket} (n={len(subset)})", 
                   color=duration_colors[i], s=20)
    
    # Perfect prediction line
    min_val = min(df['expected'].min(), df['predicted'].min())
    max_val = max(df['expected'].max(), df['predicted'].max())
    plt.plot([min_val, max_val], [min_val, max_val], 'k--', alpha=0.5, label='Perfect Prediction')
    
    plt.xlabel('Expected Reimbursement ($)')
    plt.ylabel('Predicted Reimbursement ($)')
    plt.title('Expected vs Predicted by Duration')
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(True, alpha=0.3)
    
    # 6. Scatter plot: Expected vs Predicted by Mileage
    plt.subplot(3, 3, 6)
    mileage_colors = plt.cm.viridis(np.linspace(0, 1, len(mileage_stats)))
    for i, bucket in enumerate(mileage_stats['mileage_bucket']):
        subset = df[df['mileage_bucket'] == bucket]
        plt.scatter(subset['expected'], subset['predicted'], 
                   alpha=0.6, label=f"{bucket} (n={len(subset)})", 
                   color=mileage_colors[i], s=20)
    
    plt.plot([min_val, max_val], [min_val, max_val], 'k--', alpha=0.5, label='Perfect Prediction')
    plt.xlabel('Expected Reimbursement ($)')
    plt.ylabel('Predicted Reimbursement ($)')
    plt.title('Expected vs Predicted by Mileage/Day')
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(True, alpha=0.3)
    
    # 7. Absolute error heatmap by duration and mileage
    plt.subplot(3, 3, 7)
    pivot_table = df.groupby(['duration_bucket', 'mileage_bucket'])['abs_error'].mean().unstack(fill_value=0)
    
    # Reorder for logical progression
    if len(pivot_table) > 0:
        duration_order = ["1-2 days", "3 days", "4-5 days", "6-7 days", "8-10 days", "11-14 days", "15+ days"]
        duration_order = [d for d in duration_order if d in pivot_table.index]
        pivot_table = pivot_table.reindex(duration_order)
        
        im = plt.imshow(pivot_table.values, cmap='Reds', aspect='auto')
        plt.colorbar(im, label='Mean Absolute Error ($)')
        plt.yticks(range(len(pivot_table.index)), pivot_table.index)
        plt.xticks(range(len(pivot_table.columns)), pivot_table.columns, rotation=45)
        plt.title('Mean Absolute Error Heatmap')
        plt.xlabel('Mileage per Day Bucket')
        plt.ylabel('Trip Duration Bucket')
    
    # 8. Count heatmap by duration and mileage
    plt.subplot(3, 3, 8)
    count_pivot = df.groupby(['duration_bucket', 'mileage_bucket']).size().unstack(fill_value=0)
    if len(count_pivot) > 0:
        count_pivot = count_pivot.reindex(duration_order)
        
        im = plt.imshow(count_pivot.values, cmap='Blues', aspect='auto')
        plt.colorbar(im, label='Number of Cases')
        plt.yticks(range(len(count_pivot.index)), count_pivot.index)
        plt.xticks(range(len(count_pivot.columns)), count_pivot.columns, rotation=45)
        plt.title('Case Count Heatmap')
        plt.xlabel('Mileage per Day Bucket')
        plt.ylabel('Trip Duration Bucket')
    
    # 9. Summary statistics table
    plt.subplot(3, 3, 9)
    plt.axis('off')
    
    # Overall statistics
    overall_stats = f"""
    OVERALL STATISTICS
    
    Total Cases: {len(df):,}
    Mean Error: ${df['error'].mean():.2f}
    Std Error: ${df['error'].std():.2f}
    Mean Abs Error: ${df['abs_error'].mean():.2f}
    
    Correlation: {df['expected'].corr(df['predicted']):.3f}
    
    TOP ERROR BUCKETS:
    Duration: {duration_stats.loc[duration_stats['mean'].abs().idxmax(), 'duration_bucket']}
    (Mean Error: ${duration_stats.loc[duration_stats['mean'].abs().idxmax(), 'mean']:.2f})
    
    Mileage: {mileage_stats.loc[mileage_stats['mean'].abs().idxmax(), 'mileage_bucket']}
    (Mean Error: ${mileage_stats.loc[mileage_stats['mean'].abs().idxmax(), 'mean']:.2f})
    """
    
    plt.text(0.1, 0.9, overall_stats, transform=plt.gca().transAxes, 
             fontsize=10, verticalalignment='top', fontfamily='monospace')
    
    plt.tight_layout()
    plt.savefig('bucketed_drift_analysis.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    return duration_stats, mileage_stats

def print_detailed_analysis(df, duration_stats, mileage_stats):
    """Print detailed statistical analysis"""
    
    print("\n" + "="*80)
    print("BUCKETED DRIFT ANALYSIS REPORT")
    print("="*80)
    
    print(f"\nOVERALL SUMMARY:")
    print(f"  Total test cases: {len(df):,}")
    print(f"  Mean prediction error: ${df['error'].mean():.2f}")
    print(f"  Standard deviation: ${df['error'].std():.2f}")
    print(f"  Mean absolute error: ${df['abs_error'].mean():.2f}")
    print(f"  Correlation (expected vs predicted): {df['expected'].corr(df['predicted']):.3f}")
    
    print(f"\nTRIP DURATION ANALYSIS:")
    print(f"{'Bucket':<15} {'Count':<8} {'Mean Error':<12} {'Std Error':<12} {'Mean |Error|':<12}")
    print("-" * 65)
    for _, row in duration_stats.iterrows():
        bucket_data = df[df['duration_bucket'] == row['duration_bucket']]
        print(f"{row['duration_bucket']:<15} {row['count']:<8} ${row['mean']:<11.2f} ${row['std']:<11.2f} ${bucket_data['abs_error'].mean():<11.2f}")
    
    print(f"\nMILEAGE PER DAY ANALYSIS:")
    print(f"{'Bucket':<15} {'Count':<8} {'Mean Error':<12} {'Std Error':<12} {'Mean |Error|':<12}")
    print("-" * 65)
    for _, row in mileage_stats.iterrows():
        bucket_data = df[df['mileage_bucket'] == row['mileage_bucket']]
        print(f"{row['mileage_bucket']:<15} {row['count']:<8} ${row['mean']:<11.2f} ${row['std']:<11.2f} ${bucket_data['abs_error'].mean():<11.2f}")
    
    # Identify problematic patterns
    print(f"\nPROBLEMATIC PATTERNS:")
    
    # Duration buckets with highest absolute mean error
    worst_duration = duration_stats.loc[duration_stats['mean'].abs().idxmax()]
    print(f"  Worst duration bucket: {worst_duration['duration_bucket']} (mean error: ${worst_duration['mean']:.2f})")
    
    # Mileage buckets with highest absolute mean error
    worst_mileage = mileage_stats.loc[mileage_stats['mean'].abs().idxmax()]
    print(f"  Worst mileage bucket: {worst_mileage['mileage_bucket']} (mean error: ${worst_mileage['mean']:.2f})")
    
    # Look for systematic over/under-prediction
    over_predict = df[df['error'] > 0]
    under_predict = df[df['error'] < 0]
    
    print(f"\nSYSTEMATIC BIAS ANALYSIS:")
    print(f"  Over-predictions: {len(over_predict)} cases ({len(over_predict)/len(df)*100:.1f}%)")
    print(f"  Under-predictions: {len(under_predict)} cases ({len(under_predict)/len(df)*100:.1f}%)")
    
    if len(over_predict) > 0:
        print(f"  Mean over-prediction: ${over_predict['error'].mean():.2f}")
    if len(under_predict) > 0:
        print(f"  Mean under-prediction: ${under_predict['error'].mean():.2f}")

def main():
    """Main execution function"""
    print("Loading data and calculating predictions...")
    df = load_and_process_data()
    
    print(f"Processed {len(df)} test cases successfully.")
    
    print("Generating bucketed analysis plots...")
    duration_stats, mileage_stats = plot_bucketed_analysis(df)
    
    print_detailed_analysis(df, duration_stats, mileage_stats)
    
    print(f"\nBucketed analysis complete! Check 'bucketed_drift_analysis.png' for visualizations.")

if __name__ == "__main__":
    main()
