#!/usr/bin/env python3
import argparse
import asyncio
import csv
import json
import random
import time
from typing import Any, Dict, List

import aiohttp


def load_subjects(path: str) -> List[Dict[str, Any]]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_resources(path: str) -> List[Dict[str, Any]]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


async def sample_once(session: aiohttp.ClientSession, base_url: str, subjects, resources, action: int) -> Dict[str, Any]:
    subj = random.choice(subjects)
    res = random.choice(resources)
    body = {"subject": subj["address"], "resourceId": res["resourceId"], "action": action}

    start = time.time()
    async with session.post(f"{base_url}/measure/check-access", json=body) as resp:
        end = time.time()
        data = {}
        try:
            data = await resp.json()
        except Exception:
            pass
        return {
            "status": resp.status,
            "latency_ms": data.get("latencyMs"),
            "gas_estimate": data.get("gasEstimate"),
            "allowed": data.get("allowed"),
            "subject": subj["address"],
            "resourceId": res["resourceId"],
            "action": action,
            "rt_ms": f"{(end - start) * 1000.0:.3f}",
        }


async def main_async(args):
    subjects = load_subjects(args.subjects)
    resources = load_resources(args.resources)
    base = args.base_url.rstrip("/")
    results: List[Dict[str, Any]] = []

    timeout = aiohttp.ClientTimeout(total=args.timeout)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        for i in range(args.samples):
            r = await sample_once(session, base, subjects, resources, args.action)
            results.append(r)
            if args.sleep > 0:
                await asyncio.sleep(args.sleep)

    with open(args.output, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(
            f,
            fieldnames=[
                "status",
                "latency_ms",
                "gas_estimate",
                "allowed",
                "subject",
                "resourceId",
                "action",
                "rt_ms",
            ],
        )
        w.writeheader()
        w.writerows(results)
    print(f"Wrote {args.output}")


def parse_args():
    p = argparse.ArgumentParser(description="E4: sample check-access gas/latency under current policy count")
    p.add_argument("--base-url", type=str, default="http://localhost:4000/api")
    p.add_argument("--subjects", type=str, default="outputs/subjects.json")
    p.add_argument("--resources", type=str, default="outputs/resources.json")
    p.add_argument("--samples", type=int, default=200)
    p.add_argument("--sleep", type=float, default=0.0)
    p.add_argument("--action", type=int, default=0, help="Action enum value (READ=0)")
    p.add_argument("--timeout", type=int, default=30)
    p.add_argument("--output", type=str, default="experiment_results/e4/access_gas.csv")
    return p.parse_args()


def main():
    args = parse_args()
    asyncio.run(main_async(args))


if __name__ == "__main__":
    main()
