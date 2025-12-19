#!/usr/bin/env python
"""
E1: RBAC vs Hybrid-Audit vs ClaimGuard Comparison Analysis

Reads CSVs from experiment_results/rbac, experiment_results/hybrid, and experiment_results/claimguard
Generates journal-ready tables and figures for latency, throughput, correctness comparisons.

Outputs:
  - figures/e1/latency_comparison_table.csv
  - figures/e1/latency_comparison_bar.png
  - figures/e1/throughput_comparison.png
  - figures/e1/correctness_table.csv
  - figures/e1/policy_update_table.csv
"""

import os
import glob
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Directory config
RESULT_DIR = os.path.join("claimguard-peg", "experiment_results")
OUTPUT_DIR = os.path.join("claimguard-peg", "figures", "e1")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# =========================================================================
# 1. LATENCY COMPARISON TABLE (3 modes)
# =========================================================================


def compute_latency_comparison():
    """
    Generate a table with P50/P90/P99 latencies for RBAC, Hybrid-Audit, ClaimGuard
    from the latency_read_n200_c10.csv files (chosen as representative n=200 workload).
    """
    modes = ["rbac", "hybrid", "claimguard"]
    rows = []

    for mode in modes:
        path = os.path.join(RESULT_DIR, mode, "latency_read_n200_c10.csv")
        if not os.path.exists(path):
            print(f"WARNING: {path} not found, skipping {mode}")
            continue

        df = pd.read_csv(path)
        lat = df["latency_ms"].dropna().astype(float)

        p50 = float(np.percentile(lat, 50))
        p90 = float(np.percentile(lat, 90))
        p99 = float(np.percentile(lat, 99))

        rows.append([mode.upper(), p50, p90, p99])

    out = pd.DataFrame(
        rows,
        columns=["System", "P50_ms", "P90_ms", "P99_ms"],
    )
    out_path = os.path.join(OUTPUT_DIR, "latency_comparison_table.csv")
    out.to_csv(out_path, index=False)
    print("Latency Comparison Table (n=200):")
    print(out)
    print(f"Saved → {out_path}\n")
    return out


# =========================================================================
# 2. LATENCY BAR CHART (3 modes side-by-side)
# =========================================================================


def plot_latency_comparison_bar(df_latency):
    """
    Generate a bar chart with P50/P90/P99 for each mode.
    """
    if df_latency.empty:
        print("No latency data for bar chart")
        return

    modes = df_latency["System"].tolist()
    p50 = df_latency["P50_ms"].tolist()
    p90 = df_latency["P90_ms"].tolist()
    p99 = df_latency["P99_ms"].tolist()

    x = np.arange(len(modes))
    width = 0.25

    fig, ax = plt.subplots(figsize=(10, 6))

    ax.bar(x - width, p50, width, label="P50", alpha=0.8)
    ax.bar(x, p90, width, label="P90", alpha=0.8)
    ax.bar(x + width, p99, width, label="P99", alpha=0.8)

    ax.set_xlabel("System", fontsize=24)
    ax.set_ylabel("Latency (ms)", fontsize=24)
    ax.set_xticks(x)
    ax.set_xticklabels(modes, fontsize=24)
    ax.tick_params(axis='y', labelsize=24)
    ax.legend(fontsize=24)
    ax.grid(True, axis='y', alpha=0.3)

    plt.tight_layout()
    out_path = os.path.join(OUTPUT_DIR, "latency_comparison_bar.png")
    plt.savefig(out_path, dpi=300, bbox_inches="tight")
    print(f"Saved latency bar chart → {out_path}\n")
    plt.close()


# =========================================================================
# 3. THROUGHPUT COMPARISON (concurrency on x-axis, req/s on y, 3 curves)
# =========================================================================


def plot_throughput_comparison():
    """
    For each mode, compute throughput from throughput_read_n1000_c*.csv
    Plot concurrency vs req/s for RBAC, Hybrid, ClaimGuard.
    """
    modes = ["rbac", "hybrid", "claimguard"]
    data = []

    for mode in modes:
        files = sorted(glob.glob(os.path.join(RESULT_DIR, mode, "throughput_read_n*.csv")))
        if not files:
            print(f"No throughput files for {mode}")
            continue

        mode_rows = []
        for path in files:
            df = pd.read_csv(path)
            lat = df["latency_ms"].dropna().astype(float)
            if lat.empty:
                continue

            avg_lat_s = lat.mean() / 1000.0

            basename = os.path.basename(path).replace(".csv", "")
            parts = basename.split("_")
            c_part = [p for p in parts if p.startswith("c")][0]
            conc = int(c_part[1:])

            thr_est = conc / avg_lat_s if avg_lat_s > 0 else 0
            mode_rows.append([mode, conc, thr_est])

        if mode_rows:
            data.extend(mode_rows)

    if not data:
        print("No throughput data to plot")
        return

    df_thr = pd.DataFrame(data, columns=["mode", "concurrency", "throughput_rps"])

    fig, ax = plt.subplots(figsize=(10, 6))

    for mode in modes:
        subset = df_thr[df_thr["mode"] == mode].sort_values("concurrency")
        if subset.empty:
            continue
        label = mode.upper()
        if mode == "hybrid":
            label = "Hybrid-Audit"
        elif mode == "claimguard":
            label = "ClaimGuard"

        ax.plot(subset["concurrency"], subset["throughput_rps"], marker="o", label=label, linewidth=2)

    ax.set_xlabel("Concurrency (users)", fontsize=24)
    ax.set_ylabel("Throughput (req/s)", fontsize=24)
    ax.tick_params(axis='x', labelsize=24)
    ax.tick_params(axis='y', labelsize=24)
    ax.legend(fontsize=24)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    out_path = os.path.join(OUTPUT_DIR, "throughput_comparison.png")
    plt.savefig(out_path, dpi=300, bbox_inches="tight")
    print(f"Saved throughput comparison → {out_path}\n")
    plt.close()


# =========================================================================
# 4. CORRECTNESS TABLE (FAR/FRR)
# =========================================================================


def compute_correctness_comparison():
    """
    Aggregate 'allowed' flags across all latency + throughput runs
    to produce allow/deny counts and compute allow ratio for each mode.
    (Conceptual FAR/FRR if we had ground truth; for now, we just show allowed/denied ratios.)
    """
    modes = ["rbac", "hybrid", "claimguard"]
    rows = []

    for mode in modes:
        files = sorted(
            glob.glob(os.path.join(RESULT_DIR, mode, "throughput_read_n*.csv"))
            + glob.glob(os.path.join(RESULT_DIR, mode, "latency_read_n*.csv"))
        )

        total = 0
        allowed = 0
        denied = 0

        for path in files:
            df = pd.read_csv(path)
            if "allowed" not in df.columns:
                continue
            total += len(df)
            allowed += df["allowed"].fillna(False).astype(bool).sum()
            denied += (~df["allowed"].fillna(False).astype(bool)).sum()

        allow_ratio = allowed / total if total else 0
        deny_ratio = denied / total if total else 0

        rows.append([mode.upper(), total, allowed, denied, allow_ratio, deny_ratio])

    out = pd.DataFrame(
        rows,
        columns=["System", "Total_Requests", "Allowed", "Denied", "Allow_Ratio", "Deny_Ratio"]
    )

    out_path = os.path.join(OUTPUT_DIR, "correctness_table.csv")
    out.to_csv(out_path, index=False)
    print("Correctness Summary:")
    print(out)
    print(f"Saved → {out_path}\n")


# =========================================================================
# 5. POLICY UPDATE TABLE
# =========================================================================


def extract_policy_update_costs():
    """
    Read policy_updates_10.csv from ClaimGuard and hybrid modes (if present).
    RBAC has no on-chain policy update, so just show ClaimGuard and Hybrid latencies.
    """
    rows = []

    for mode in ["claimguard", "hybrid"]:
        path = os.path.join(RESULT_DIR, mode, "policy_updates_10.csv")
        if not os.path.exists(path):
            print(f"WARNING: {path} not found, skipping {mode} policy update")
            continue

        df = pd.read_csv(path)

        avg_lat = float(df["latency_ms"].mean())
        avg_gas = float(df["gas_used"].mean()) if "gas_used" in df.columns else 0

        rows.append([mode.upper(), avg_lat, avg_gas])

    if not rows:
        print("No policy update data available")
        return

    out = pd.DataFrame(
        rows,
        columns=["System", "Avg_Latency_ms", "Avg_Gas_Used"]
    )

    out_path = os.path.join(OUTPUT_DIR, "policy_update_table.csv")
    out.to_csv(out_path, index=False)
    print("Policy Update Costs:")
    print(out)
    print(f"Saved → {out_path}\n")


# =========================================================================
# MAIN
# =========================================================================


if __name__ == "__main__":
    print("=== E1 Comparison Analysis ===\n")

    df_lat = compute_latency_comparison()
    plot_latency_comparison_bar(df_lat)
    plot_throughput_comparison()
    compute_correctness_comparison()
    extract_policy_update_costs()

    print("All E1 comparison outputs complete. Check claimguard-peg/figures/e1/\n")
