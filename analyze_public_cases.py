#!/usr/bin/env python3
"""
Comprehensive Analysis of Public Test Cases
Analyzes the reimbursement patterns across multiple dimensions to understand the black box system.
"""

import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from legacy_calculate import calculate_legacy_reimbursement

def load_public_cases():
    """Load and process public test cases"""
    with open('public_cases.json', 'r') as f:
        cases = json.load(f)
    
    # Convert to DataFrame for easier analysis
    data = []
    for case in cases:
        inp = case['input']
        expected = case['expected_output']
        
        # Calculate derived metrics
        miles_per_day = inp['miles_traveled'] / inp['trip_duration_days'] if inp['trip_duration_days'] > 0 else 0
        receipts_per_day = inp['total_receipts_amount'] / inp['trip_duration_days'] if inp['trip_duration_days'] > 0 else 0
        
        # Get our algorithm prediction
        predicted = calculate_legacy_reimbursement(
            inp['trip_duration_days'], 
            inp['miles_traveled'], 
            inp['total_receipts_amount']
        )
        
        data.append({
            'trip_duration_days': inp['trip_duration_days'],
            'miles_traveled': inp['miles_traveled'],
            'total_receipts_amount': inp['total_receipts_amount'],
            'expected_output': expected,
            'predicted_output': predicted,
            'error': predicted - expected,
            'abs_error': abs(predicted - expected),
            'miles_per_day': miles_per_day,
            'receipts_per_day': receipts_per_day,
            # Categorical features for analysis
            'duration_category': categorize_duration(inp['trip_duration_days']),
            'mileage_category': categorize_mileage(miles_per_day),
            'receipt_category': categorize_receipts(receipts_per_day),
            'total_receipt_category': categorize_total_receipts(inp['total_receipts_amount'])
        })
    
    return pd.DataFrame(data)

def categorize_duration(days):
    """Categorize trip duration"""
    if days == 1:
        return "1 day"
    elif days in [2, 3]:
        return "2-3 days"
    elif days in [4, 5]:
        return "4-5 days"
    elif days in [6, 7]:
        return "6-7 days"
    elif days in [8, 9, 10]:
        return "8-10 days"
    else:
        return "11+ days"

def categorize_mileage(miles_per_day):
    """Categorize mileage efficiency"""
    if miles_per_day < 50:
        return "<50 mi/day"
    elif miles_per_day < 100:
        return "50-100 mi/day"
    elif miles_per_day < 150:
        return "100-150 mi/day"
    elif miles_per_day < 200:
        return "150-200 mi/day"
    elif miles_per_day < 300:
        return "200-300 mi/day"
    else:
        return "300+ mi/day"

def categorize_receipts(receipts_per_day):
    """Categorize daily receipt spending"""
    if receipts_per_day < 30:
        return "Very Low (<$30/day)"
    elif receipts_per_day < 75:
        return "Low ($30-75/day)"
    elif receipts_per_day < 150:
        return "Medium ($75-150/day)"
    elif receipts_per_day < 250:
        return "High ($150-250/day)"
    else:
        return "Very High (>$250/day)"

def categorize_total_receipts(total_receipts):
    """Categorize total receipt amounts"""
    if total_receipts < 50:
        return "Very Low (<$50)"
    elif total_receipts < 200:
        return "Low ($50-200)"
    elif total_receipts < 500:
        return "Medium ($200-500)"
    elif total_receipts < 1000:
        return "High ($500-1000)"
    else:
        return "Very High (>$1000)"

def create_comprehensive_analysis(df):
    """Create comprehensive visualizations"""
    
    # Set up the plotting style
    plt.style.use('default')
    sns.set_palette("husl")
    
    # Create a large figure with multiple subplots
    fig = plt.figure(figsize=(24, 20))
    
    # 1. Overall Performance Metrics
    ax1 = plt.subplot(4, 4, 1)
    correlation = np.corrcoef(df['expected_output'], df['predicted_output'])[0, 1]
    mae = df['abs_error'].mean()
    ax1.scatter(df['expected_output'], df['predicted_output'], alpha=0.6, s=20)
    ax1.plot([df['expected_output'].min(), df['expected_output'].max()], 
             [df['expected_output'].min(), df['expected_output'].max()], 'r--', alpha=0.8)
    ax1.set_xlabel('Expected Output ($)')
    ax1.set_ylabel('Predicted Output ($)')
    ax1.set_title(f'Overall Performance\nCorr: {correlation:.3f}, MAE: ${mae:.2f}')
    ax1.grid(True, alpha=0.3)
    
    # 2. Error Distribution
    ax2 = plt.subplot(4, 4, 2)
    ax2.hist(df['error'], bins=50, alpha=0.7, edgecolor='black')
    ax2.axvline(0, color='red', linestyle='--', alpha=0.8)
    ax2.set_xlabel('Error (Predicted - Expected) ($)')
    ax2.set_ylabel('Frequency')
    ax2.set_title('Error Distribution')
    ax2.grid(True, alpha=0.3)
    
    # 3. Error by Trip Duration
    ax3 = plt.subplot(4, 4, 3)
    duration_groups = df.groupby('duration_category')['error'].apply(list)
    duration_labels = list(duration_groups.index)
    duration_data = list(duration_groups.values)
    bp = ax3.boxplot(duration_data, labels=duration_labels, patch_artist=True)
    for patch in bp['boxes']:
        patch.set_facecolor('lightblue')
    ax3.axhline(0, color='red', linestyle='--', alpha=0.8)
    ax3.set_xlabel('Trip Duration')
    ax3.set_ylabel('Error ($)')
    ax3.set_title('Error by Trip Duration')
    ax3.tick_params(axis='x', rotation=45)
    ax3.grid(True, alpha=0.3)
    
    # 4. Error by Mileage Category
    ax4 = plt.subplot(4, 4, 4)
    mileage_groups = df.groupby('mileage_category')['error'].apply(list)
    mileage_labels = list(mileage_groups.index)
    mileage_data = list(mileage_groups.values)
    bp = ax4.boxplot(mileage_data, labels=mileage_labels, patch_artist=True)
    for patch in bp['boxes']:
        patch.set_facecolor('lightgreen')
    ax4.axhline(0, color='red', linestyle='--', alpha=0.8)
    ax4.set_xlabel('Miles per Day')
    ax4.set_ylabel('Error ($)')
    ax4.set_title('Error by Mileage Efficiency')
    ax4.tick_params(axis='x', rotation=45)
    ax4.grid(True, alpha=0.3)
    
    # 5. Error by Receipt Category
    ax5 = plt.subplot(4, 4, 5)
    receipt_groups = df.groupby('receipt_category')['error'].apply(list)
    receipt_labels = list(receipt_groups.index)
    receipt_data = list(receipt_groups.values)
    bp = ax5.boxplot(receipt_data, labels=receipt_labels, patch_artist=True)
    for patch in bp['boxes']:
        patch.set_facecolor('lightyellow')
    ax5.axhline(0, color='red', linestyle='--', alpha=0.8)
    ax5.set_xlabel('Receipts per Day')
    ax5.set_ylabel('Error ($)')
    ax5.set_title('Error by Daily Receipt Spending')
    ax5.tick_params(axis='x', rotation=45)
    ax5.grid(True, alpha=0.3)
    
    # 6. Absolute Error by Trip Duration
    ax6 = plt.subplot(4, 4, 6)
    duration_summary = df.groupby('duration_category').agg({
        'abs_error': ['mean', 'count']
    }).round(2)
    duration_summary.columns = ['Mean_MAE', 'Count']
    duration_summary = duration_summary.reset_index()
    
    bars = ax6.bar(duration_summary['duration_category'], duration_summary['Mean_MAE'], 
                   alpha=0.7, color='skyblue', edgecolor='black')
    ax6.set_xlabel('Trip Duration')
    ax6.set_ylabel('Mean Absolute Error ($)')
    ax6.set_title('MAE by Trip Duration')
    ax6.tick_params(axis='x', rotation=45)
    ax6.grid(True, alpha=0.3)
    
    # Add count labels on bars
    for bar, count in zip(bars, duration_summary['Count']):
        height = bar.get_height()
        ax6.text(bar.get_x() + bar.get_width()/2., height + 1,
                f'n={count}', ha='center', va='bottom', fontsize=8)
    
    # 7. Expected vs Predicted by Duration
    ax7 = plt.subplot(4, 4, 7)
    for duration in df['duration_category'].unique():
        subset = df[df['duration_category'] == duration]
        ax7.scatter(subset['expected_output'], subset['predicted_output'], 
                   label=duration, alpha=0.6, s=15)
    ax7.plot([df['expected_output'].min(), df['expected_output'].max()], 
             [df['expected_output'].min(), df['expected_output'].max()], 'r--', alpha=0.8)
    ax7.set_xlabel('Expected Output ($)')
    ax7.set_ylabel('Predicted Output ($)')
    ax7.set_title('Performance by Trip Duration')
    ax7.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=8)
    ax7.grid(True, alpha=0.3)
    
    # 8. Heatmap: Error by Duration vs Mileage
    ax8 = plt.subplot(4, 4, 8)
    pivot_table = df.pivot_table(values='error', 
                                index='duration_category', 
                                columns='mileage_category', 
                                aggfunc='mean')
    sns.heatmap(pivot_table, annot=True, fmt='.1f', cmap='RdBu_r', center=0, 
                ax=ax8, cbar_kws={'label': 'Mean Error ($)'})
    ax8.set_title('Mean Error Heatmap\n(Duration vs Mileage)')
    ax8.set_xlabel('Mileage Category')
    ax8.set_ylabel('Duration Category')
    
    # 9. Receipt Amount vs Expected Output
    ax9 = plt.subplot(4, 4, 9)
    scatter = ax9.scatter(df['total_receipts_amount'], df['expected_output'], 
                         c=df['trip_duration_days'], cmap='viridis', alpha=0.6, s=20)
    ax9.set_xlabel('Total Receipt Amount ($)')
    ax9.set_ylabel('Expected Output ($)')
    ax9.set_title('Expected Output vs Receipt Amount')
    ax9.grid(True, alpha=0.3)
    plt.colorbar(scatter, ax=ax9, label='Trip Duration (days)')
    
    # 10. Miles vs Expected Output
    ax10 = plt.subplot(4, 4, 10)
    scatter = ax10.scatter(df['miles_traveled'], df['expected_output'], 
                          c=df['trip_duration_days'], cmap='plasma', alpha=0.6, s=20)
    ax10.set_xlabel('Miles Traveled')
    ax10.set_ylabel('Expected Output ($)')
    ax10.set_title('Expected Output vs Miles Traveled')
    ax10.grid(True, alpha=0.3)
    plt.colorbar(scatter, ax=ax10, label='Trip Duration (days)')
    
    # 11. Error vs Miles per Day
    ax11 = plt.subplot(4, 4, 11)
    ax11.scatter(df['miles_per_day'], df['error'], alpha=0.6, s=20, color='orange')
    ax11.axhline(0, color='red', linestyle='--', alpha=0.8)
    ax11.set_xlabel('Miles per Day')
    ax11.set_ylabel('Error ($)')
    ax11.set_title('Error vs Mileage Efficiency')
    ax11.grid(True, alpha=0.3)
    
    # 12. Error vs Receipts per Day
    ax12 = plt.subplot(4, 4, 12)
    ax12.scatter(df['receipts_per_day'], df['error'], alpha=0.6, s=20, color='purple')
    ax12.axhline(0, color='red', linestyle='--', alpha=0.8)
    ax12.set_xlabel('Receipts per Day ($)')
    ax12.set_ylabel('Error ($)')
    ax12.set_title('Error vs Daily Receipt Spending')
    ax12.grid(True, alpha=0.3)
    
    # 13. Performance by Total Receipt Category
    ax13 = plt.subplot(4, 4, 13)
    receipt_summary = df.groupby('total_receipt_category').agg({
        'abs_error': ['mean', 'count']
    }).round(2)
    receipt_summary.columns = ['Mean_MAE', 'Count']
    receipt_summary = receipt_summary.reset_index()
    
    bars = ax13.bar(receipt_summary['total_receipt_category'], receipt_summary['Mean_MAE'], 
                    alpha=0.7, color='lightcoral', edgecolor='black')
    ax13.set_xlabel('Total Receipt Category')
    ax13.set_ylabel('Mean Absolute Error ($)')
    ax13.set_title('MAE by Total Receipt Amount')
    ax13.tick_params(axis='x', rotation=45)
    ax13.grid(True, alpha=0.3)
    
    # Add count labels on bars
    for bar, count in zip(bars, receipt_summary['Count']):
        height = bar.get_height()
        ax13.text(bar.get_x() + bar.get_width()/2., height + 1,
                 f'n={count}', ha='center', va='bottom', fontsize=8)
    
    # 14. 3D Relationship Plot
    ax14 = plt.subplot(4, 4, 14, projection='3d')
    scatter = ax14.scatter(df['trip_duration_days'], df['miles_traveled'], df['total_receipts_amount'],
                          c=df['expected_output'], cmap='coolwarm', alpha=0.6, s=20)
    ax14.set_xlabel('Trip Duration (days)')
    ax14.set_ylabel('Miles Traveled')
    ax14.set_zlabel('Receipt Amount ($)')
    ax14.set_title('3D Input Space\n(colored by expected output)')
    plt.colorbar(scatter, ax=ax14, label='Expected Output ($)', shrink=0.5)
    
    # 15. Bias Analysis
    ax15 = plt.subplot(4, 4, 15)
    under_predictions = (df['error'] < 0).sum()
    over_predictions = (df['error'] > 0).sum()
    exact_predictions = (df['error'] == 0).sum()
    
    labels = ['Under-predictions', 'Over-predictions', 'Exact']
    counts = [under_predictions, over_predictions, exact_predictions]
    colors = ['red', 'blue', 'green']
    
    wedges, texts, autotexts = ax15.pie(counts, labels=labels, colors=colors, autopct='%1.1f%%')
    ax15.set_title(f'Prediction Bias Distribution\n(Total: {len(df)} cases)')
    
    # 16. Extreme Cases Analysis
    ax16 = plt.subplot(4, 4, 16)
    # Find top 10 worst cases in each direction
    worst_under = df.nsmallest(10, 'error')
    worst_over = df.nlargest(10, 'error')
    
    ax16.scatter(worst_under['expected_output'], worst_under['predicted_output'], 
                color='red', s=50, alpha=0.7, label='Worst Under-predictions')
    ax16.scatter(worst_over['expected_output'], worst_over['predicted_output'], 
                color='blue', s=50, alpha=0.7, label='Worst Over-predictions')
    ax16.plot([df['expected_output'].min(), df['expected_output'].max()], 
             [df['expected_output'].min(), df['expected_output'].max()], 'black', alpha=0.8)
    ax16.set_xlabel('Expected Output ($)')
    ax16.set_ylabel('Predicted Output ($)')
    ax16.set_title('Extreme Error Cases')
    ax16.legend()
    ax16.grid(True, alpha=0.3)
    
    plt.tight_layout()
    return fig

def print_summary_statistics(df):
    """Print detailed summary statistics"""
    print("=" * 80)
    print("PUBLIC CASES COMPREHENSIVE ANALYSIS")
    print("=" * 80)
    
    # Overall Performance
    correlation = np.corrcoef(df['expected_output'], df['predicted_output'])[0, 1]
    mae = df['abs_error'].mean()
    median_ae = df['abs_error'].median()
    rmse = np.sqrt((df['error'] ** 2).mean())
    
    print(f"\n📊 OVERALL PERFORMANCE:")
    print(f"   Total Cases: {len(df):,}")
    print(f"   Mean Absolute Error: ${mae:.2f}")
    print(f"   Median Absolute Error: ${median_ae:.2f}")
    print(f"   Root Mean Square Error: ${rmse:.2f}")
    print(f"   Correlation Coefficient: {correlation:.4f}")
    
    # Bias Analysis
    under_predictions = (df['error'] < 0).sum()
    over_predictions = (df['error'] > 0).sum()
    exact_predictions = (df['error'] == 0).sum()
    mean_bias = df['error'].mean()
    
    print(f"\n🎯 PREDICTION BIAS:")
    print(f"   Under-predictions: {under_predictions} ({under_predictions/len(df)*100:.1f}%)")
    print(f"   Over-predictions: {over_predictions} ({over_predictions/len(df)*100:.1f}%)")
    print(f"   Exact predictions: {exact_predictions} ({exact_predictions/len(df)*100:.1f}%)")
    print(f"   Mean Error (bias): ${mean_bias:.2f}")
    
    # Accuracy Brackets
    within_25 = (df['abs_error'] <= 25).sum()
    within_50 = (df['abs_error'] <= 50).sum()
    within_100 = (df['abs_error'] <= 100).sum()
    over_300 = (df['abs_error'] > 300).sum()
    
    print(f"\n📈 ACCURACY BRACKETS:")
    print(f"   Cases within ±$25: {within_25} ({within_25/len(df)*100:.1f}%)")
    print(f"   Cases within ±$50: {within_50} ({within_50/len(df)*100:.1f}%)")
    print(f"   Cases within ±$100: {within_100} ({within_100/len(df)*100:.1f}%)")
    print(f"   Cases with >$300 error: {over_300} ({over_300/len(df)*100:.1f}%)")
    
    # Performance by Category
    print(f"\n🔍 PERFORMANCE BY TRIP DURATION:")
    duration_stats = df.groupby('duration_category').agg({
        'abs_error': ['mean', 'count'],
        'error': 'mean'
    }).round(2)
    duration_stats.columns = ['MAE', 'Count', 'Mean_Error']
    for idx, row in duration_stats.iterrows():
        print(f"   {idx}: MAE=${row['MAE']:.2f}, Bias=${row['Mean_Error']:.2f} ({row['Count']} cases)")
    
    print(f"\n🛣️ PERFORMANCE BY MILEAGE EFFICIENCY:")
    mileage_stats = df.groupby('mileage_category').agg({
        'abs_error': ['mean', 'count'],
        'error': 'mean'
    }).round(2)
    mileage_stats.columns = ['MAE', 'Count', 'Mean_Error']
    for idx, row in mileage_stats.iterrows():
        print(f"   {idx}: MAE=${row['MAE']:.2f}, Bias=${row['Mean_Error']:.2f} ({row['Count']} cases)")
    
    print(f"\n💰 PERFORMANCE BY RECEIPT SPENDING:")
    receipt_stats = df.groupby('receipt_category').agg({
        'abs_error': ['mean', 'count'],
        'error': 'mean'
    }).round(2)
    receipt_stats.columns = ['MAE', 'Count', 'Mean_Error']
    for idx, row in receipt_stats.iterrows():
        print(f"   {idx}: MAE=${row['MAE']:.2f}, Bias=${row['Mean_Error']:.2f} ({row['Count']} cases)")
    
    # Extreme Cases
    worst_under = df.nsmallest(3, 'error')
    worst_over = df.nlargest(3, 'error')
    
    print(f"\n🚨 WORST UNDER-PREDICTIONS:")
    for idx, row in worst_under.iterrows():
        print(f"   Expected: ${row['expected_output']:.2f}, Got: ${row['predicted_output']:.2f}, Error: ${row['error']:.2f}")
        print(f"   Trip: {row['trip_duration_days']} days, {row['miles_traveled']} miles, ${row['total_receipts_amount']:.2f} receipts")
        print()
    
    print(f"🚨 WORST OVER-PREDICTIONS:")
    for idx, row in worst_over.iterrows():
        print(f"   Expected: ${row['expected_output']:.2f}, Got: ${row['predicted_output']:.2f}, Error: ${row['error']:.2f}")
        print(f"   Trip: {row['trip_duration_days']} days, {row['miles_traveled']} miles, ${row['total_receipts_amount']:.2f} receipts")
        print()

def main():
    """Main analysis function"""
    print("Loading and analyzing public cases...")
    
    # Load data
    df = load_public_cases()
    
    # Print summary statistics
    print_summary_statistics(df)
    
    # Create comprehensive visualizations
    print("\n🎨 Creating comprehensive visualizations...")
    fig = create_comprehensive_analysis(df)
    
    # Save the plot
    plt.savefig('public_cases_comprehensive_analysis.png', dpi=300, bbox_inches='tight')
    print("📊 Comprehensive analysis saved as 'public_cases_comprehensive_analysis.png'")
    
    # Save the processed data for further analysis
    df.to_csv('public_cases_analysis.csv', index=False)
    print("💾 Detailed data saved as 'public_cases_analysis.csv'")
    
    print("\n✅ PUBLIC CASES ANALYSIS COMPLETE!")
    print("Generated files:")
    print("📈 public_cases_comprehensive_analysis.png - 16-panel comprehensive analysis")
    print("📊 public_cases_analysis.csv - Detailed processed data with all metrics")

if __name__ == "__main__":
    main()
