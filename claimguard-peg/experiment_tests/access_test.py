#!/usr/bin/env python3
import argparse
import asyncio
import csv
import json
import random
import time
from datetime import datetime
from typing import List, Dict, Any

import aiohttp


def load_subjects(path: str) -> List[Dict[str, Any]]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_resources(path: str) -> List[Dict[str, Any]]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


async def worker(
    name: str,
    session: aiohttp.ClientSession,
    base_url: str,
    subjects: List[Dict[str, Any]],
    resources: List[Dict[str, Any]],
    actions: List[str],
    requests_queue: asyncio.Queue,
    results: List[Dict[str, Any]],
):
    while True:
        try:
            _ = requests_queue.get_nowait()
        except asyncio.QueueEmpty:
            return

        subj = random.choice(subjects)
        res = random.choice(resources)
        action = random.choice(actions)

        payload = {
            "subject": subj["address"],
            "resourceId": res["resourceId"],
            "action": action,
        }

        start_ts = time.time()
        start_iso = datetime.utcfromtimestamp(start_ts).isoformat() + "Z"

        status = None
        allowed = None
        error = None

        try:
            async with session.post(f"{base_url}/access", json=payload) as resp:
                status = resp.status
                try:
                    data = await resp.json()
                except Exception:
                    data = {}

                # Our PEG returns { allowed: bool, capability: {...} } on success
                if status == 200 and isinstance(data, dict):
                    allowed = data.get("allowed")
                elif status == 403:
                    # may include {allowed: false, reason: "..."}
                    allowed = False
                else:
                    allowed = None

        except Exception as e:
            error = str(e)

        end_ts = time.time()
        latency_ms = (end_ts - start_ts) * 1000.0

        results.append(
            {
                "worker": name,
                "start_time_iso": start_iso,
                "latency_ms": f"{latency_ms:.3f}",
                "status": status,
                "allowed": allowed,
                "subject_address": subj["address"],
                "subject_role": subj.get("role"),
                "resource_id": res["resourceId"],
                "resource_type": res.get("rType"),
                "resource_sensitivity": res.get("sensitivity"),
                "action": action,
                "error": error,
            }
        )


async def main_async(args):
    subjects = load_subjects(args.subjects)
    resources = load_resources(args.resources)

    if not subjects:
        raise RuntimeError("No subjects loaded")
    if not resources:
        raise RuntimeError("No resources loaded")

    actions = args.actions
    print(f"Loaded {len(subjects)} subjects, {len(resources)} resources.")
    print(f"Using actions: {actions}")
    print(f"Total requests: {args.requests}, concurrency: {args.concurrency}")

    # Populate queue with N items – each item represents one request to perform
    requests_queue: asyncio.Queue = asyncio.Queue()
    for _ in range(args.requests):
        await requests_queue.put(1)

    results: List[Dict[str, Any]] = []

    timeout = aiohttp.ClientTimeout(total=args.timeout)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        workers = []
        for i in range(args.concurrency):
            w = asyncio.create_task(
                worker(
                    name=f"w{i}",
                    session=session,
                    base_url=args.base_url.rstrip("/"),
                    subjects=subjects,
                    resources=resources,
                    actions=actions,
                    requests_queue=requests_queue,
                    results=results,
                )
            )
            workers.append(w)

        start_all = time.time()
        await asyncio.gather(*workers)
        end_all = time.time()

    duration = end_all - start_all
    print(f"Completed {len(results)} requests in {duration:.3f} seconds.")
    if results:
        avg_latency = sum(float(r["latency_ms"])
                          for r in results) / len(results)
        print(f"Average latency: {avg_latency:.2f} ms")

        allowed_count = sum(1 for r in results if r["allowed"] is True)
        denied_count = sum(1 for r in results if r["allowed"] is False)
        print(f"Allowed: {allowed_count}, Denied: {denied_count}")

    # Write CSV
    out_path = args.output
    with open(out_path, "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = [
            "worker",
            "start_time_iso",
            "latency_ms",
            "status",
            "allowed",
            "subject_address",
            "subject_role",
            "resource_id",
            "resource_type",
            "resource_sensitivity",
            "action",
            "error",
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"Results written to {out_path}")


def parse_args():
    parser = argparse.ArgumentParser(
        description="ClaimGuard access load tester")
    parser.add_argument(
        "--subjects",
        type=str,
        default="./claimguard-peg/outputs/subjects.json",
        help="Path to subjects.json",
    )
    parser.add_argument(
        "--resources",
        type=str,
        default="./claimguard-peg/outputs/resources.json",
        help="Path to resources.json",
    )
    parser.add_argument(
        "--base-url",
        type=str,
        default="http://localhost:4000/api",
        help="Base URL of the PEG (without trailing slash)",
    )
    parser.add_argument(
        "--requests",
        type=int,
        default=1000,
        help="Total number of requests to perform",
    )
    parser.add_argument(
        "--concurrency",
        type=int,
        default=100,
        help="Number of concurrent workers",
    )
    parser.add_argument(
        "--actions",
        nargs="+",
        default=["READ"],
        help="List of actions to randomly choose from (e.g. READ APPEND UPDATE)",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=10,
        help="Request timeout in seconds",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="results.csv",
        help="Output CSV file",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    asyncio.run(main_async(args))


if __name__ == "__main__":
    main()
