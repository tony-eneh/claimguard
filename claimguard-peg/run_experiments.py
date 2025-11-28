#!/usr/bin/env python
"""
Run ClaimGuard experiments and save raw result CSVs.

Assumes (relative to repo root):
  - claimguard-peg/experiment_tests/access_test.py
  - claimguard-peg/experiment_tests/policy_update_test.py
  - claimguard-peg/outputs/subjects.json
  - claimguard-peg/outputs/resources.json
  - results go to claimguard-peg/experiment_results/

Usage (from repo root):
  python claimguard-peg/run_experiments.py
"""

import os
import sys
import subprocess

# ---------- CONFIG ---------------------------------------------------------

LATENCY_REQUESTS = [50, 100, 200, 500]
LATENCY_CONCURRENCY = 10

THROUGHPUT_TOTAL_REQUESTS = 1000
THROUGHPUT_CONCURRENCY = [10, 50, 100, 200]

POLICY_UPDATE_COUNT = 10

BASE_URL = os.environ.get("CLAIMGUARD_BASE_URL", "http://localhost:4000/api")

# ---------- PATHS ----------------------------------------------------------

# ROOT is claimguard-peg/
ROOT = os.path.dirname(os.path.abspath(__file__))

TEST_DIR = os.path.join(ROOT, "experiment_tests")
RESULT_DIR = os.path.join(ROOT, "experiment_results")
OUTPUT_DIR = os.path.join(ROOT, "outputs")

ACCESS_TEST = os.path.join(TEST_DIR, "access_test.py")
POLICY_TEST = os.path.join(TEST_DIR, "policy_update_test.py")

SUBJECTS_JSON = os.path.join(OUTPUT_DIR, "subjects.json")
RESOURCES_JSON = os.path.join(OUTPUT_DIR, "resources.json")

PY_EXE = sys.executable or "python"


def run(cmd: list[str]) -> None:
    print("\n>>> Running:", " ".join(cmd))
    proc = subprocess.run(cmd, cwd=ROOT)
    if proc.returncode != 0:
        print(
            f"!!! Command failed with code {proc.returncode}", file=sys.stderr)
        sys.exit(proc.returncode)


def ensure_paths() -> None:
    if not os.path.exists(ACCESS_TEST):
        print(f"Cannot find access_test.py at {ACCESS_TEST}", file=sys.stderr)
        sys.exit(1)
    if not os.path.exists(POLICY_TEST):
        print(
            f"Cannot find policy_update_test.py at {POLICY_TEST}", file=sys.stderr)
        sys.exit(1)
    if not os.path.exists(SUBJECTS_JSON):
        print(f"Cannot find subjects.json at {SUBJECTS_JSON}", file=sys.stderr)
        sys.exit(1)
    if not os.path.exists(RESOURCES_JSON):
        print(
            f"Cannot find resources.json at {RESOURCES_JSON}", file=sys.stderr)
        sys.exit(1)
    os.makedirs(RESULT_DIR, exist_ok=True)


def run_latency_tests() -> None:
    print("\n=== Latency tests ===")
    # paths relative to ROOT so they look nice in logs
    subjects_rel = os.path.relpath(
        SUBJECTS_JSON, ROOT)   # "outputs/subjects.json"
    resources_rel = os.path.relpath(
        RESOURCES_JSON, ROOT)  # "outputs/resources.json"

    for n in LATENCY_REQUESTS:
        out_rel = f"experiment_results/latency_read_n{n}_c{LATENCY_CONCURRENCY}.csv"
        cmd = [
            PY_EXE,
            ACCESS_TEST,
            "--requests", str(n),
            "--concurrency", str(LATENCY_CONCURRENCY),
            "--actions", "READ",
            "--subjects", subjects_rel,
            "--resources", resources_rel,
            "--output", out_rel,
            "--base-url", BASE_URL,
        ]
        run(cmd)


def run_throughput_tests() -> None:
    print("\n=== Throughput tests ===")
    subjects_rel = os.path.relpath(SUBJECTS_JSON, ROOT)
    resources_rel = os.path.relpath(RESOURCES_JSON, ROOT)

    for c in THROUGHPUT_CONCURRENCY:
        out_rel = f"experiment_results/throughput_read_n{THROUGHPUT_TOTAL_REQUESTS}_c{c}.csv"
        cmd = [
            PY_EXE,
            ACCESS_TEST,
            "--requests", str(THROUGHPUT_TOTAL_REQUESTS),
            "--concurrency", str(c),
            "--actions", "READ",
            "--subjects", subjects_rel,
            "--resources", resources_rel,
            "--output", out_rel,
            "--base-url", BASE_URL,
        ]
        run(cmd)


def run_policy_update_tests() -> None:
    print("\n=== Policy update tests ===")
    out_rel = f"experiment_results/policy_updates_{POLICY_UPDATE_COUNT}.csv"
    cmd = [
        PY_EXE,
        POLICY_TEST,
        "--count", str(POLICY_UPDATE_COUNT),
        "--output", out_rel,
        "--base-url", BASE_URL,
    ]
    run(cmd)


if __name__ == "__main__":
    ensure_paths()
    run_latency_tests()
    run_throughput_tests()
    run_policy_update_tests()
    print("\nAll experiments finished. CSVs are in claimguard-peg/experiment_results/")
