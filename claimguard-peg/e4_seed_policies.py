#!/usr/bin/env python3
import argparse
import asyncio
import csv
import json
import random
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

import aiohttp


def build_random_policy(now_ts: int) -> Dict[str, Any]:
    role = random.choice([2, 4, 5, 6, 7, 8])  # INSURER..REGULATOR
    r_type = random.choice([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    action = random.choice([0])  # READ focus
    max_sensitivity = random.choice([2, 3, 4, 5])
    # mostly wildcards
    org_id = "0x0"
    jurisdiction = "0x0"
    case_id = "0x0"
    if random.random() < 0.2:
        # add a bounded time window in 10% of rules
        not_before = now_ts
        not_after = now_ts + (7 * 24 * 60 * 60)
    else:
        not_before = 0
        not_after = 0
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
        "allow": True,
    }


async def create_policy(session: aiohttp.ClientSession, base_url: str, idx: int) -> Dict[str, Any]:
    now_ts = int(time.time())
    body = build_random_policy(now_ts)
    start = time.time()
    async with session.post(f"{base_url}/policy", json=body) as resp:
        end = time.time()
        latency_ms = (end - start) * 1000.0
        data = {}
        try:
            data = await resp.json()
        except Exception:
            pass
        return {
            "index": idx,
            "status": resp.status,
            "latency_ms": f"{latency_ms:.3f}",
            "tx_hash": data.get("txHash"),
            "gas_used": data.get("gasUsed"),
            "policy_id": data.get("policyId"),
            "error": None if resp.status == 200 else json.dumps(data),
        }


async def get_policy_count(session: aiohttp.ClientSession, base_url: str) -> int:
    async with session.get(f"{base_url}/policy/count") as resp:
        data = await resp.json()
        return int(data.get("nextPolicyId", 1)) - 1


async def main_async(args):
    base = args.base_url.rstrip("/")
    out = args.output
    target = args.target
    concurrency = args.concurrency
    rate = args.rate  # updates per second, 0 for unlimited burst
    results: List[Dict[str, Any]] = []

    timeout = aiohttp.ClientTimeout(total=args.timeout)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        current = await get_policy_count(session, base)
        print(f"Existing policies on-chain: {current}")
        to_create = max(0, target - current)
        if to_create == 0:
            print("No additional policies needed.")
        else:
            print(f"Creating {to_create} additional policies to reach {target}...")

        q: asyncio.Queue = asyncio.Queue()
        for i in range(to_create):
            await q.put(i)

        async def worker(name: str):
            last_sent: Optional[float] = None
            while not q.empty():
                try:
                    i = q.get_nowait()
                except asyncio.QueueEmpty:
                    return
                # simple rate limiter
                if rate > 0:
                    now = time.time()
                    if last_sent is not None:
                        min_interval = 1.0 / rate
                        sleep_for = (last_sent + min_interval) - now
                        if sleep_for > 0:
                            await asyncio.sleep(sleep_for)
                    last_sent = time.time()
                r = await create_policy(session, base, int(i))
                results.append({"worker": name, **r})

        workers = [asyncio.create_task(worker(f"w{k}")) for k in range(concurrency)]
        t0 = time.time()
        await asyncio.gather(*workers)
        t1 = time.time()
        print(f"Created {len(results)} policies in {(t1 - t0):.2f}s")

    # write CSV
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(
            f,
            fieldnames=[
                "worker",
                "index",
                "status",
                "latency_ms",
                "tx_hash",
                "gas_used",
                "policy_id",
                "error",
            ],
        )
        w.writeheader()
        w.writerows(results)
    print(f"Wrote {out}")


def parse_args():
    p = argparse.ArgumentParser(description="E4: seed policies to target count with optional rate limiting")
    p.add_argument("--base-url", type=str, default="http://localhost:4000/api")
    p.add_argument("--target", type=int, default=100)
    p.add_argument("--concurrency", type=int, default=4)
    p.add_argument("--rate", type=float, default=0.0, help="updates per second; 0 = unlimited")
    p.add_argument("--timeout", type=int, default=120)
    p.add_argument("--output", type=str, default="experiment_results/e4/policy_seed.csv")
    return p.parse_args()


def main():
    args = parse_args()
    asyncio.run(main_async(args))


if __name__ == "__main__":
    main()
