#!/usr/bin/env python3
import os
import argparse
import pandas as pd
import matplotlib.pyplot as plt


def summarize_access(file_path: str) -> dict:
    if not os.path.exists(file_path):
        return {"count": None, "p50_ms": None, "p90_ms": None, "p99_ms": None, "avg_gas": None}
    df = pd.read_csv(file_path)
    df = df[pd.to_numeric(df["latency_ms"], errors="coerce").notna()]
    df["latency_ms"] = df["latency_ms"].astype(float)
    p50 = df["latency_ms"].quantile(0.5)
    p90 = df["latency_ms"].quantile(0.9)
    p99 = df["latency_ms"].quantile(0.99)
    if "gas_estimate" in df.columns:
        gas = pd.to_numeric(df["gas_estimate"], errors="coerce")
        avg_gas = gas[gas.notna()].mean()
    else:
        avg_gas = None
    return {"count": len(df), "p50_ms": p50, "p90_ms": p90, "p99_ms": p99, "avg_gas": avg_gas}


def main():
    ap = argparse.ArgumentParser(description="Analyze E4 outputs and generate figures")
    ap.add_argument("--dir", type=str, default="experiment_results/e4")
    ap.add_argument("--figdir", type=str, default="figures/e4")
    args = ap.parse_args()

    os.makedirs(args.figdir, exist_ok=True)

    stages = [
        ("baseline", os.path.join(args.dir, "access_gas_baseline.csv"), 11),
        ("100", os.path.join(args.dir, "access_gas_100.csv"), 100),
        ("1000", os.path.join(args.dir, "access_gas_1000.csv"), 1000),
    ]

    rows = []
    for name, path, n in stages:
        s = summarize_access(path)
        rows.append({"stage": name, "policies": n, **s})

    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(args.dir, "e4_scale_summary.csv"), index=False)

    # Plot latency vs policy count (P50)
    plt.figure(figsize=(6,4))
    plt.plot(df["policies"], df["p50_ms"], marker='o')
    plt.xlabel("Policy count")
    plt.ylabel("P50 checkAccess latency (ms)")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(args.figdir, "policy_count_vs_latency_p50.png"), dpi=160)

    # Plot avg gas vs policy count
    if df["avg_gas"].notna().any():
        plt.figure(figsize=(6,4))
        plt.plot(df["policies"], df["avg_gas"], marker='o', color='orange')
        plt.xlabel("Policy count")
        plt.ylabel("Estimated gas (checkAccess)")
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(os.path.join(args.figdir, "policy_count_vs_gas.png"), dpi=160)

    print("E4 analysis complete:")
    print(df)


if __name__ == "__main__":
    main()
