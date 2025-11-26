#!/usr/bin/env python3
import argparse
import asyncio
import csv
import random
import time
from datetime import datetime
from typing import List, Dict, Any

import aiohttp


def build_random_policy(now_ts: int) -> Dict[str, Any]:
    """
    Build a random-ish policy update.
    For the experiment, we don't need semantic variety; just enough
    variation to avoid exact duplicates.
    """

    # Role / rType / action as numbers to match Solidity enums
    # You can tweak these ranges to match your actual enums
    role = random.choice([2, 4, 5, 6])  # e.g. INSURER, ADJUSTER, POLICE, COURT
    # GENERIC, MEDICAL_REPORT, IMAGE, VIDEO, TELEMATICS
    r_type = random.choice([0, 2, 5, 6, 8])
    action = random.choice([0, 1, 2])  # READ, APPEND, UPDATE

    max_sensitivity = random.choice([2, 3, 4, 5])

    # You can either use wildcard (0x0) or random-ish bytes32
    org_id = "0x0"
    jurisdiction = "0x0"
    case_id = "0x0"

    # Time window: valid from now to now + 30 days, or 0 / 0 for any
    if random.random() < 0.5:
        not_before = 0
        not_after = 0
    else:
        not_before = now_ts
        not_after = now_ts + (30 * 24 * 60 * 60)

    allow = True

    return {
        "role": role,
        "orgId": org_id,
        "jurisdiction": jurisdiction,
        "rType": r_type,
        "caseId": case_id,
        "action": action,
        "maxSensitivity": max_sensitivity,
        "notBefore": not_before,
        "notAfter": not_after,
        "allow": allow,
    }


async def worker(
    name: str,
    session: aiohttp.ClientSession,
    base_url: str,
    requests_queue: asyncio.Queue,
    results: List[Dict[str, Any]],
):
    while True:
        try:
            idx = requests_queue.get_nowait()
        except asyncio.QueueEmpty:
            return

        now_ts = int(time.time())
        policy_body = build_random_policy(now_ts)

        start_ts = time.time()
        start_iso = datetime.utcfromtimestamp(start_ts).isoformat() + "Z"

        status = None
        latency_ms = None
        tx_hash = None
        gas_used = None
        block_number = None
        error = None

        try:
            async with session.post(f"{base_url}/policy", json=policy_body) as resp:
                status = resp.status
                end_ts = time.time()
                latency_ms = (end_ts - start_ts) * 1000.0

                try:
                    data = await resp.json()
                except Exception:
                    data = {}

                if status == 200 and isinstance(data, dict):
                    tx_hash = data.get("txHash")
                    gas_used = data.get("gasUsed")
                    block_number = data.get("blockNumber")
                else:
                    error = f"Unexpected status {status}, body={data}"
        except Exception as e:
            end_ts = time.time()
            latency_ms = (end_ts - start_ts) * 1000.0
            error = str(e)

        results.append(
            {
                "worker": name,
                "index": idx,
                "start_time_iso": start_iso,
                "latency_ms": f"{latency_ms:.3f}" if latency_ms is not None else "",
                "status": status,
                "tx_hash": tx_hash,
                "gas_used": gas_used,
                "block_number": block_number,
                "error": error,
            }
        )


async def main_async(args):
    requests_queue: asyncio.Queue = asyncio.Queue()
    for i in range(args.count):
        await requests_queue.put(i)

    results: List[Dict[str, Any]] = []

    timeout = aiohttp.ClientTimeout(total=args.timeout)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        workers = []
        base_url = args.base_url.rstrip("/")
        for i in range(args.concurrency):
            w = asyncio.create_task(
                worker(
                    name=f"w{i}",
                    session=session,
                    base_url=base_url,
                    requests_queue=requests_queue,
                    results=results,
                )
            )
            workers.append(w)

        start_all = time.time()
        await asyncio.gather(*workers)
        end_all = time.time()

    duration = end_all - start_all
    print(
        f"Completed {len(results)} policy updates in {duration:.3f} seconds.")

    if results:
        latencies = [float(r["latency_ms"])
                     for r in results if r["latency_ms"]]
        if latencies:
            avg_lat = sum(latencies) / len(latencies)
            print(f"Average confirmation latency: {avg_lat:.2f} ms")
            print(f"Min: {min(latencies):.2f} ms, Max: {max(latencies):.2f} ms")

    # Write CSV
    out_path = args.output
    with open(out_path, "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = [
            "worker",
            "index",
            "start_time_iso",
            "latency_ms",
            "status",
            "tx_hash",
            "gas_used",
            "block_number",
            "error",
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"Results written to {out_path}")


def parse_args():
    parser = argparse.ArgumentParser(
        description="ClaimGuard policy update benchmark")
    parser.add_argument(
        "--base-url",
        type=str,
        default="http://localhost:4000/api",
        help="Base URL of the PEG (without trailing slash)",
    )
    parser.add_argument(
        "--count",
        type=int,
        default=50,
        help="Number of policy updates to send",
    )
    parser.add_argument(
        "--concurrency",
        type=int,
        default=1,
        help="Number of concurrent workers (1 = sequential)",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=60,
        help="Request timeout in seconds",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="policy_updates.csv",
        help="Output CSV file for results",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    asyncio.run(main_async(args))


if __name__ == "__main__":
    main()
