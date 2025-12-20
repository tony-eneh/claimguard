#!/usr/bin/env python3
"""
E2 Analysis: Compare local vs Sepolia performance metrics.
"""

import json
import os
import argparse
import pandas as pd
import matplotlib.pyplot as plt
from typing import Dict

def load_results(e1_dir: str = "experiment_results/e1", e2_dir: str = "experiment_results/e2"):
    """Load E1 (local) and E2 (Sepolia) results."""
    results = {
        "e1": {},
        "e2": {}
    }
    
    # Load E1 latency
    e1_latency_file = os.path.join(e1_dir, "latency_read_n100_c10.csv")
    if os.path.exists(e1_latency_file):
        df = pd.read_csv(e1_latency_file)
        if 'latency_ms' in df.columns:
            latencies = df['latency_ms'].tolist()
            results["e1"]["latency"] = {
                "p50": df['latency_ms'].median(),
                "p90": df['latency_ms'].quantile(0.90),
                "p99": df['latency_ms'].quantile(0.99)
            }
            print(f"✓ Loaded E1 latency from {e1_latency_file}")
    
    # Load E2 latency
    e2_latency_file = os.path.join(e2_dir, "e2_access_latency.json")
    if os.path.exists(e2_latency_file):
        with open(e2_latency_file, "r") as f:
            data = json.load(f)
            results["e2"]["latency"] = {
                "p50": data.get("p50_ms", 0),
                "p90": data.get("p90_ms", 0),
                "p99": data.get("p99_ms", 0)
            }
            print(f"✓ Loaded E2 latency from {e2_latency_file}")
    
    # Load E2 policy confirmation
    e2_policy_file = os.path.join(e2_dir, "e2_policy_confirmation.json")
    if os.path.exists(e2_policy_file):
        with open(e2_policy_file, "r") as f:
            results["e2"]["policy_confirmation"] = json.load(f)
            print(f"✓ Loaded E2 policy confirmation from {e2_policy_file}")
    
    # Load E2 throughput
    e2_throughput_file = os.path.join(e2_dir, "e2_throughput.json")
    if os.path.exists(e2_throughput_file):
        with open(e2_throughput_file, "r") as f:
            results["e2"]["throughput"] = json.load(f)
            print(f"✓ Loaded E2 throughput from {e2_throughput_file}")
    
    return results

def generate_latency_comparison_table(results: Dict, output_dir: str):
    """Generate latency comparison table (Local vs Sepolia)."""
    data = []
    
    if "latency" in results["e1"]:
        data.append({
            "Environment": "Local (Hardhat)",
            "P50 (ms)": f"{results['e1']['latency']['p50']:.1f}",
            "P90 (ms)": f"{results['e1']['latency']['p90']:.1f}",
            "P99 (ms)": f"{results['e1']['latency']['p99']:.1f}"
        })
    
    if "latency" in results["e2"]:
        data.append({
            "Environment": "Sepolia Testnet",
            "P50 (ms)": f"{results['e2']['latency']['p50']:.1f}",
            "P90 (ms)": f"{results['e2']['latency']['p90']:.1f}",
            "P99 (ms)": f"{results['e2']['latency']['p99']:.1f}"
        })
    
    df = pd.DataFrame(data)
    
    # Save CSV
    csv_file = os.path.join(output_dir, "e2_latency_comparison.csv")
    df.to_csv(csv_file, index=False)
    print(f"✓ Latency comparison saved to {csv_file}")
    
    # Save LaTeX table
    latex_file = os.path.join(output_dir, "e2_latency_comparison.tex")
    with open(latex_file, "w", encoding='utf-8') as f:
        f.write("\\begin{table}[ht]\n")
        f.write("\\centering\n")
        f.write("\\caption{Access Latency: Local vs Sepolia}\n")
        f.write("\\small\n")
        f.write("\\begin{tabular}{lccc}\n")
        f.write("\\toprule\n")
        f.write("\\textbf{Environment} & \\textbf{P50 (ms)} & \\textbf{P90 (ms)} & \\textbf{P99 (ms)} \\\\\n")
        f.write("\\midrule\n")
        for _, row in df.iterrows():
            f.write(f"{row['Environment']} & {row['P50 (ms)']} & {row['P90 (ms)']} & {row['P99 (ms)']} \\\\\n")
        f.write("\\bottomrule\n")
        f.write("\\end{tabular}\n")
        f.write("\\label{tab:e2-latency}\n")
        f.write("\\end{table}\n")
    print(f"✓ LaTeX table saved to {latex_file}")
    
    return df

def generate_policy_confirmation_table(results: Dict, output_dir: str):
    """Generate policy update confirmation time table."""
    if "policy_confirmation" not in results["e2"]:
        print("⚠ No policy confirmation data available")
        return None
    
    pc = results["e2"]["policy_confirmation"]
    
    data = [{
        "Operation": "Policy Creation",
        "Avg (s)": f"{pc.get('avg_s', 0):.2f}",
        "Min (s)": f"{pc.get('min_s', 0):.2f}",
        "Max (s)": f"{pc.get('max_s', 0):.2f}"
    }]
    
    df = pd.DataFrame(data)
    
    # Save CSV
    csv_file = os.path.join(output_dir, "e2_policy_confirmation.csv")
    df.to_csv(csv_file, index=False)
    print(f"✓ Policy confirmation saved to {csv_file}")
    
    # Save LaTeX table
    latex_file = os.path.join(output_dir, "e2_policy_confirmation.tex")
    with open(latex_file, "w", encoding='utf-8') as f:
        f.write("\\begin{table}[ht]\n")
        f.write("\\centering\n")
        f.write("\\caption{Policy Update Confirmation Time (Sepolia)}\n")
        f.write("\\small\n")
        f.write("\\begin{tabular}{lccc}\n")
        f.write("\\toprule\n")
        f.write("\\textbf{Operation} & \\textbf{Avg (s)} & \\textbf{Min (s)} & \\textbf{Max (s)} \\\\\n")
        f.write("\\midrule\n")
        for _, row in df.iterrows():
            f.write(f"{row['Operation']} & {row['Avg (s)']} & {row['Min (s)']} & {row['Max (s)']} \\\\\n")
        f.write("\\bottomrule\n")
        f.write("\\end{tabular}\n")
        f.write("\\label{tab:e2-policy}\n")
        f.write("\\end{table}\n")
    print(f"✓ LaTeX table saved to {latex_file}")
    
    return df

def generate_latency_chart(results: Dict, output_dir: str):
    """Generate latency comparison bar chart."""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    environments = []
    p50_values = []
    p90_values = []
    p99_values = []
    
    if "latency" in results["e1"]:
        environments.append("Local\n(Hardhat)")
        p50_values.append(results["e1"]["latency"]["p50"])
        p90_values.append(results["e1"]["latency"]["p90"])
        p99_values.append(results["e1"]["latency"]["p99"])
    
    if "latency" in results["e2"]:
        environments.append("Sepolia\nTestnet")
        p50_values.append(results["e2"]["latency"]["p50"])
        p90_values.append(results["e2"]["latency"]["p90"])
        p99_values.append(results["e2"]["latency"]["p99"])
    
    x = range(len(environments))
    width = 0.25
    
    ax.bar([i - width for i in x], p50_values, width, label='P50', alpha=0.8)
    ax.bar(x, p90_values, width, label='P90', alpha=0.8)
    ax.bar([i + width for i in x], p99_values, width, label='P99', alpha=0.8)
    
    ax.set_ylabel('Latency (ms)', fontweight='bold')
    ax.set_title('Access Latency: Local vs Sepolia', fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(environments)
    ax.legend()
    ax.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    
    chart_file = os.path.join(output_dir, "e2_latency_comparison.png")
    plt.savefig(chart_file, dpi=300, bbox_inches='tight')
    print(f"✓ Chart saved to {chart_file}")
    plt.close()

def main():
    parser = argparse.ArgumentParser(description="E2 Analysis")
    parser.add_argument("--e1-dir", default="experiment_results/e1", help="E1 results directory")
    parser.add_argument("--e2-dir", default="experiment_results/e2", help="E2 results directory")
    parser.add_argument("--output-dir", default="experiment_results/e2", help="Output directory")
    parser.add_argument("--fig-dir", default="figures/e2", help="Figure output directory")
    
    args = parser.parse_args()
    
    print("=" * 80)
    print("E2 ANALYSIS: LOCAL VS SEPOLIA COMPARISON")
    print("=" * 80)
    
    # Load results
    results = load_results(args.e1_dir, args.e2_dir)
    
    # Create output directories
    os.makedirs(args.output_dir, exist_ok=True)
    os.makedirs(args.fig_dir, exist_ok=True)
    
    # Generate tables
    print("\nGenerating tables...")
    latency_df = generate_latency_comparison_table(results, args.output_dir)
    policy_df = generate_policy_confirmation_table(results, args.output_dir)
    
    # Generate charts
    print("\nGenerating charts...")
    generate_latency_chart(results, args.fig_dir)
    
    print("\n" + "=" * 80)
    print("E2 ANALYSIS COMPLETE")
    print("=" * 80)
    
    if latency_df is not None:
        print("\nLatency Comparison:")
        print(latency_df.to_string(index=False))
    
    if policy_df is not None:
        print("\nPolicy Confirmation:")
        print(policy_df.to_string(index=False))

if __name__ == "__main__":
    main()
