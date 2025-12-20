#!/usr/bin/env python3
"""
E2: Realistic Blockchain / Network Conditions
Re-runs E1 experiments with contracts on Sepolia to measure real blockchain latency impact.

Metrics:
- Access latency (P50/P90/P99) with RPC round-trip
- Throughput under real block timing
- Policy update confirmation time
"""

import asyncio
import aiohttp
import time
import json
import os
import argparse
from pathlib import Path
from typing import List, Dict, Any
import statistics

BASE_URL = "http://127.0.0.1:4000/api"

class E2Tester:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.results: Dict[str, Any] = {}
        
    async def test_access_latency(self, samples: int = 100):
        """
        Test access latency under real blockchain conditions.
        Measures end-to-end time including RPC round-trip and on-chain evaluation.
        """
        print(f"\n[E2-1] Testing Access Latency ({samples} samples)...")
        
        latencies = []
        valid_subject = "0x1234567890123456789012345678901234567890"
        
        async with aiohttp.ClientSession() as session:
            for i in range(samples):
                resource_id = (i % 100) + 1  # Cycle through resources
                
                start_time = time.time()
                try:
                    resp = await session.post(
                        f"{self.base_url}/access",
                        json={
                            "subject": valid_subject,
                            "resourceId": resource_id,
                            "action": "READ"
                        },
                        timeout=aiohttp.ClientTimeout(total=30)
                    )
                    end_time = time.time()
                    latency_ms = (end_time - start_time) * 1000
                    
                    if resp.status in [200, 403]:  # Both valid responses
                        latencies.append(latency_ms)
                    
                    if (i + 1) % 20 == 0:
                        print(f"  -> {i + 1}/{samples} samples collected")
                    
                except Exception as e:
                    print(f"  Error on sample {i+1}: {e}")
                    continue
        
        if not latencies:
            print("  ✗ No valid latency samples collected")
            return {}
        
        # Compute percentiles
        latencies_sorted = sorted(latencies)
        p50 = statistics.median(latencies_sorted)
        p90 = latencies_sorted[int(len(latencies_sorted) * 0.90)]
        p99 = latencies_sorted[int(len(latencies_sorted) * 0.99)]
        avg = statistics.mean(latencies_sorted)
        
        result = {
            "test": "access_latency",
            "samples": len(latencies),
            "p50_ms": round(p50, 2),
            "p90_ms": round(p90, 2),
            "p99_ms": round(p99, 2),
            "avg_ms": round(avg, 2),
            "min_ms": round(min(latencies), 2),
            "max_ms": round(max(latencies), 2),
            "raw_latencies": latencies
        }
        
        print(f"  ✓ Latency P50={p50:.1f}ms, P90={p90:.1f}ms, P99={p99:.1f}ms")
        
        self.results["access_latency"] = result
        return result
    
    async def test_throughput(self, concurrency_levels: List[int] = [10, 50, 100]):
        """
        Test throughput under varying concurrency with real blockchain.
        """
        print(f"\n[E2-2] Testing Throughput (concurrency: {concurrency_levels})...")
        
        throughput_results = []
        valid_subject = "0x1234567890123456789012345678901234567890"
        
        for concurrency in concurrency_levels:
            print(f"  Testing concurrency={concurrency}...")
            
            request_count = concurrency * 10  # 10 requests per concurrent user
            
            async def make_request(session, req_id):
                resource_id = (req_id % 100) + 1
                try:
                    resp = await session.post(
                        f"{self.base_url}/access",
                        json={
                            "subject": valid_subject,
                            "resourceId": resource_id,
                            "action": "READ"
                        },
                        timeout=aiohttp.ClientTimeout(total=30)
                    )
                    return resp.status in [200, 403]
                except:
                    return False
            
            async with aiohttp.ClientSession() as session:
                start_time = time.time()
                
                tasks = [make_request(session, i) for i in range(request_count)]
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                end_time = time.time()
                duration_s = end_time - start_time
                
                successful = sum(1 for r in results if r is True)
                throughput = successful / duration_s if duration_s > 0 else 0
                
                throughput_results.append({
                    "concurrency": concurrency,
                    "requests": request_count,
                    "successful": successful,
                    "duration_s": round(duration_s, 2),
                    "throughput_rps": round(throughput, 2)
                })
                
                print(f"    -> {successful}/{request_count} successful, {throughput:.1f} req/s")
        
        self.results["throughput"] = {
            "test": "throughput",
            "results": throughput_results
        }
        
        return throughput_results
    
    async def test_policy_update_confirmation(self, samples: int = 10):
        """
        Test policy update confirmation time (transaction inclusion in block).
        Measures time from tx submission to confirmation.
        """
        print(f"\n[E2-3] Testing Policy Update Confirmation Time ({samples} samples)...")
        
        confirmation_times = []
        
        async with aiohttp.ClientSession() as session:
            for i in range(samples):
                # Create a policy matching the server's /policy schema
                # Types.Role.DRIVER=1, ResourceType.GENERIC=0, Action.READ=0
                policy_data = {
                    "role": 1,
                    "orgId": "0x0000000000000000000000000000000000000000000000000000000000000000",
                    "jurisdiction": "0x0000000000000000000000000000000000000000000000000000000000000000",
                    "rType": 0,
                    "caseId": "0x0000000000000000000000000000000000000000000000000000000000000000",
                    "action": 0,
                    "maxSensitivity": 3,
                    "notBefore": 0,
                    "notAfter": 0,
                    "allow": True
                }

                start_time = time.time()
                retries = getattr(self, "policy_retries", 1)
                delay = getattr(self, "policy_retry_delay", 3.0)
                last_status = None
                for attempt in range(retries):
                    try:
                        resp = await session.post(
                            f"{self.base_url}/policy",
                            json=policy_data,
                            timeout=aiohttp.ClientTimeout(total=90)  # longer for public RPC
                        )
                        end_time = time.time()

                        if resp.status == 200:
                            confirmation_time_s = end_time - start_time
                            confirmation_times.append(confirmation_time_s)
                            print(f"  -> Policy {i+1}/{samples}: {confirmation_time_s:.2f}s confirmation")
                            break
                        else:
                            last_status = resp.status
                            if attempt < retries - 1:
                                await asyncio.sleep(delay * (attempt + 1))
                            else:
                                print(f"  ✗ Policy {i+1} failed with status {resp.status}")
                    except Exception as e:
                        last_status = str(e)
                        if attempt < retries - 1:
                            await asyncio.sleep(delay * (attempt + 1))
                        else:
                            print(f"  ✗ Policy {i+1} error: {e}")
                            continue
        
        if not confirmation_times:
            print("  ✗ No successful policy updates")
            return {}
        
        result = {
            "test": "policy_update_confirmation",
            "samples": len(confirmation_times),
            "avg_s": round(statistics.mean(confirmation_times), 2),
            "min_s": round(min(confirmation_times), 2),
            "max_s": round(max(confirmation_times), 2),
            "median_s": round(statistics.median(confirmation_times), 2),
            "raw_times": confirmation_times
        }
        
        print(f"  ✓ Avg confirmation: {result['avg_s']}s, Range: [{result['min_s']}s - {result['max_s']}s]")
        
        self.results["policy_confirmation"] = result
        return result
    
    async def run_all_tests(self):
        """Run all E2 tests."""
        print("=" * 80)
        print("E2: REALISTIC BLOCKCHAIN / NETWORK CONDITIONS")
        print("=" * 80)
        
        # Health check
        try:
            async with aiohttp.ClientSession() as session:
                resp = await session.get(f"{self.base_url}/../health")
                if resp.status == 200:
                    print("✓ Gateway health check passed")
                else:
                    print("✗ Gateway not responding")
                    return False
        except:
            print("✗ Cannot reach gateway")
            return False
        
        # Run tests
        await self.test_access_latency(samples=100)
        await self.test_throughput(concurrency_levels=[10, 50, 100])
        await self.test_policy_update_confirmation(samples=10)
        
        return True
    
    def save_results(self, output_dir: str = "experiment_results/e2"):
        """Save results to file."""
        base_dir = Path(__file__).resolve().parent
        out_path = Path(output_dir)
        if not out_path.is_absolute():
            out_path = base_dir / out_path

        os.makedirs(out_path, exist_ok=True)

        # Save individual test results
        for test_name, result in self.results.items():
            filename = out_path / f"e2_{test_name}.json"
            with open(filename, "w") as f:
                json.dump(result, f, indent=2)
            print(f"✓ Saved {filename}")

        # Save summary
        summary = {
            "access_latency": self.results.get("access_latency", {}),
            "throughput": self.results.get("throughput", {}),
            "policy_confirmation": self.results.get("policy_confirmation", {})
        }

        summary_file = out_path / "e2_summary.json"
        with open(summary_file, "w") as f:
            json.dump(summary, f, indent=2)
        print(f"✓ Saved {summary_file}")

async def main():
    parser = argparse.ArgumentParser(description="E2: Realistic Blockchain Conditions")
    parser.add_argument("--base-url", default=BASE_URL, help="Gateway base URL")
    parser.add_argument("--output-dir", default="experiment_results/e2", help="Output directory")
    parser.add_argument(
        "--only",
        default="all",
        help="Comma-separated subset to run: access,throughput,policy (default: all)",
    )
    parser.add_argument(
        "--policy-retries",
        type=int,
        default=3,
        help="Retries per policy tx on transient RPC errors",
    )
    parser.add_argument(
        "--policy-retry-delay",
        type=float,
        default=3.0,
        help="Base delay (seconds) between policy retries",
    )
    
    args = parser.parse_args()
    allowed = {s.strip().lower() for s in args.only.split(',') if s.strip()}
    run_access = 'access' in allowed or 'all' in allowed or args.only == 'all'
    run_throughput = 'throughput' in allowed or 'all' in allowed or args.only == 'all'
    run_policy = 'policy' in allowed or 'all' in allowed or args.only == 'all'
    
    tester = E2Tester(args.base_url)
    success = True
    
    print("=" * 80)
    print("E2: REALISTIC BLOCKCHAIN / NETWORK CONDITIONS")
    print("=" * 80)
    
    # Health check
    try:
        async with aiohttp.ClientSession() as session:
            resp = await session.get(f"{tester.base_url}/../health")
            if resp.status == 200:
                print("✓ Gateway health check passed")
            else:
                print("✗ Gateway not responding")
                return 1
    except Exception:
        print("✗ Cannot reach gateway")
        return 1
    
    if run_access:
        await tester.test_access_latency(samples=100)
    if run_throughput:
        await tester.test_throughput(concurrency_levels=[10, 50, 100])
    if run_policy:
        # Inject retry parameters via attributes to avoid changing signature widely
        tester.policy_retries = max(1, args.policy_retries)
        tester.policy_retry_delay = max(0.5, args.policy_retry_delay)
        await tester.test_policy_update_confirmation(samples=10)
    
    if success:
        tester.save_results(args.output_dir)
        print("\n" + "=" * 80)
        print("E2 TESTS COMPLETED SUCCESSFULLY")
        print("=" * 80)
        print(f"Results saved to {args.output_dir}")
    else:
        print("\n✗ E2 tests could not be completed")
        return 1

if __name__ == "__main__":
    asyncio.run(main())
