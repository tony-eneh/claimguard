import os
import glob
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

RESULT_DIR = "claimguard-peg/experiment_results"
OUTPUT_DIR = "claimguard-peg/figures"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ----------------------------
# 1. LATENCY SUMMARY TABLES
# ----------------------------


def compute_latency_stats():
    rows = []
    files = sorted(glob.glob(os.path.join(RESULT_DIR, "latency_read_n*.csv")))
    for path in files:
        df = pd.read_csv(path)
        lat = df["latency_ms"].dropna().astype(float)

        p50 = float(np.percentile(lat, 50))
        p90 = float(np.percentile(lat, 90))
        p99 = float(np.percentile(lat, 99))

        basename = os.path.basename(path).replace(".csv", "")
        # e.g. latency_read_n50_c10 → n=50, c=10
        parts = basename.split("_")
        n_part = [p for p in parts if p.startswith("n")][0]
        c_part = [p for p in parts if p.startswith("c")][0]
        n_req = int(n_part[1:])
        conc = int(c_part[1:])

        rows.append([basename, n_req, conc, p50, p90, p99])

    out = pd.DataFrame(
        rows,
        columns=["test", "requests", "concurrency",
                 "P50_ms", "P90_ms", "P99_ms"],
    )
    out_path = os.path.join(OUTPUT_DIR, "latency_summary.csv")
    out.to_csv(out_path, index=False)
    print(out)
    print(f"\nSaved → {out_path}\n")


# ----------------------------
# 2. LATENCY BAR CHART
# ----------------------------


def plot_latency_bar_chart():
    """
    Generate a bar chart showing P50, P90, and P99 latencies
    for different request counts from latency_read_n*.csv files
    """
    rows = []
    files = sorted(glob.glob(os.path.join(RESULT_DIR, "latency_read_n*.csv")))

    if not files:
        print("No latency_read_n*.csv files found")
        return

    for path in files:
        df = pd.read_csv(path)
        lat = df["latency_ms"].dropna().astype(float)

        if lat.empty:
            continue

        p50 = float(np.percentile(lat, 50))
        p90 = float(np.percentile(lat, 90))
        p99 = float(np.percentile(lat, 99))

        basename = os.path.basename(path).replace(".csv", "")
        # e.g. latency_read_n50_c10 → n=50
        parts = basename.split("_")
        n_part = [p for p in parts if p.startswith("n")][0]
        n_req = int(n_part[1:])

        rows.append([n_req, p50, p90, p99])

    df_lat = pd.DataFrame(rows, columns=["requests", "P50", "P90", "P99"])
    df_lat = df_lat.sort_values("requests")

    print("Latency Data for Bar Chart:")
    print(df_lat)
    print()

    # Create bar chart
    x = np.arange(len(df_lat))
    width = 0.25

    fig, ax = plt.subplots(figsize=(10, 6))

    bars1 = ax.bar(x - width, df_lat["P50"], width, label="P50", alpha=0.8)
    bars2 = ax.bar(x, df_lat["P90"], width, label="P90", alpha=0.8)
    bars3 = ax.bar(x + width, df_lat["P99"], width, label="P99", alpha=0.8)

    ax.set_xlabel("Number of Requests", fontsize=12)
    ax.set_ylabel("Latency (ms)", fontsize=12)
    # ax.set_title("PureChain ABAC Latency Distribution", fontsize=14)
    ax.set_xticks(x)
    ax.set_xticklabels([f"n={n}" for n in df_lat["requests"]])
    ax.legend()
    ax.grid(True, axis='y', alpha=0.3)

    plt.tight_layout()

    out_path = os.path.join(OUTPUT_DIR, "latency_bar_chart.png")
    plt.savefig(out_path, dpi=300, bbox_inches="tight")
    print(f"Saved latency bar chart → {out_path}\n")
    plt.close()


# ----------------------------
# 3. THROUGHPUT PLOT
# ----------------------------


def plot_throughput():
    """
    Throughput ≈ concurrency / avg_latency_seconds

    We use *all* requests (200, 403, 500, …) because throughput is
    "decisions per second", not "successful reads per second".
    """
    rows = []
    files = sorted(glob.glob(os.path.join(
        RESULT_DIR, "throughput_read_n*.csv")))
    if not files:
        print("No throughput_read_n*.csv files found")
        return

    for path in files:
        df = pd.read_csv(path)
        lat = df["latency_ms"].dropna().astype(float)

        if lat.empty:
            continue

        avg_lat_s = lat.mean() / 1000.0  # average per-request latency in seconds

        basename = os.path.basename(path).replace(".csv", "")
        # e.g. throughput_read_n1000_c50 → c=50
        parts = basename.split("_")
        c_part = [p for p in parts if p.startswith("c")][0]
        conc = int(c_part[1:])

        # steady-state throughput estimate
        thr_est = conc / avg_lat_s  # req/s

        rows.append([conc, thr_est])

    df_thr = pd.DataFrame(rows, columns=["concurrency", "throughput_rps"])
    df_thr = df_thr.sort_values("concurrency")

    print(df_thr)
    print()

    plt.figure(figsize=(6, 4))
    plt.plot(df_thr["concurrency"], df_thr["throughput_rps"], marker="o")
    plt.xlabel("Concurrency (users)")
    plt.ylabel("Throughput (req/s)")
    # plt.title("PureChain ABAC Throughput")
    plt.grid(True)

    out_path = os.path.join(OUTPUT_DIR, "throughput.png")
    plt.savefig(out_path, dpi=300, bbox_inches="tight")
    print(f"Saved throughput plot → {out_path}\n")


# ----------------------------
# 4. POLICY UPDATE COSTS
# ----------------------------


def extract_policy_update_costs():
    path = os.path.join(RESULT_DIR, "policy_updates_10.csv")
    if not os.path.exists(path):
        print("No policy_updates_10.csv found")
        return

    df = pd.read_csv(path)

    avg_lat = float(df["latency_ms"].mean())
    avg_gas = float(df["gas_used"].mean())
    avg_block = float(df["block_number"].mean())

    out = pd.DataFrame(
        [
            {
                "avg_latency_ms": avg_lat,
                "avg_gas_used": avg_gas,
                "avg_block_number": avg_block,
            }
        ]
    )

    out_path = os.path.join(OUTPUT_DIR, "policy_update_summary.csv")
    out.to_csv(out_path, index=False)
    print(out)
    print(f"\nSaved → {out_path}\n")


# ----------------------------
# 5. AUTHORIZATION CORRECTNESS
# ----------------------------


def compute_correctness():
    """
    We only have an `allowed` flag, not ground-truth labels.
    So here we just summarise how many decisions were allows vs denies.
    FAR/FRR in the LaTeX text will stay conceptual unless you add
    an `intended_allowed` column in the generators.
    """
    files = sorted(
        glob.glob(os.path.join(RESULT_DIR, "throughput_read_n*.csv"))
        + glob.glob(os.path.join(RESULT_DIR, "latency_read_n*.csv"))
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

    out = pd.DataFrame(
        [
            {
                "total_decisions": total,
                "allowed": allowed,
                "denied": denied,
                "allow_ratio": allow_ratio,
                "deny_ratio": deny_ratio,
            }
        ]
    )

    out_path = os.path.join(OUTPUT_DIR, "correctness_summary.csv")
    out.to_csv(out_path, index=False)
    print(out)
    print(f"\nSaved → {out_path}\n")


# ----------------------------
# RUN ALL
# ----------------------------
if __name__ == "__main__":
    compute_latency_stats()
    plot_latency_bar_chart()
    plot_throughput()
    extract_policy_update_costs()
    compute_correctness()

    print("\nAll analysis complete.")
