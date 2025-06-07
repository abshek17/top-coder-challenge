#!/usr/bin/env python3
"""
Comprehensive visualization of results.json data.
Creates multiple plots to analyze prediction accuracy and patterns.
"""

import json
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from collections import defaultdict
import pandas as pd

def load_results():
    """Load results from JSON file."""
    with open('results.json', 'r') as f:
        data = json.load(f)
    return data

def create_comprehensive_visualizations(data):
    """Create a comprehensive set of visualizations."""
    
    # Extract raw results
    results = data['raw_results']
    summary = data['summary_statistics']
    
    # Convert to DataFrame for easier analysis
    df = pd.DataFrame(results)
    
    # Set up the plotting style
    plt.style.use('default')
    sns.set_palette("husl")
    
    # Create a large figure with multiple subplots
    fig = plt.figure(figsize=(20, 16))
    
    # 1. Prediction vs Expected Scatter Plot (top left)
    ax1 = plt.subplot(3, 4, 1)
    scatter = ax1.scatter(df['expected_output'], df['actual_output'], 
                         alpha=0.6, c=df['absolute_error'], cmap='viridis', s=30)
    # Perfect prediction line
    min_val = min(df['expected_output'].min(), df['actual_output'].min())
    max_val = max(df['expected_output'].max(), df['actual_output'].max())
    ax1.plot([min_val, max_val], [min_val, max_val], 'r--', alpha=0.8, linewidth=2)
    ax1.set_xlabel('Expected Output ($)')
    ax1.set_ylabel('Actual Output ($)')
    ax1.set_title(f'Prediction Accuracy\n(r = {summary["correlation_coefficient"]:.4f})')
    ax1.grid(True, alpha=0.3)
    plt.colorbar(scatter, ax=ax1, label='Absolute Error ($)')
    
    # 2. Error Distribution Histogram (top center-left)
    ax2 = plt.subplot(3, 4, 2)
    ax2.hist(df['error'], bins=50, alpha=0.7, color='skyblue', edgecolor='black')
    ax2.axvline(0, color='red', linestyle='--', linewidth=2, label='Perfect Prediction')
    ax2.axvline(df['error'].mean(), color='orange', linestyle='-', linewidth=2, 
                label=f'Mean Error: ${df["error"].mean():.2f}')
    ax2.set_xlabel('Prediction Error ($)')
    ax2.set_ylabel('Frequency')
    ax2.set_title('Error Distribution')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # 3. Absolute Error by Trip Duration (top center-right)
    ax3 = plt.subplot(3, 4, 3)
    duration_groups = df.groupby('trip_duration_days')['absolute_error'].agg(['mean', 'std', 'count'])
    duration_groups = duration_groups[duration_groups['count'] >= 5]  # Filter groups with enough samples
    ax3.errorbar(duration_groups.index, duration_groups['mean'], 
                yerr=duration_groups['std'], marker='o', capsize=5, capthick=2)
    ax3.set_xlabel('Trip Duration (days)')
    ax3.set_ylabel('Mean Absolute Error ($)')
    ax3.set_title('Error by Trip Duration')
    ax3.grid(True, alpha=0.3)
    
    # 4. Absolute Error by Miles per Day (top right)
    ax4 = plt.subplot(3, 4, 4)
    # Create mileage bins
    df['mileage_bin'] = pd.cut(df['miles_per_day'], 
                              bins=[0, 50, 100, 150, 200, 250, 300, np.inf], 
                              labels=['<50', '50-100', '100-150', '150-200', '200-250', '250-300', '300+'])
    mileage_groups = df.groupby('mileage_bin', observed=True)['absolute_error'].agg(['mean', 'std', 'count'])
    ax4.bar(range(len(mileage_groups)), mileage_groups['mean'], 
            yerr=mileage_groups['std'], capsize=5, alpha=0.7)
    ax4.set_xlabel('Miles per Day')
    ax4.set_ylabel('Mean Absolute Error ($)')
    ax4.set_title('Error by Mileage Range')
    ax4.set_xticks(range(len(mileage_groups)))
    ax4.set_xticklabels(mileage_groups.index, rotation=45)
    ax4.grid(True, alpha=0.3)
    
    # 5. Error vs Miles per Day Scatter (middle left)
    ax5 = plt.subplot(3, 4, 5)
    ax5.scatter(df['miles_per_day'], df['error'], alpha=0.6, s=30)
    ax5.axhline(0, color='red', linestyle='--', alpha=0.8)
    ax5.set_xlabel('Miles per Day')
    ax5.set_ylabel('Prediction Error ($)')
    ax5.set_title('Error vs Daily Mileage')
    ax5.grid(True, alpha=0.3)
    
    # 6. Error vs Trip Duration Scatter (middle center-left)
    ax6 = plt.subplot(3, 4, 6)
    ax6.scatter(df['trip_duration_days'], df['error'], alpha=0.6, s=30)
    ax6.axhline(0, color='red', linestyle='--', alpha=0.8)
    ax6.set_xlabel('Trip Duration (days)')
    ax6.set_ylabel('Prediction Error ($)')
    ax6.set_title('Error vs Trip Duration')
    ax6.grid(True, alpha=0.3)
    
    # 7. Receipts per Day vs Error (middle center-right)
    ax7 = plt.subplot(3, 4, 7)
    ax7.scatter(df['receipts_per_day'], df['error'], alpha=0.6, s=30)
    ax7.axhline(0, color='red', linestyle='--', alpha=0.8)
    ax7.set_xlabel('Receipts per Day ($)')
    ax7.set_ylabel('Prediction Error ($)')
    ax7.set_title('Error vs Daily Receipts')
    ax7.grid(True, alpha=0.3)
    
    # 8. Percentage Error Distribution (middle right)
    ax8 = plt.subplot(3, 4, 8)
    ax8.hist(df['percentage_error'], bins=50, alpha=0.7, color='lightcoral', edgecolor='black')
    ax8.axvline(0, color='red', linestyle='--', linewidth=2, label='Perfect Prediction')
    ax8.axvline(df['percentage_error'].mean(), color='orange', linestyle='-', linewidth=2,
                label=f'Mean: {df["percentage_error"].mean():.1f}%')
    ax8.set_xlabel('Percentage Error (%)')
    ax8.set_ylabel('Frequency')
    ax8.set_title('Percentage Error Distribution')
    ax8.legend()
    ax8.grid(True, alpha=0.3)
    
    # 9. Heatmap of Error by Duration and Mileage Bins (bottom left, spanning 2 columns)
    ax9 = plt.subplot(3, 4, (9, 10))
    # Create duration bins
    df['duration_bin'] = pd.cut(df['trip_duration_days'], 
                               bins=[0, 3, 5, 7, 10, 15, np.inf],
                               labels=['1-3', '4-5', '6-7', '8-10', '11-15', '15+'])
    
    # Create pivot table for heatmap
    heatmap_data = df.pivot_table(values='error', 
                                 index='duration_bin', 
                                 columns='mileage_bin', 
                                 aggfunc='mean',
                                 observed=True)
    
    sns.heatmap(heatmap_data, annot=True, fmt='.0f', cmap='RdBu_r', center=0,
                ax=ax9, cbar_kws={'label': 'Mean Error ($)'})
    ax9.set_title('Mean Error Heatmap: Duration vs Mileage')
    ax9.set_xlabel('Miles per Day')
    ax9.set_ylabel('Trip Duration (days)')
    
    # 10. Top Problematic Cases (bottom center-right)
    ax10 = plt.subplot(3, 4, 11)
    # Get top 20 highest absolute errors
    top_errors = df.nlargest(20, 'absolute_error')
    bars = ax10.bar(range(len(top_errors)), top_errors['absolute_error'], 
                   color=['red' if x < 0 else 'blue' for x in top_errors['error']])
    ax10.set_xlabel('Case Rank (by Absolute Error)')
    ax10.set_ylabel('Absolute Error ($)')
    ax10.set_title('Top 20 Problematic Cases')
    ax10.grid(True, alpha=0.3)
    
    # 11. Summary Statistics Box (bottom right)
    ax11 = plt.subplot(3, 4, 12)
    ax11.axis('off')
    
    # Create summary text
    summary_text = f"""
ALGORITHM PERFORMANCE SUMMARY

Total Cases: {data['metadata']['total_cases']:,}
Mean Absolute Error: ${summary['mean_absolute_error']:.2f}
Correlation: {summary['correlation_coefficient']:.4f}

PREDICTION DISTRIBUTION:
Under-predicted: {summary['under_predicted_cases']} ({summary['under_prediction_rate']:.1f}%)
Over-predicted: {summary['over_predicted_cases']} ({summary['over_prediction_rate']:.1f}%)

ERROR STATISTICS:
Mean Error: ${df['error'].mean():.2f}
Median Error: ${df['error'].median():.2f}
Std Dev: ${df['error'].std():.2f}
Min Error: ${df['error'].min():.2f}
Max Error: ${df['error'].max():.2f}

EXTREME CASES:
Worst Under-prediction: ${df['error'].min():.2f}
Worst Over-prediction: ${df['error'].max():.2f}
Cases within ±$50: {len(df[df['absolute_error'] <= 50])} ({len(df[df['absolute_error'] <= 50])/len(df)*100:.1f}%)
Cases within ±$100: {len(df[df['absolute_error'] <= 100])} ({len(df[df['absolute_error'] <= 100])/len(df)*100:.1f}%)
"""
    
    ax11.text(0.05, 0.95, summary_text, transform=ax11.transAxes, fontsize=10,
              verticalalignment='top', fontfamily='monospace',
              bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.8))
    
    # Adjust layout and save
    plt.tight_layout()
    plt.suptitle('Legacy Reimbursement Algorithm - Comprehensive Results Analysis', 
                 fontsize=16, fontweight='bold', y=0.98)
    
    # Save the plot
    plt.savefig('comprehensive_results_analysis.png', dpi=300, bbox_inches='tight')
    print("Comprehensive visualization saved as 'comprehensive_results_analysis.png'")
    
    return fig

def create_error_pattern_analysis(data):
    """Create focused analysis of error patterns."""
    results = data['raw_results']
    df = pd.DataFrame(results)
    
    # Create a focused figure for error patterns
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    
    # 1. Box plot of errors by trip duration
    ax1 = axes[0, 0]
    duration_data = [df[df['trip_duration_days'] == d]['error'].values 
                    for d in sorted(df['trip_duration_days'].unique())[:15]]  # Top 15 durations
    duration_labels = sorted(df['trip_duration_days'].unique())[:15]
    ax1.boxplot(duration_data, labels=duration_labels)
    ax1.set_xlabel('Trip Duration (days)')
    ax1.set_ylabel('Prediction Error ($)')
    ax1.set_title('Error Distribution by Trip Duration')
    ax1.grid(True, alpha=0.3)
    ax1.tick_params(axis='x', rotation=45)
    
    # 2. Violin plot of errors by mileage bins
    ax2 = axes[0, 1]
    df['mileage_bin'] = pd.cut(df['miles_per_day'], 
                              bins=[0, 50, 100, 150, 200, 250, 300, np.inf], 
                              labels=['<50', '50-100', '100-150', '150-200', '200-250', '250-300', '300+'])
    
    # Filter out bins with too few samples for violin plot
    valid_bins = df['mileage_bin'].value_counts()
    valid_bins = valid_bins[valid_bins >= 10].index
    df_filtered = df[df['mileage_bin'].isin(valid_bins)]
    
    sns.violinplot(data=df_filtered, x='mileage_bin', y='error', ax=ax2)
    ax2.set_xlabel('Miles per Day')
    ax2.set_ylabel('Prediction Error ($)')
    ax2.set_title('Error Distribution by Mileage Range')
    ax2.tick_params(axis='x', rotation=45)
    ax2.grid(True, alpha=0.3)
    
    # 3. Cumulative error plot
    ax3 = axes[0, 2]
    sorted_errors = np.sort(df['absolute_error'])
    cumulative_pct = np.arange(1, len(sorted_errors) + 1) / len(sorted_errors) * 100
    ax3.plot(sorted_errors, cumulative_pct, linewidth=2)
    ax3.axvline(50, color='red', linestyle='--', label='$50 threshold')
    ax3.axvline(100, color='orange', linestyle='--', label='$100 threshold')
    ax3.axvline(200, color='purple', linestyle='--', label='$200 threshold')
    ax3.set_xlabel('Absolute Error ($)')
    ax3.set_ylabel('Cumulative Percentage (%)')
    ax3.set_title('Cumulative Error Distribution')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # 4. Error vs Total Reimbursement Amount
    ax4 = axes[1, 0]
    ax4.scatter(df['expected_output'], df['error'], alpha=0.6, s=30)
    ax4.axhline(0, color='red', linestyle='--', alpha=0.8)
    ax4.set_xlabel('Expected Reimbursement ($)')
    ax4.set_ylabel('Prediction Error ($)')
    ax4.set_title('Error vs Reimbursement Amount')
    ax4.grid(True, alpha=0.3)
    
    # 5. Prediction accuracy by percentile
    ax5 = axes[1, 1]
    # Divide into percentile buckets
    df['expected_percentile'] = pd.qcut(df['expected_output'], q=10, labels=False)
    percentile_stats = df.groupby('expected_percentile')['absolute_error'].agg(['mean', 'std', 'count'])
    ax5.errorbar(range(len(percentile_stats)), percentile_stats['mean'], 
                yerr=percentile_stats['std'], marker='o', capsize=5, capthick=2)
    ax5.set_xlabel('Expected Output Percentile (0-9)')
    ax5.set_ylabel('Mean Absolute Error ($)')
    ax5.set_title('Error by Reimbursement Amount Percentile')
    ax5.grid(True, alpha=0.3)
    
    # 6. Over/Under prediction analysis
    ax6 = axes[1, 2]
    over_under_by_duration = df.groupby('trip_duration_days').agg({
        'under_predicted': 'sum',
        'over_predicted': 'sum',
        'case_id': 'count'
    }).head(15)  # Top 15 durations
    
    width = 0.35
    x = np.arange(len(over_under_by_duration))
    ax6.bar(x - width/2, over_under_by_duration['under_predicted'], width, 
           label='Under-predicted', alpha=0.8)
    ax6.bar(x + width/2, over_under_by_duration['over_predicted'], width, 
           label='Over-predicted', alpha=0.8)
    ax6.set_xlabel('Trip Duration (days)')
    ax6.set_ylabel('Number of Cases')
    ax6.set_title('Over/Under Prediction by Duration')
    ax6.set_xticks(x)
    ax6.set_xticklabels(over_under_by_duration.index)
    ax6.legend()
    ax6.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.suptitle('Detailed Error Pattern Analysis', fontsize=16, fontweight='bold', y=0.98)
    plt.savefig('error_pattern_analysis.png', dpi=300, bbox_inches='tight')
    print("Error pattern analysis saved as 'error_pattern_analysis.png'")
    
    return fig

def print_detailed_statistics(data):
    """Print detailed statistics about the results."""
    results = data['raw_results']
    df = pd.DataFrame(results)
    
    print("\n" + "="*60)
    print("DETAILED ANALYSIS RESULTS")
    print("="*60)
    
    print(f"\n📊 OVERALL PERFORMANCE:")
    print(f"   Total Cases Analyzed: {len(df):,}")
    print(f"   Mean Absolute Error: ${df['absolute_error'].mean():.2f}")
    print(f"   Median Absolute Error: ${df['absolute_error'].median():.2f}")
    print(f"   Correlation Coefficient: {data['summary_statistics']['correlation_coefficient']:.4f}")
    
    print(f"\n📈 ERROR DISTRIBUTION:")
    print(f"   Cases within ±$25: {len(df[df['absolute_error'] <= 25]):,} ({len(df[df['absolute_error'] <= 25])/len(df)*100:.1f}%)")
    print(f"   Cases within ±$50: {len(df[df['absolute_error'] <= 50]):,} ({len(df[df['absolute_error'] <= 50])/len(df)*100:.1f}%)")
    print(f"   Cases within ±$100: {len(df[df['absolute_error'] <= 100]):,} ({len(df[df['absolute_error'] <= 100])/len(df)*100:.1f}%)")
    print(f"   Cases with >$300 error: {len(df[df['absolute_error'] > 300]):,} ({len(df[df['absolute_error'] > 300])/len(df)*100:.1f}%)")
    
    print(f"\n🎯 PREDICTION BIAS:")
    print(f"   Under-predictions: {data['summary_statistics']['under_predicted_cases']:,} ({data['summary_statistics']['under_prediction_rate']:.1f}%)")
    print(f"   Over-predictions: {data['summary_statistics']['over_predicted_cases']:,} ({data['summary_statistics']['over_prediction_rate']:.1f}%)")
    print(f"   Mean Error (bias): ${df['error'].mean():.2f}")
    
    print(f"\n🔍 WORST PERFORMING SEGMENTS:")
    
    # Duration analysis
    duration_errors = df.groupby('trip_duration_days')['error'].agg(['mean', 'count']).sort_values('mean')
    duration_errors = duration_errors[duration_errors['count'] >= 5]  # Filter reliable samples
    print(f"\n   Trip Duration (worst 3):")
    for duration, stats in duration_errors.head(3).iterrows():
        print(f"      {duration} days: ${stats['mean']:.2f} mean error ({stats['count']} cases)")
    
    # Mileage analysis
    df['mileage_bin'] = pd.cut(df['miles_per_day'], 
                              bins=[0, 50, 100, 150, 200, 250, 300, np.inf], 
                              labels=['<50', '50-100', '100-150', '150-200', '200-250', '250-300', '300+'])
    mileage_errors = df.groupby('mileage_bin', observed=True)['error'].agg(['mean', 'count']).sort_values('mean')
    print(f"\n   Mileage Range (worst 3):")
    for mileage, stats in mileage_errors.head(3).iterrows():
        print(f"      {mileage} mi/day: ${stats['mean']:.2f} mean error ({stats['count']} cases)")
    
    print(f"\n🏆 EXTREME CASES:")
    worst_under = df.loc[df['error'].idxmin()]
    worst_over = df.loc[df['error'].idxmax()]
    
    print(f"   Worst Under-prediction:")
    print(f"      Case #{worst_under['case_id']}: Expected ${worst_under['expected_output']:.2f}, Got ${worst_under['actual_output']:.2f}")
    print(f"      Trip: {worst_under['trip_duration_days']} days, {worst_under['miles_traveled']} miles, ${worst_under['total_receipts_amount']:.2f} receipts")
    print(f"      Error: ${worst_under['error']:.2f}")
    
    print(f"   Worst Over-prediction:")
    print(f"      Case #{worst_over['case_id']}: Expected ${worst_over['expected_output']:.2f}, Got ${worst_over['actual_output']:.2f}")
    print(f"      Trip: {worst_over['trip_duration_days']} days, {worst_over['miles_traveled']} miles, ${worst_over['total_receipts_amount']:.2f} receipts")
    print(f"      Error: ${worst_over['error']:.2f}")

def main():
    """Main execution function."""
    print("🎨 Creating comprehensive visualizations from results.json...")
    
    # Load the data
    data = load_results()
    
    # Create comprehensive visualizations
    print("\n📊 Generating comprehensive results analysis...")
    create_comprehensive_visualizations(data)
    
    # Create focused error pattern analysis
    print("\n🔍 Generating detailed error pattern analysis...")
    create_error_pattern_analysis(data)
    
    # Print detailed statistics
    print_detailed_statistics(data)
    
    print(f"\n✅ VISUALIZATION COMPLETE!")
    print(f"   Generated files:")
    print(f"   📈 comprehensive_results_analysis.png - 11-panel comprehensive analysis")
    print(f"   📊 error_pattern_analysis.png - 6-panel detailed error patterns")
    print(f"\n💡 These visualizations provide deep insights into:")
    print(f"   • Prediction accuracy and correlation patterns")
    print(f"   • Error distribution across different trip characteristics")  
    print(f"   • Problematic segments for targeted improvements")
    print(f"   • Performance benchmarks and outlier identification")

if __name__ == '__main__':
    main()
