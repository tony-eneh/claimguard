"""
Analyze E6-lite edge ingest simulation results.

Reads:
- experiment_results/e6/e6_edge_ingest_metrics.csv

Writes:
- papers/2_journal/artifacts/experiments/e6_summary.json
- papers/2_journal/artifacts/tables/e6_metrics_table.md
"""

from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List


def read_metrics(path: Path) -> List[Dict[str, float]]:
    rows: List[Dict[str, float]] = []
    with path.open('r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append({
                'scenario': row['scenario'],
                'producers': int(row['producers']),
                'requests_per_producer': int(row['requests_per_producer']),
                'total_requests': int(row['total_requests']),
                'mean_ingest_latency_ms': float(row['mean_ingest_latency_ms']),
                'mean_decision_latency_ms': float(row['mean_decision_latency_ms']),
                'replay_attempts': int(row['replay_attempts']),
                'replay_blocked': int(row['replay_blocked']),
                'replay_block_rate': float(row['replay_block_rate']),
                'invalid_attestation_attempts': int(row['invalid_attestation_attempts']),
                'invalid_attestation_rejected': int(row['invalid_attestation_rejected']),
                'invalid_attestation_reject_rate': float(row['invalid_attestation_reject_rate']),
            })
    return rows


def find_scenario(rows: List[Dict[str, float]], name: str) -> Dict[str, float]:
    for row in rows:
        if row['scenario'] == name:
            return row
    raise ValueError(f'Scenario not found: {name}')


def to_percent(value: float) -> float:
    return round(value * 100.0, 2)


def main() -> None:
    metrics_path = Path('experiment_results/e6/e6_edge_ingest_metrics.csv')
    if not metrics_path.exists():
        raise FileNotFoundError(
            'Missing E6 metrics CSV. Run: python claimguard-peg/e6_run.py'
        )

    rows = read_metrics(metrics_path)
    standard = find_scenario(rows, 'standard')
    attested = find_scenario(rows, 'attestation_aware')

    ingest_overhead_ms = round(
        attested['mean_ingest_latency_ms'] - standard['mean_ingest_latency_ms'],
        3,
    )
    decision_latency_under_burst_ms = round(attested['mean_decision_latency_ms'], 3)

    summary = {
        'generated_at_utc': datetime.now(timezone.utc).isoformat(),
        'input_file': str(metrics_path),
        'four_required_metrics': {
            'ingest_latency_overhead_ms': ingest_overhead_ms,
            'replay_block_rate_percent_attestation_aware': to_percent(attested['replay_block_rate']),
            'invalid_attestation_reject_rate_percent': to_percent(attested['invalid_attestation_reject_rate']),
            'decision_latency_under_burst_ms_attestation_aware': decision_latency_under_burst_ms,
        },
        'raw': {
            'standard': standard,
            'attestation_aware': attested,
        },
        'limitations': [
            'Simulation-based edge clients only',
            'No hardware-rooted attestation in this revision',
            'Bounded IoT/edge profile (not a general IoT framework)',
        ],
    }

    summary_dir = Path('papers/2_journal/artifacts/experiments')
    table_dir = Path('papers/2_journal/artifacts/tables')
    summary_dir.mkdir(parents=True, exist_ok=True)
    table_dir.mkdir(parents=True, exist_ok=True)

    summary_path = summary_dir / 'e6_summary.json'
    with summary_path.open('w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2)

    table_path = table_dir / 'e6_metrics_table.md'
    with table_path.open('w', encoding='utf-8') as f:
        f.write('# E6-lite Metrics (IoT/Edge Deployment Profile)\n\n')
        f.write('| Metric | Value |\n')
        f.write('|---|---:|\n')
        f.write(f"| Ingest latency overhead (attestation-aware - standard), ms | {ingest_overhead_ms} |\n")
        f.write(
            f"| Replay block rate (attestation-aware), % | "
            f"{to_percent(attested['replay_block_rate'])} |\n"
        )
        f.write(
            f"| Invalid attestation reject rate, % | "
            f"{to_percent(attested['invalid_attestation_reject_rate'])} |\n"
        )
        f.write(
            f"| Decision latency under burst (attestation-aware), ms | "
            f"{decision_latency_under_burst_ms} |\n"
        )

    print('E6 analysis completed.')
    print(f'  Summary JSON: {summary_path}')
    print(f'  Metrics table: {table_path}')


if __name__ == '__main__':
    main()
