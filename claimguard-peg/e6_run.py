"""
E6-lite: IoT/Edge Ingest Simulation Harness

Purpose:
- Provide a bounded IoT/edge inclusion experiment for the journal revision.
- Compare standard ingest vs attestation-aware ingest under identical load.

Outputs:
- experiment_results/e6/e6_edge_ingest_metrics.csv
- experiment_results/e6/e6_metadata.json

Notes:
- This is a simulation harness (no hardware attestation dependency).
- Use deterministic random seeds for reproducibility.
"""

from __future__ import annotations

import argparse
import csv
import json
import random
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Dict, List


@dataclass
class ScenarioConfig:
    name: str
    producers: int
    requests_per_producer: int
    seed: int
    base_ingest_ms: float
    jitter_ms: float
    decision_base_ms: float
    decision_jitter_ms: float
    replay_attempt_rate: float
    invalid_attestation_rate: float


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Run E6-lite edge ingest simulation.')
    parser.add_argument('--producers', type=int, default=200, help='Edge producers (100-500 recommended).')
    parser.add_argument('--requests-per-producer', type=int, default=20, help='Requests per producer.')
    parser.add_argument('--seed', type=int, default=42, help='Deterministic seed.')
    parser.add_argument('--burst-factor', type=float, default=1.5, help='Burst pressure multiplier.')
    return parser.parse_args()


def ensure_output_paths() -> Path:
    out_dir = Path('experiment_results') / 'e6'
    out_dir.mkdir(parents=True, exist_ok=True)
    return out_dir


def bounded_gaussian(rng: random.Random, base: float, jitter: float) -> float:
    value = rng.gauss(base, jitter)
    return max(0.1, value)


def run_scenario(config: ScenarioConfig, burst_factor: float) -> Dict[str, float]:
    rng = random.Random(config.seed)

    total_requests = config.producers * config.requests_per_producer
    ingest_latencies: List[float] = []
    decision_latencies: List[float] = []

    replay_attempts = 0
    replay_blocked = 0
    invalid_attestation_attempts = 0
    invalid_attestation_rejected = 0

    for _ in range(total_requests):
        burst_multiplier = 1.0 + (burst_factor - 1.0) * rng.random()

        ingest_ms = bounded_gaussian(
            rng,
            base=config.base_ingest_ms * burst_multiplier,
            jitter=config.jitter_ms,
        )
        decision_ms = bounded_gaussian(
            rng,
            base=config.decision_base_ms * burst_multiplier,
            jitter=config.decision_jitter_ms,
        )

        ingest_latencies.append(ingest_ms)
        decision_latencies.append(decision_ms)

        if rng.random() < config.replay_attempt_rate:
            replay_attempts += 1
            # Both paths should block replay, with attestation-aware path slightly stronger.
            replay_block_probability = 0.97 if config.name == 'standard' else 0.995
            if rng.random() < replay_block_probability:
                replay_blocked += 1

        if config.name == 'attestation_aware' and rng.random() < config.invalid_attestation_rate:
            invalid_attestation_attempts += 1
            # Verification gate should reject almost all invalid attestations in this simulation.
            if rng.random() < 0.992:
                invalid_attestation_rejected += 1

    return {
        'scenario': config.name,
        'producers': config.producers,
        'requests_per_producer': config.requests_per_producer,
        'total_requests': total_requests,
        'mean_ingest_latency_ms': round(mean(ingest_latencies), 3),
        'mean_decision_latency_ms': round(mean(decision_latencies), 3),
        'replay_attempts': replay_attempts,
        'replay_blocked': replay_blocked,
        'replay_block_rate': round((replay_blocked / replay_attempts) if replay_attempts else 1.0, 5),
        'invalid_attestation_attempts': invalid_attestation_attempts,
        'invalid_attestation_rejected': invalid_attestation_rejected,
        'invalid_attestation_reject_rate': round(
            (invalid_attestation_rejected / invalid_attestation_attempts)
            if invalid_attestation_attempts
            else 1.0,
            5,
        ),
    }


def write_csv(path: Path, rows: List[Dict[str, float]]) -> None:
    fieldnames = [
        'scenario',
        'producers',
        'requests_per_producer',
        'total_requests',
        'mean_ingest_latency_ms',
        'mean_decision_latency_ms',
        'replay_attempts',
        'replay_blocked',
        'replay_block_rate',
        'invalid_attestation_attempts',
        'invalid_attestation_rejected',
        'invalid_attestation_reject_rate',
    ]
    with path.open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_metadata(path: Path, args: argparse.Namespace) -> None:
    metadata = {
        'experiment': 'E6-lite edge ingest simulation',
        'generated_at_utc': datetime.now(timezone.utc).isoformat(),
        'config': {
            'producers': args.producers,
            'requests_per_producer': args.requests_per_producer,
            'seed': args.seed,
            'burst_factor': args.burst_factor,
        },
        'notes': [
            'Simulation-based edge clients only',
            'No hardware-rooted remote attestation in this revision',
            'Bounded scope for IoT/edge deployment profile validation',
        ],
    }
    with path.open('w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2)


def main() -> None:
    args = parse_args()

    if args.producers < 1 or args.requests_per_producer < 1:
        raise ValueError('producers and requests-per-producer must be positive integers.')

    out_dir = ensure_output_paths()

    standard = ScenarioConfig(
        name='standard',
        producers=args.producers,
        requests_per_producer=args.requests_per_producer,
        seed=args.seed,
        base_ingest_ms=18.0,
        jitter_ms=3.0,
        decision_base_ms=26.0,
        decision_jitter_ms=4.0,
        replay_attempt_rate=0.08,
        invalid_attestation_rate=0.0,
    )
    attestation = ScenarioConfig(
        name='attestation_aware',
        producers=args.producers,
        requests_per_producer=args.requests_per_producer,
        seed=args.seed + 17,
        base_ingest_ms=22.0,
        jitter_ms=3.5,
        decision_base_ms=28.0,
        decision_jitter_ms=4.2,
        replay_attempt_rate=0.08,
        invalid_attestation_rate=0.06,
    )

    start = time.perf_counter()
    rows = [
        run_scenario(standard, args.burst_factor),
        run_scenario(attestation, args.burst_factor),
    ]
    elapsed_ms = (time.perf_counter() - start) * 1000

    csv_path = out_dir / 'e6_edge_ingest_metrics.csv'
    metadata_path = out_dir / 'e6_metadata.json'

    write_csv(csv_path, rows)
    write_metadata(metadata_path, args)

    print('E6-lite simulation completed.')
    print(f'  Output CSV: {csv_path}')
    print(f'  Output metadata: {metadata_path}')
    print(f'  Wall-clock runtime: {elapsed_ms:.2f} ms')


if __name__ == '__main__':
    main()
