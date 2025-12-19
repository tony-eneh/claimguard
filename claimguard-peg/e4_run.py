#!/usr/bin/env python3
import argparse
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))


def run(cmd: list[str]):
    print("\n>>>", " ".join(cmd))
    proc = subprocess.run(cmd, cwd=ROOT)
    if proc.returncode != 0:
        print(f"!!! Command failed: {' '.join(cmd)}", file=sys.stderr)
        sys.exit(proc.returncode)


def main():
    parser = argparse.ArgumentParser(description="E4 Orchestrator: seed, scale, churn, revocation")
    parser.add_argument("--base-url", type=str, default="http://localhost:4000/api")
    parser.add_argument("--results-dir", type=str, default="experiment_results/e4")
    args = parser.parse_args()

    base_url = args.base_url
    out_dir = os.path.join(ROOT, args.results_dir)
    os.makedirs(out_dir, exist_ok=True)

    # Stage 0: ensure baseline measurement
    run([sys.executable, os.path.join(ROOT, "e4_scale_access_gas.py"),
         "--base-url", base_url,
         "--samples", "300",
         "--output", os.path.join(args.results_dir, "access_gas_baseline.csv")])

    # Stage 1: seed to 100 policies
    run([sys.executable, os.path.join(ROOT, "e4_seed_policies.py"),
         "--base-url", base_url,
         "--target", "100",
         "--concurrency", "6",
         "--rate", "0",
         "--output", os.path.join(args.results_dir, "seed_100.csv")])

    run([sys.executable, os.path.join(ROOT, "e4_scale_access_gas.py"),
         "--base-url", base_url,
         "--samples", "300",
         "--output", os.path.join(args.results_dir, "access_gas_100.csv")])

    # Stage 2: seed to 1000 policies
    run([sys.executable, os.path.join(ROOT, "e4_seed_policies.py"),
         "--base-url", base_url,
         "--target", "1000",
         "--concurrency", "8",
         "--rate", "0",
         "--output", os.path.join(args.results_dir, "seed_1000.csv")])

    run([sys.executable, os.path.join(ROOT, "e4_scale_access_gas.py"),
         "--base-url", base_url,
         "--samples", "400",
         "--output", os.path.join(args.results_dir, "access_gas_1000.csv")])

    # Stage 3: revocation effectiveness
    run([sys.executable, os.path.join(ROOT, "e4_revocation_test.py"),
         "--base-url", base_url,
         "--output", os.path.join(args.results_dir, "revocation_summary.csv")])

    print("\nE4 complete. Outputs in", out_dir)


if __name__ == "__main__":
    main()
