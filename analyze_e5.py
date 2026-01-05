"""
E5 Analysis: Generate figures and tables for KICS Winter 2026 paper

Analyzes audit log query performance results and generates LaTeX-ready
figures and tables.

Author: ClaimGuard Team
Date: January 2026
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
import os

# Use non-interactive backend
matplotlib.use('Agg')

# Set style for publication-quality figures
plt.style.use('seaborn-v0_8-paper')
matplotlib.rcParams['font.size'] = 18
matplotlib.rcParams['font.family'] = 'serif'
matplotlib.rcParams['font.serif'] = ['Times New Roman']
matplotlib.rcParams['axes.labelsize'] = 18
matplotlib.rcParams['axes.titlesize'] = 20
matplotlib.rcParams['xtick.labelsize'] = 16
matplotlib.rcParams['ytick.labelsize'] = 16
matplotlib.rcParams['legend.fontsize'] = 16
matplotlib.rcParams['lines.linewidth'] = 2.5
matplotlib.rcParams['lines.markersize'] = 10

# Read results
print("Loading experiment results...")
df = pd.read_csv('experiment_results/e5_audit_logs.csv')

print(f"Total records: {len(df)}")
print(f"Event counts tested: {sorted(df['event_count'].unique())}")
print(f"Query patterns: {df['pattern'].unique().tolist()}")

# Calculate statistics
print("\nCalculating statistics...")
stats = df.groupby(['event_count', 'pattern']).agg({
    'blockchain_latency_ms': ['median', 'std', 'mean'],
    'postgres_latency_ms': ['median', 'std', 'mean'],
    'mongo_latency_ms': ['median', 'std', 'mean'],
    'result_count': 'first'
}).reset_index()

# Flatten column names
stats.columns = ['_'.join(col).strip('_') for col in stats.columns.values]

# Create output directory
os.makedirs('papers/3_conference/figures', exist_ok=True)

# Generate 4 separate figures for each query pattern
print("\nGenerating Figures 1-4: Query Latency vs Event Count (separate plots)...")
patterns = ['by_subject', 'by_resource', 'time_range', 'all_denials']
pattern_filenames = {
    'by_subject': 'e5_latency_by_subject',
    'by_resource': 'e5_latency_by_resource',
    'time_range': 'e5_latency_time_range',
    'all_denials': 'e5_latency_all_denials'
}
pattern_titles = {
    'by_subject': 'By Subject',
    'by_resource': 'By Resource',
    'time_range': 'Time Range',
    'all_denials': 'All Denials'
}

for pattern in patterns:
    fig, ax = plt.subplots(figsize=(7, 5))
    data = stats[stats['pattern'] == pattern]
    
    # Plot with error bars
    ax.errorbar(data['event_count'], data['blockchain_latency_ms_median'],
                yerr=data['blockchain_latency_ms_std'],
                marker='o', capsize=4, label='Blockchain')
    ax.errorbar(data['event_count'], data['postgres_latency_ms_median'],
                yerr=data['postgres_latency_ms_std'],
                marker='s', capsize=4, label='PostgreSQL')
    ax.errorbar(data['event_count'], data['mongo_latency_ms_median'],
                yerr=data['mongo_latency_ms_std'],
                marker='^', capsize=4, label='MongoDB')
    
    ax.set_xlabel('Event Count')
    ax.set_ylabel('Median Latency (ms)')
    # No title - use LaTeX caption instead
    ax.legend(loc='best')
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.set_xscale('log')
    ax.set_yscale('log')
    
    plt.tight_layout()
    filename = pattern_filenames[pattern]
    plt.savefig(f'papers/3_conference/figures/{filename}.png', dpi=300, bbox_inches='tight')
    plt.savefig(f'papers/3_conference/figures/{filename}.pdf', bbox_inches='tight')
    print(f"  Saved: papers/3_conference/figures/{filename}.{{png,pdf}}")
    plt.close()

# Figure 2: Comparison at 10K Events (Bar Chart)
print("\nGenerating Figure 2: Latency Comparison at 10K Events...")
data_10k = stats[stats['event_count'] == 10000]

fig, ax = plt.subplots(figsize=(8, 5))
x = np.arange(len(patterns))
width = 0.25

blockchain_vals = [data_10k[data_10k['pattern'] == p]['blockchain_latency_ms_median'].values[0] 
                   if not data_10k[data_10k['pattern'] == p].empty else 0 
                   for p in patterns]
postgres_vals = [data_10k[data_10k['pattern'] == p]['postgres_latency_ms_median'].values[0] 
                 for p in patterns]
mongo_vals = [data_10k[data_10k['pattern'] == p]['mongo_latency_ms_median'].values[0] 
              for p in patterns]

bars1 = ax.bar(x - width, blockchain_vals, width, label='Blockchain', color='#1f77b4')
bars2 = ax.bar(x, postgres_vals, width, label='PostgreSQL', color='#ff7f0e')
bars3 = ax.bar(x + width, mongo_vals, width, label='MongoDB', color='#2ca02c')

ax.set_xlabel('Query Pattern')
ax.set_ylabel('Median Latency (ms)')
# No title - use LaTeX caption instead
ax.set_xticks(x)
ax.set_xticklabels([pattern_titles[p] for p in patterns], rotation=15, ha='right')
ax.legend(loc='best')
ax.grid(True, alpha=0.3, axis='y', linestyle='--')
ax.set_yscale('log')

plt.tight_layout()
plt.savefig('papers/3_conference/figures/e5_comparison_bar.png', dpi=300, bbox_inches='tight')
plt.savefig('papers/3_conference/figures/e5_comparison_bar.pdf', bbox_inches='tight')
print("  Saved: papers/3_conference/figures/e5_comparison_bar.{png,pdf}")
plt.close()

# Table 1: Median Query Latency at 10K Events (LaTeX)
print("\nGenerating LaTeX Table 1: Query Latency at 10K Events...")
print("\n" + "="*70)
print("\\begin{table}[t]")
print("\\caption{Median Query Latency (ms) at 10,000 Events}")
print("\\label{tab:latency}")
print("\\centering")
print("\\begin{tabular}{lrrrc}")
print("\\toprule")
print("Query Pattern & Blockchain & PostgreSQL & MongoDB & Ratio (BC/PG) \\\\")
print("\\midrule")

for pattern in patterns:
    row = data_10k[data_10k['pattern'] == pattern]
    if not row.empty:
        bc = row['blockchain_latency_ms_median'].values[0]
        pg = row['postgres_latency_ms_median'].values[0]
        mg = row['mongo_latency_ms_median'].values[0]
        ratio = bc / pg if pg > 0 else 0
        print(f"{pattern_titles[pattern]:15s} & {bc:6.1f} & {pg:6.1f} & {mg:6.1f} & {ratio:4.1f}$\\times$ \\\\")

print("\\bottomrule")
print("\\end{tabular}")
print("\\end{table}")
print("="*70)

# Table 2: Summary Statistics
print("\nGenerating summary statistics...")
print("\n" + "="*70)
print("SUMMARY STATISTICS")
print("="*70)

for event_count in sorted(df['event_count'].unique()):
    print(f"\n--- Event Count: {event_count} ---")
    subset = stats[stats['event_count'] == event_count]
    
    print(f"{'Pattern':<15} | {'Blockchain':<12} | {'PostgreSQL':<12} | {'MongoDB':<12}")
    print("-" * 70)
    
    for pattern in patterns:
        row = subset[subset['pattern'] == pattern]
        if not row.empty:
            bc = row['blockchain_latency_ms_median'].values[0]
            pg = row['postgres_latency_ms_median'].values[0]
            mg = row['mongo_latency_ms_median'].values[0]
            print(f"{pattern:<15} | {bc:10.2f}ms | {pg:10.2f}ms | {mg:10.2f}ms")

# Performance ratio analysis
print("\n" + "="*70)
print("PERFORMANCE RATIO ANALYSIS (Blockchain / PostgreSQL)")
print("="*70)

for event_count in sorted(df['event_count'].unique()):
    print(f"\n--- Event Count: {event_count} ---")
    subset = stats[stats['event_count'] == event_count]
    
    for pattern in patterns:
        row = subset[subset['pattern'] == pattern]
        if not row.empty:
            bc = row['blockchain_latency_ms_median'].values[0]
            pg = row['postgres_latency_ms_median'].values[0]
            ratio = bc / pg if pg > 0 else 0
            print(f"  {pattern:<15}: {ratio:5.2f}x slower")

# Storage cost estimation (placeholder - would need actual measurements)
print("\n" + "="*70)
print("STORAGE COST ESTIMATION")
print("="*70)
print("\nNote: Actual gas costs and storage sizes should be measured during deployment.")
print("Estimated costs per 10K events:")
print("  - Blockchain: ~50,000 gas per event = 500K gas total")
print("  - PostgreSQL: ~1-2 MB disk space")
print("  - MongoDB: ~2-3 MB disk space")

print("\n" + "="*70)
print("Analysis complete!")
print("Figures saved to: papers/3_conference/figures/")
print("="*70)
