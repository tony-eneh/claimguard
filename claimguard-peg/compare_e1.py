#!/usr/bin/env python3
"""
Generate E1 comparison outputs across RBAC, Hybrid-Audit, and ClaimGuard.
- Reads CSVs from claimguard-peg/experiment_results/{rbac, hybrid, claimguard}
- Produces combined latency table, throughput comparison figure, and authorization summary.
- Writes LaTeX tables to journal/figures and PNG to journal/figures.
"""
import os
import glob
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

ROOT = os.path.dirname(os.path.abspath(__file__))
RESULTS_BASE = os.path.join(ROOT, "experiment_results")
SYSTEMS = {
    "RBAC-DB": os.path.join(RESULTS_BASE, "rbac"),
    "Hybrid-Audit": os.path.join(RESULTS_BASE, "hybrid"),
    "ClaimGuard": os.path.join(RESULTS_BASE, "claimguard"),
}

JOURNAL_FIG_DIR = os.path.join(ROOT, "..", "journal", "figures")
os.makedirs(JOURNAL_FIG_DIR, exist_ok=True)

LATENCY_OUT_TEX = os.path.join(JOURNAL_FIG_DIR, "e1_latency_table.tex")
AUTH_OUT_TEX = os.path.join(JOURNAL_FIG_DIR, "e1_authorization_table.tex")
THR_OUT_PNG = os.path.join(JOURNAL_FIG_DIR, "e1_throughput_comparison.png")


def read_latency_files(dir_path: str):
    files = sorted(glob.glob(os.path.join(dir_path, "latency_read_n*.csv")))
    rows = []
    for p in files:
        df = pd.read_csv(p)
        lat = df["latency_ms"].dropna().astype(float)
        if lat.empty:
            continue
        p50 = float(np.percentile(lat, 50))
        p90 = float(np.percentile(lat, 90))
        p99 = float(np.percentile(lat, 99))
        base = os.path.basename(p).replace(".csv", "")
        parts = base.split("_")
        n_part = [x for x in parts if x.startswith("n")][0]
        c_part = [x for x in parts if x.startswith("c")][0]
        n = int(n_part[1:])
        c = int(c_part[1:])
        rows.append({"requests": n, "concurrency": c, "P50": p50, "P90": p90, "P99": p99})
    return pd.DataFrame(rows)


def read_throughput_files(dir_path: str):
    files = sorted(glob.glob(os.path.join(dir_path, "throughput_read_n*.csv")))
    rows = []
    for p in files:
        df = pd.read_csv(p)
        lat = df["latency_ms"].dropna().astype(float)
        if lat.empty:
            continue
        base = os.path.basename(p).replace(".csv", "")
        parts = base.split("_")
        c_part = [x for x in parts if x.startswith("c")][0]
        c = int(c_part[1:])
        avg_lat_s = lat.mean() / 1000.0
        thr = c / avg_lat_s
        rows.append({"concurrency": c, "throughput_rps": thr})
    return pd.DataFrame(rows)


def read_auth_outcomes(dir_path: str):
    files = sorted(glob.glob(os.path.join(dir_path, "throughput_read_n*.csv"))
                   + glob.glob(os.path.join(dir_path, "latency_read_n*.csv")))
    total = 0
    allowed = 0
    denied = 0
    for p in files:
        df = pd.read_csv(p)
        if "allowed" not in df.columns:
            continue
        total += len(df)
        allowed += df["allowed"].fillna(False).astype(bool).sum()
        denied += (~df["allowed"].fillna(False).astype(bool)).sum()
    allow_ratio = (allowed / total) if total else 0.0
    deny_ratio = (denied / total) if total else 0.0
    return {"total": total, "allowed": allowed, "denied": denied, "allow_ratio": allow_ratio, "deny_ratio": deny_ratio}


def make_latency_table():
    # Combine for requests n in {50,100,200,500} at c=10
    targets = [50, 100, 200, 500]
    rows = []
    for sys, dirp in SYSTEMS.items():
        df = read_latency_files(dirp)
        if df.empty:
            continue
        
        for n in targets:
            rec = df[(df["requests"] == n) & (df["concurrency"] == 10)]
            if rec.empty:
                continue
            r = rec.iloc[0]
            rows.append([sys, n, int(r["concurrency"]), round(r["P50"], 2), round(r["P90"], 2), round(r["P99"], 2)])
    out = pd.DataFrame(rows, columns=["System", "Requests", "Concurrency", "P50", "P90", "P99"])

    # Write LaTeX table
    lines = []
    lines.append("\\begin{table}[ht]")
    lines.append("\\centering")
    lines.append("\\caption{E1: End-to-End Access Latency (ms) across systems}")
    lines.append("\\begin{tabular}{lcccc}")
    lines.append("\\toprule")
    lines.append("\\textbf{System} & \\textbf{P50} & \\textbf{P90} & \\textbf{P99} \\\")
    lines.append("\\midrule")
    # Order rows grouped by system (average across targets)
    # For simplicity, show the n=200, c=10 representative values
    rep = out[out["Requests"] == 200]
    for _, row in rep.iterrows():
        lines.append(f"{row['System']} & {row['P50']:.2f} & {row['P90']:.2f} & {row['P99']:.2f} \\")
    lines.append("\\bottomrule")
    lines.append("\\end{tabular}")
    lines.append("\\label{tab:e1-latency}")
    lines.append("\\end{table}")

    with open(LATENCY_OUT_TEX, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    return out


def make_throughput_comparison():
    plt.figure(figsize=(7, 4))
    for sys, dirp in SYSTEMS.items():
        df = read_throughput_files(dirp)
        if df.empty:
            continue
        df = df.sort_values("concurrency")
        plt.plot(df["concurrency"], df["throughput_rps"], marker="o", label=sys)
    plt.xlabel("Concurrency (users)")
    plt.ylabel("Throughput (req/s)")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(THR_OUT_PNG, dpi=300, bbox_inches="tight")
    plt.close()


def make_auth_table():
    rows = []
    for sys, dirp in SYSTEMS.items():
        m = read_auth_outcomes(dirp)
        rows.append([sys, m["total"], m["allowed"], m["denied"], round(m["allow_ratio"], 4), round(m["deny_ratio"], 4)])
    out = pd.DataFrame(rows, columns=["System", "Total", "Allowed", "Denied", "AllowRatio", "DenyRatio"])

    # Write LaTeX table
    lines = []
    lines.append("\\begin{table}[ht]")
    lines.append("\\centering")
    lines.append("\\caption{E1: Authorization Outcomes (proxy for FAR/FRR)}")
    lines.append("\\begin{tabular}{lccc}")
    lines.append("\\toprule")
    lines.append("\\textbf{System} & \\textbf{Allowed (")} ; lines.append("\\%) & \\textbf{Denied (") ; lines.append("\\%)} \\\")
    # The above split to avoid escaping issues; build rows
    lines = lines[:-1]  # remove malformed lines
    lines.append("\\textbf{System} & \\textbf{Allowed (\\%)} & \\textbf{Denied (\\%)} \\\")
    lines.append("\\midrule")
    for _, row in out.iterrows():
        allowed_pct = 100.0 * float(row["AllowRatio"]) if row["Total"] else 0.0
        denied_pct = 100.0 * float(row["DenyRatio"]) if row["Total"] else 0.0
        lines.append(f"{row['System']} & {allowed_pct:.2f} & {denied_pct:.2f} \\")
    lines.append("\\bottomrule")
    lines.append("\\end{tabular}")
    lines.append("\\label{tab:e1-auth}")
    lines.append("\\end{table}")

    with open(AUTH_OUT_TEX, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    return out


if __name__ == "__main__":
    lat_df = make_latency_table()
    make_throughput_comparison()
    auth_df = make_auth_table()
    print("Generated:")
    print(" -", LATENCY_OUT_TEX)
    print(" -", AUTH_OUT_TEX)
    print(" -", THR_OUT_PNG)
