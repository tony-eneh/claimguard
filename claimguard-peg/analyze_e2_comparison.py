#!/usr/bin/env python3
"""
E2 Comparison Analysis: Local vs Sepolia
Generates LaTeX tables and figures comparing local Hardhat vs public Sepolia network.
"""

import json
import os
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend

# Paths
SCRIPT_DIR = Path(__file__).resolve().parent
LOCAL_DIR = SCRIPT_DIR / "experiment_results" / "e2"
SEPOLIA_DIR = SCRIPT_DIR / "experiment_results" / "e2-sepolia"
OUTPUT_DIR = SCRIPT_DIR / "figures"

def load_json(path):
    """Load JSON file."""
    with open(path, 'r') as f:
        return json.load(f)

def generate_latency_table():
    """Generate LaTeX table for access latency comparison."""
    local_latency = load_json(LOCAL_DIR / "e2_access_latency.json")
    sepolia_latency = load_json(SEPOLIA_DIR / "e2_access_latency.json")
    
    latex = r"""\begin{table}[h]
\centering
\caption{Access Latency: Local vs Public Network (E2)}
\label{tab:e2-latency}
\begin{tabular}{lrrr}
\toprule
\textbf{Metric} & \textbf{Local (ms)} & \textbf{Sepolia (ms)} & \textbf{Overhead} \\
\midrule
"""
    
    metrics = [
        ("P50", "p50_ms"),
        ("P90", "p90_ms"),
        ("P99", "p99_ms"),
        ("Average", "avg_ms"),
        ("Min", "min_ms"),
        ("Max", "max_ms"),
    ]
    
    for label, key in metrics:
        local_val = local_latency[key]
        sepolia_val = sepolia_latency[key]
        overhead = ((sepolia_val - local_val) / local_val) * 100
        latex += f"{label} & {local_val:.2f} & {sepolia_val:.2f} & {overhead:.1f}\\% \\\\\n"
    
    latex += r"""\bottomrule
\end{tabular}
\end{table}
"""
    
    output_path = OUTPUT_DIR / "e2_latency_table.tex"
    with open(output_path, 'w') as f:
        f.write(latex)
    print(f"✓ Generated {output_path}")

def generate_throughput_table():
    """Generate LaTeX table for throughput comparison."""
    local_throughput = load_json(LOCAL_DIR / "e2_throughput.json")
    sepolia_throughput = load_json(SEPOLIA_DIR / "e2_throughput.json")
    
    latex = r"""\begin{table}[h]
\centering
\caption{Throughput: Local vs Public Network (E2)}
\label{tab:e2-throughput}
\begin{tabular}{lrrr}
\toprule
\textbf{Concurrency} & \textbf{Local (req/s)} & \textbf{Sepolia (req/s)} & \textbf{Reduction} \\
\midrule
"""
    
    for local_res, sepolia_res in zip(local_throughput["results"], sepolia_throughput["results"]):
        conc = local_res["concurrency"]
        local_tput = local_res["throughput_rps"]
        sepolia_tput = sepolia_res["throughput_rps"]
        reduction = ((local_tput - sepolia_tput) / local_tput) * 100
        latex += f"{conc} & {local_tput:.2f} & {sepolia_tput:.2f} & {reduction:.1f}\\% \\\\\n"
    
    latex += r"""\bottomrule
\end{tabular}
\end{table}
"""
    
    output_path = OUTPUT_DIR / "e2_throughput_table.tex"
    with open(output_path, 'w') as f:
        f.write(latex)
    print(f"✓ Generated {output_path}")

def generate_policy_confirmation_table():
    """Generate LaTeX table for policy confirmation time comparison."""
    local_policy = load_json(LOCAL_DIR / "e2_policy_confirmation.json")
    sepolia_policy = load_json(SEPOLIA_DIR / "e2_policy_confirmation.json")
    
    latex = r"""\begin{table}[h]
\centering
\caption{Policy Update Confirmation Time: Local vs Public Network (E2)}
\label{tab:e2-policy}
\begin{tabular}{lrrr}
\toprule
\textbf{Metric} & \textbf{Local (s)} & \textbf{Sepolia (s)} & \textbf{Overhead} \\
\midrule
"""
    
    metrics = [
        ("Average", "avg_s"),
        ("Median", "median_s"),
        ("Min", "min_s"),
        ("Max", "max_s"),
    ]
    
    for label, key in metrics:
        local_val = local_policy[key]
        sepolia_val = sepolia_policy[key]
        overhead = ((sepolia_val - local_val) / local_val) * 100 if local_val > 0 else 0
        latex += f"{label} & {local_val:.2f} & {sepolia_val:.2f} & {overhead:.1f}\\% \\\\\n"
    
    latex += r"""\bottomrule
\end{tabular}
\end{table}
"""
    
    output_path = OUTPUT_DIR / "e2_policy_table.tex"
    with open(output_path, 'w') as f:
        f.write(latex)
    print(f"✓ Generated {output_path}")

def generate_latency_comparison_chart():
    """Generate bar chart comparing latency percentiles."""
    local_latency = load_json(LOCAL_DIR / "e2_access_latency.json")
    sepolia_latency = load_json(SEPOLIA_DIR / "e2_access_latency.json")
    
    metrics = ["p50_ms", "p90_ms", "p99_ms"]
    labels = ["P50", "P90", "P99"]
    
    local_vals = [local_latency[m] for m in metrics]
    sepolia_vals = [sepolia_latency[m] for m in metrics]
    
    x = range(len(labels))
    width = 0.35
    
    fig, ax = plt.subplots(figsize=(8, 5))
    bars1 = ax.bar([i - width/2 for i in x], local_vals, width, label='Local (Hardhat)', color='#2563eb')
    bars2 = ax.bar([i + width/2 for i in x], sepolia_vals, width, label='Sepolia (Public)', color='#dc2626')
    
    ax.set_xlabel('Latency Percentile', fontsize=18)
    ax.set_ylabel('Latency (ms)', fontsize=18)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=18)
    ax.tick_params(axis='y', labelsize=18)
    ax.legend(fontsize=18)
    ax.grid(axis='y', alpha=0.3)
    
    # Add value labels on bars
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.1f}',
                   ha='center', va='bottom', fontsize=20)
    
    plt.tight_layout()
    output_path = OUTPUT_DIR / "e2_latency_comparison.png"
    plt.savefig(output_path, format='png', dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✓ Generated {output_path}")

def generate_throughput_comparison_chart():
    """Generate bar chart comparing throughput."""
    local_throughput = load_json(LOCAL_DIR / "e2_throughput.json")
    sepolia_throughput = load_json(SEPOLIA_DIR / "e2_throughput.json")
    
    concurrency_levels = [r["concurrency"] for r in local_throughput["results"]]
    local_tput = [r["throughput_rps"] for r in local_throughput["results"]]
    sepolia_tput = [r["throughput_rps"] for r in sepolia_throughput["results"]]
    
    x = range(len(concurrency_levels))
    width = 0.35
    
    fig, ax = plt.subplots(figsize=(8, 5))
    bars1 = ax.bar([i - width/2 for i in x], local_tput, width, label='Local (Hardhat)', color='#2563eb')
    bars2 = ax.bar([i + width/2 for i in x], sepolia_tput, width, label='Sepolia (Public)', color='#dc2626')
    
    ax.set_xlabel('Concurrency Level', fontsize=18)
    ax.set_ylabel('Throughput (req/s)', fontsize=18)
    ax.set_xticks(x)
    ax.set_xticklabels(concurrency_levels, fontsize=18)
    ax.tick_params(axis='y', labelsize=18)
    ax.legend(fontsize=18)
    ax.grid(axis='y', alpha=0.3)
    
    # Add value labels on bars
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.0f}',
                   ha='center', va='bottom', fontsize=20)
    
    plt.tight_layout()
    output_path = OUTPUT_DIR / "e2_throughput_comparison.png"
    plt.savefig(output_path, format='png', dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✓ Generated {output_path}")

def generate_policy_confirmation_chart():
    """Generate comparison chart for policy confirmation times."""
    local_policy = load_json(LOCAL_DIR / "e2_policy_confirmation.json")
    sepolia_policy = load_json(SEPOLIA_DIR / "e2_policy_confirmation.json")
    
    metrics = ["avg_s", "median_s", "min_s", "max_s"]
    labels = ["Average", "Median", "Min", "Max"]
    
    local_vals = [local_policy[m] for m in metrics]
    sepolia_vals = [sepolia_policy[m] for m in metrics]
    
    x = range(len(labels))
    width = 0.35
    
    fig, ax = plt.subplots(figsize=(8, 5))
    bars1 = ax.bar([i - width/2 for i in x], local_vals, width, label='Local (Hardhat)', color='#2563eb')
    bars2 = ax.bar([i + width/2 for i in x], sepolia_vals, width, label='Sepolia (Public)', color='#dc2626')
    
    ax.set_xlabel('Confirmation Time Metric', fontsize=18)
    ax.set_ylabel('Time (seconds)', fontsize=18)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=18)
    ax.tick_params(axis='y', labelsize=18)
    ax.legend(fontsize=18)
    ax.grid(axis='y', alpha=0.3)
    
    # Add value labels on bars
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.1f}',
                   ha='center', va='bottom', fontsize=20)
    
    plt.tight_layout()
    output_path = OUTPUT_DIR / "e2_policy_comparison.png"
    plt.savefig(output_path, format='png', dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✓ Generated {output_path}")

def main():
    """Generate all E2 comparison tables and figures."""
    print("=" * 80)
    print("E2 COMPARISON ANALYSIS: LOCAL VS SEPOLIA")
    print("=" * 80)
    
    # Create output directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Generate LaTeX tables
    print("\nGenerating LaTeX tables...")
    generate_latency_table()
    generate_throughput_table()
    generate_policy_confirmation_table()
    
    # Generate comparison charts
    print("\nGenerating comparison charts...")
    generate_latency_comparison_chart()
    generate_throughput_comparison_chart()
    generate_policy_confirmation_chart()
    
    print("\n" + "=" * 80)
    print("E2 COMPARISON ANALYSIS COMPLETED")
    print("=" * 80)
    print(f"\nOutputs saved to {OUTPUT_DIR}")
    print("\nLaTeX tables:")
    print("  - e2_latency_table.tex")
    print("  - e2_throughput_table.tex")
    print("  - e2_policy_table.tex")
    print("\nFigures:")
    print("  - e2_latency_comparison.pdf")
    print("  - e2_throughput_comparison.pdf")
    print("  - e2_policy_comparison.pdf")

if __name__ == "__main__":
    main()
