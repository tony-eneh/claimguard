#!/usr/bin/env python3
import argparse
import asyncio
import csv
import json
import time
from typing import Any, Dict, List, Optional

import aiohttp


def load_subjects(path: str) -> List[Dict[str, Any]]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_resources(path: str) -> List[Dict[str, Any]]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


async def post(session: aiohttp.ClientSession, url: str, body: Dict[str, Any]) -> Dict[str, Any]:
    async with session.post(url, json=body) as resp:
        data = {}
        try:
            data = await resp.json()
        except Exception:
            pass
        return {"status": resp.status, **data}


async def main_async(args):
    base = args.base_url.rstrip("/")
    subjects = load_subjects(args.subjects)
    resources = load_resources(args.resources)

    # Pick an ADJUSTER and a MEDICAL_REPORT resource (sensitivity=5)
    subj = next(s for s in subjects if s.get("role") == "ADJUSTER")
    res = next(r for r in resources if r.get("rType") == "MEDICAL_REPORT")

    timeout = aiohttp.ClientTimeout(total=args.timeout)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        # 1) Verify baseline is denied (Adjuster READ on sensitivity 5)
        access_body = {"subject": subj["address"], "resourceId": res["resourceId"], "action": 0}
        a1 = await post(session, f"{base}/access", access_body)
        baseline_allowed = bool(a1.get("allowed", False))
        print(f"Baseline allowed={baseline_allowed}")

        # 2) Create a narrow policy to allow this exact caseId/type/sensitivity
        now_ts = int(time.time())
        create_body = {
            "role": 4,  # ADJUSTER
            "orgId": "0x0",
            "jurisdiction": "0x0",
            "rType": 2,  # MEDICAL_REPORT
            "caseId": res.get("caseId", "0x0"),
            "action": 0,  # READ
            "maxSensitivity": 5,
            "notBefore": 0,
            "notAfter": 0,
            "allow": True,
        }
        c = await post(session, f"{base}/policy", create_body)
        if c.get("status") != 200:
            raise RuntimeError(f"Failed to create policy: {c}")
        policy_id: Optional[int] = c.get("policyId")
        print(f"Created policyId={policy_id}")

        # 3) Poll until access becomes allowed
        t_start_allow = time.time()
        allow_delay_ms: Optional[float] = None
        for _ in range(args.poll_iters):
            a = await post(session, f"{base}/access", access_body)
            if bool(a.get("allowed", False)):
                allow_delay_ms = (time.time() - t_start_allow) * 1000.0
                break
            await asyncio.sleep(args.poll_interval)

        # 4) Revoke the policy
        if policy_id is None:
            # fallback: nothing to revoke
            raise RuntimeError("No policyId returned to revoke")
        r = await post(session, f"{base}/policy/revoke", {"policyId": policy_id})
        if r.get("status") != 200:
            raise RuntimeError(f"Failed to revoke policy: {r}")

        # 5) Poll until access becomes denied
        t_start_deny = time.time()
        deny_delay_ms: Optional[float] = None
        for _ in range(args.poll_iters):
            a = await post(session, f"{base}/access", access_body)
            if not bool(a.get("allowed", False)):
                deny_delay_ms = (time.time() - t_start_deny) * 1000.0
                break
            await asyncio.sleep(args.poll_interval)

    # Write summary CSV
    with open(args.output, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["baseline_allowed", "allow_delay_ms", "deny_delay_ms", "policy_id", "subject", "resourceId"]) 
        w.writeheader()
        w.writerow({
            "baseline_allowed": baseline_allowed,
            "allow_delay_ms": f"{allow_delay_ms:.3f}" if allow_delay_ms is not None else "",
            "deny_delay_ms": f"{deny_delay_ms:.3f}" if deny_delay_ms is not None else "",
            "policy_id": policy_id,
            "subject": subj["address"],
            "resourceId": res["resourceId"],
        })
    print(f"Wrote {args.output}")


def parse_args():
    p = argparse.ArgumentParser(description="E4: revocation effectiveness test")
    p.add_argument("--base-url", type=str, default="http://localhost:4000/api")
    p.add_argument("--subjects", type=str, default="outputs/subjects.json")
    p.add_argument("--resources", type=str, default="outputs/resources.json")
    p.add_argument("--poll-iters", type=int, default=60)
    p.add_argument("--poll-interval", type=float, default=0.5)
    p.add_argument("--timeout", type=int, default=60)
    p.add_argument("--output", type=str, default="experiment_results/e4/revocation_summary.csv")
    return p.parse_args()


def main():
    args = parse_args()
    asyncio.run(main_async(args))


if __name__ == "__main__":
    main()
