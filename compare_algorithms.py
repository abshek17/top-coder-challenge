#!/usr/bin/env python3
"""
Compare refined algorithm against original legacy algorithm and expected results.
"""

import json
import sys
import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from legacy_calculate import calculate_legacy_reimbursement
    from refined_calculate import calculate_refined_reimbursement
except ImportError as e:
    print(f"Could not import algorithms: {e}")
    sys.exit(1)

def load_test_data():
    """Load test cases from public_cases.json"""
    with open('public_cases.json', 'r') as f:
        cases = json.load(f)
    return cases

def compare_algorithms():
    """Compare original vs refined algorithm performance"""
    cases = load_test_data()
    
    results = []
    
    for i, case in enumerate(cases):
        try:
            input_data = case.get('input', case)
            
            trip_days = input_data['trip_duration_days']
            miles = input_data['miles_traveled']
            receipts = input_data['total_receipts_amount']
            expected = case['expected_output']
            
            # Calculate with both algorithms
            original_pred = calculate_legacy_reimbursement(trip_days, miles, receipts)
            refined_pred = calculate_refined_reimbursement(trip_days, miles, receipts)
            
            # Calculate errors
            original_error = original_pred - expected
            refined_error = refined_pred - expected
            
            miles_per_day = miles / trip_days if trip_days > 0 else 0
            
            results.append({
                'case_id': i,
                'trip_days': trip_days,
                'miles': miles,
                'receipts': receipts,
                'miles_per_day': miles_per_day,
                'expected': expected,
                'original_pred': original_pred,
                'refined_pred': refined_pred,
                'original_error': original_error,
                'refined_error': refined_error,
                'original_abs_error': abs(original_error),
                'refined_abs_error': abs(refined_error),
                'improvement': abs(original_error) - abs(refined_error),  # Positive = better
                'duration_bucket': get_duration_bucket(trip_days),
                'mileage_bucket': get_mileage_bucket(miles_per_day)
            })
            
        except Exception as e:
            print(f"Error processing case {i}: {e}")
    
    return pd.DataFrame(results)

def get_duration_bucket(days):
    """Create duration buckets (same as bucketed analysis)"""
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
    """Create mileage per day buckets (same as bucketed analysis)"""
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

def analyze_improvements(df):
    """Analyze which areas improved most"""
    
    print("="*80)
    print("ALGORITHM COMPARISON REPORT")
    print("="*80)
    
    # Overall statistics
    print(f"\nOVERALL PERFORMANCE:")
    print(f"Total test cases: {len(df):,}")
    
    print(f"\nORIGINAL ALGORITHM:")
    print(f"  Mean error: ${df['original_error'].mean():.2f}")
    print(f"  Mean absolute error: ${df['original_abs_error'].mean():.2f}")
    print(f"  Correlation: {df['expected'].corr(df['original_pred']):.3f}")
    
    print(f"\nREFINED ALGORITHM:")
    print(f"  Mean error: ${df['refined_error'].mean():.2f}")
    print(f"  Mean absolute error: ${df['refined_abs_error'].mean():.2f}")
    print(f"  Correlation: {df['expected'].corr(df['refined_pred']):.3f}")
    
    print(f"\nIMPROVEMENT:")
    print(f"  Mean absolute error reduction: ${df['improvement'].mean():.2f}")
    print(f"  Cases improved: {len(df[df['improvement'] > 0]):,} ({len(df[df['improvement'] > 0])/len(df)*100:.1f}%)")
    print(f"  Cases worsened: {len(df[df['improvement'] < 0]):,} ({len(df[df['improvement'] < 0])/len(df)*100:.1f}%)")
    
    # Duration bucket improvements
    print(f"\nIMPROVEMENT BY DURATION BUCKET:")
    duration_improvements = df.groupby('duration_bucket')['improvement'].agg(['mean', 'count']).round(2)
    duration_improvements = duration_improvements.sort_values('mean', ascending=False)
    
    print(f"{'Bucket':<15} {'Avg Improvement':<15} {'Count':<8}")
    print("-" * 40)
    for bucket, row in duration_improvements.iterrows():
        print(f"{bucket:<15} ${row['mean']:<14.2f} {row['count']:<8}")
    
    # Mileage bucket improvements
    print(f"\nIMPROVEMENT BY MILEAGE BUCKET:")
    mileage_improvements = df.groupby('mileage_bucket')['improvement'].agg(['mean', 'count']).round(2)
    mileage_improvements = mileage_improvements.sort_values('mean', ascending=False)
    
    print(f"{'Bucket':<15} {'Avg Improvement':<15} {'Count':<8}")
    print("-" * 40)
    for bucket, row in mileage_improvements.iterrows():
        print(f"{bucket:<15} ${row['mean']:<14.2f} {row['count']:<8}")
    
    # Focus on previously problematic areas
    print(f"\nFOCUS ON PREVIOUSLY PROBLEMATIC AREAS:")
    
    # 6-7 day trips (worst duration bucket)
    weekend_trips = df[df['duration_bucket'] == '6-7 days']
    if len(weekend_trips) > 0:
        print(f"  6-7 day trips:")
        print(f"    Original mean error: ${weekend_trips['original_error'].mean():.2f}")
        print(f"    Refined mean error: ${weekend_trips['refined_error'].mean():.2f}")
        print(f"    Average improvement: ${weekend_trips['improvement'].mean():.2f}")
    
    # 200-249 mi/day (worst mileage bucket)
    high_mileage = df[df['mileage_bucket'] == '200-249 mi/day']
    if len(high_mileage) > 0:
        print(f"  200-249 mi/day trips:")
        print(f"    Original mean error: ${high_mileage['original_error'].mean():.2f}")
        print(f"    Refined mean error: ${high_mileage['refined_error'].mean():.2f}")
        print(f"    Average improvement: ${high_mileage['improvement'].mean():.2f}")
    
    # <50 mi/day (severe under-prediction)
    low_mileage = df[df['mileage_bucket'] == '< 50 mi/day']
    if len(low_mileage) > 0:
        print(f"  <50 mi/day trips:")
        print(f"    Original mean error: ${low_mileage['original_error'].mean():.2f}")
        print(f"    Refined mean error: ${low_mileage['refined_error'].mean():.2f}")
        print(f"    Average improvement: ${low_mileage['improvement'].mean():.2f}")
    
    # 11-14 day trips
    long_trips = df[df['duration_bucket'] == '11-14 days']
    if len(long_trips) > 0:
        print(f"  11-14 day trips:")
        print(f"    Original mean error: ${long_trips['original_error'].mean():.2f}")
        print(f"    Refined mean error: ${long_trips['refined_error'].mean():.2f}")
        print(f"    Average improvement: ${long_trips['improvement'].mean():.2f}")

def plot_comparison(df):
    """Create comparison plots"""
    
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    
    # 1. Error distribution comparison
    axes[0, 0].hist(df['original_error'], bins=50, alpha=0.7, label='Original', color='red')
    axes[0, 0].hist(df['refined_error'], bins=50, alpha=0.7, label='Refined', color='blue')
    axes[0, 0].set_xlabel('Prediction Error ($)')
    axes[0, 0].set_ylabel('Frequency')
    axes[0, 0].set_title('Error Distribution Comparison')
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)
    
    # 2. Absolute error comparison
    axes[0, 1].hist(df['original_abs_error'], bins=50, alpha=0.7, label='Original', color='red')
    axes[0, 1].hist(df['refined_abs_error'], bins=50, alpha=0.7, label='Refined', color='blue')
    axes[0, 1].set_xlabel('Absolute Error ($)')
    axes[0, 1].set_ylabel('Frequency')
    axes[0, 1].set_title('Absolute Error Distribution')
    axes[0, 1].legend()
    axes[0, 1].grid(True, alpha=0.3)
    
    # 3. Improvement scatter
    axes[0, 2].scatter(df['original_abs_error'], df['improvement'], alpha=0.6, s=20)
    axes[0, 2].set_xlabel('Original Absolute Error ($)')
    axes[0, 2].set_ylabel('Improvement ($)')
    axes[0, 2].set_title('Improvement vs Original Error')
    axes[0, 2].axhline(y=0, color='black', linestyle='--', alpha=0.5)
    axes[0, 2].grid(True, alpha=0.3)
    
    # 4. Expected vs Predicted comparison
    min_val = min(df['expected'].min(), df['original_pred'].min(), df['refined_pred'].min())
    max_val = max(df['expected'].max(), df['original_pred'].max(), df['refined_pred'].max())
    
    axes[1, 0].scatter(df['expected'], df['original_pred'], alpha=0.6, s=20, color='red', label='Original')
    axes[1, 0].plot([min_val, max_val], [min_val, max_val], 'k--', alpha=0.5)
    axes[1, 0].set_xlabel('Expected ($)')
    axes[1, 0].set_ylabel('Predicted ($)')
    axes[1, 0].set_title('Original: Expected vs Predicted')
    axes[1, 0].grid(True, alpha=0.3)
    
    axes[1, 1].scatter(df['expected'], df['refined_pred'], alpha=0.6, s=20, color='blue', label='Refined')
    axes[1, 1].plot([min_val, max_val], [min_val, max_val], 'k--', alpha=0.5)
    axes[1, 1].set_xlabel('Expected ($)')
    axes[1, 1].set_ylabel('Predicted ($)')
    axes[1, 1].set_title('Refined: Expected vs Predicted')
    axes[1, 1].grid(True, alpha=0.3)
    
    # 5. Improvement by error bucket
    df['error_bucket'] = pd.cut(df['original_abs_error'], bins=10)
    improvement_by_bucket = df.groupby('error_bucket')['improvement'].mean()
    
    axes[1, 2].bar(range(len(improvement_by_bucket)), improvement_by_bucket.values)
    axes[1, 2].set_xlabel('Original Error Bucket')
    axes[1, 2].set_ylabel('Mean Improvement ($)')
    axes[1, 2].set_title('Improvement by Error Bucket')
    axes[1, 2].tick_params(axis='x', rotation=45)
    axes[1, 2].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('algorithm_comparison.png', dpi=300, bbox_inches='tight')
    plt.show()

def main():
    """Main execution function"""
    print("Loading test data and comparing algorithms...")
    df = compare_algorithms()
    
    print(f"Processed {len(df)} test cases successfully.")
    
    analyze_improvements(df)
    
    print("\nGenerating comparison plots...")
    plot_comparison(df)
    
    print(f"\nComparison complete! Check 'algorithm_comparison.png' for visualizations.")
    
    return df

if __name__ == "__main__":
    df = main()
