"""
E5 Additional Metrics: Write Throughput, Insertion Latency, Gas Cost, Storage Size

Measures metrics that related works have measured to enable quantitative comparison
in the KICS Winter 2026 conference paper.

Author: ClaimGuard Team
Date: January 2026
"""

import time
import json
import csv
import os
from datetime import datetime, timedelta
from statistics import median, stdev, mean
from typing import List, Dict, Tuple, Optional, Any
import random

try:
    import psycopg2
    from pymongo import MongoClient
    from web3 import Web3
except ImportError as e:
    print(f"Missing dependency: {e}")
    print("Run: pip install psycopg2-binary pymongo web3")
    exit(1)

# =============================================================================
# Configuration
# =============================================================================

BATCH_SIZES = [100, 500, 1000]
INDIVIDUAL_LATENCY_SAMPLES = 50  # Number of individual insertions to time
REPETITIONS = 5

ACTIONS = ['READ', 'APPEND', 'UPDATE', 'DELETE', 'ADJUDICATE', 'DISCLOSE']

# Database connection strings
PG_CONFIG = {
    'host': 'localhost',
    'database': 'audit_logs',
    'user': 'claimguard',
    'password': 'testpass',
    'port': 54320
}

MONGO_URI = 'mongodb://localhost:27017/'
MONGO_DB = 'audit_logs'

# Blockchain connection
HARDHAT_URL = 'http://127.0.0.1:8545'
CONTRACT_NAME = 'AccessAuditLog'

# Gas price scenarios (in gwei)
GAS_PRICES_GWEI = [10, 50, 100]
ETH_PRICE_USD = 2000  # Approximate ETH price for cost estimation

# =============================================================================
# Initialization
# =============================================================================

def load_contract_abi(contract_name: str) -> dict:
    """Load contract ABI from artifacts."""
    artifact_path = f'artifacts/contracts/{contract_name}.sol/{contract_name}.json'
    with open(artifact_path, 'r') as f:
        artifact = json.load(f)
    return artifact['abi']

def initialize_connections():
    """Initialize all database connections."""
    print("Initializing connections...")
    
    # PostgreSQL
    try:
        pg_conn = psycopg2.connect(**PG_CONFIG)
        print("  PostgreSQL: Connected")
    except Exception as e:
        print(f"  PostgreSQL: Failed - {e}")
        pg_conn = None
    
    # MongoDB
    try:
        mongo_client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        mongo_client.server_info()  # Force connection
        mongo_db = mongo_client[MONGO_DB]
        mongo_collection = mongo_db['audit_log']
        print("  MongoDB: Connected")
    except Exception as e:
        print(f"  MongoDB: Failed - {e}")
        mongo_client = None
        mongo_collection = None
    
    # Blockchain
    try:
        w3 = Web3(Web3.HTTPProvider(HARDHAT_URL))
        if w3.is_connected():
            print(f"  Blockchain: Connected (Block #{w3.eth.block_number})")
        else:
            print("  Blockchain: Not connected")
            w3 = None
    except Exception as e:
        print(f"  Blockchain: Failed - {e}")
        w3 = None
    
    # Load contract
    audit_log = None
    audit_log_address = None
    if w3:
        try:
            with open('deployments/latest.json', 'r') as f:
                deployment = json.load(f)
                raw_address = deployment.get('AccessAuditLog', {}).get('address')
                if raw_address:
                    audit_log_address = Web3.to_checksum_address(raw_address)
                    audit_log_abi = load_contract_abi(CONTRACT_NAME)
                    audit_log = w3.eth.contract(address=audit_log_address, abi=audit_log_abi)
                    print(f"  Contract: Loaded at {audit_log_address}")
        except Exception as e:
            print(f"  Contract: Failed to load - {e}")
    
    return pg_conn, mongo_collection, w3, audit_log

# =============================================================================
# Data Generation
# =============================================================================

def generate_random_address() -> str:
    """Generate random Ethereum checksum address."""
    raw = '0x' + ''.join(random.choices('0123456789abcdef', k=40))
    return Web3.to_checksum_address(raw)

def generate_random_hash() -> str:
    """Generate random keccak256 hash."""
    return '0x' + ''.join(random.choices('0123456789abcdef', k=64))

def generate_audit_event() -> Dict:
    """Generate a single random audit event."""
    return {
        'subject': generate_random_address(),
        'resourceIdHash': generate_random_hash(),
        'action': random.choice(ACTIONS),
        'allowed': random.random() < 0.8,
        'timestamp': datetime.now() - timedelta(days=random.randint(0, 365))
    }

def generate_audit_events(count: int) -> List[Dict]:
    """Generate multiple random audit events."""
    return [generate_audit_event() for _ in range(count)]

# =============================================================================
# PostgreSQL Operations
# =============================================================================

def clear_postgres(pg_conn):
    """Clear PostgreSQL audit_log table."""
    if not pg_conn:
        return
    cursor = pg_conn.cursor()
    cursor.execute("TRUNCATE TABLE audit_log")
    pg_conn.commit()
    cursor.close()

def insert_postgres_single(pg_conn, event: Dict) -> float:
    """Insert single event to PostgreSQL, return latency in ms."""
    cursor = pg_conn.cursor()
    start = time.perf_counter()
    cursor.execute(
        """INSERT INTO audit_log (subject, resource_id_hash, action, allowed, timestamp)
           VALUES (%s, %s, %s, %s, %s)""",
        (event['subject'], event['resourceIdHash'], event['action'],
         event['allowed'], event['timestamp'])
    )
    pg_conn.commit()
    latency = (time.perf_counter() - start) * 1000
    cursor.close()
    return latency

def insert_postgres_batch(pg_conn, events: List[Dict]) -> Tuple[float, float]:
    """Insert batch of events to PostgreSQL, return (total_time_ms, tps)."""
    cursor = pg_conn.cursor()
    start = time.perf_counter()
    for event in events:
        cursor.execute(
            """INSERT INTO audit_log (subject, resource_id_hash, action, allowed, timestamp)
               VALUES (%s, %s, %s, %s, %s)""",
            (event['subject'], event['resourceIdHash'], event['action'],
             event['allowed'], event['timestamp'])
        )
    pg_conn.commit()
    total_time = (time.perf_counter() - start) * 1000
    tps = len(events) / (total_time / 1000) if total_time > 0 else 0
    cursor.close()
    return total_time, tps

def get_postgres_storage_size(pg_conn) -> int:
    """Get PostgreSQL table size in bytes."""
    if not pg_conn:
        return 0
    cursor = pg_conn.cursor()
    cursor.execute("SELECT pg_total_relation_size('audit_log')")
    size = cursor.fetchone()[0]
    cursor.close()
    return size

# =============================================================================
# MongoDB Operations
# =============================================================================

def clear_mongo(mongo_collection):
    """Clear MongoDB collection."""
    if mongo_collection is not None:
        mongo_collection.delete_many({})

def insert_mongo_single(mongo_collection, event: Dict) -> float:
    """Insert single event to MongoDB, return latency in ms."""
    start = time.perf_counter()
    mongo_collection.insert_one(event.copy())  # Copy to avoid _id mutation
    latency = (time.perf_counter() - start) * 1000
    return latency

def insert_mongo_batch(mongo_collection, events: List[Dict]) -> Tuple[float, float]:
    """Insert batch of events to MongoDB, return (total_time_ms, tps)."""
    start = time.perf_counter()
    # Copy events to avoid _id mutation issues
    mongo_collection.insert_many([e.copy() for e in events])
    total_time = (time.perf_counter() - start) * 1000
    tps = len(events) / (total_time / 1000) if total_time > 0 else 0
    return total_time, tps

def get_mongo_storage_size(mongo_collection) -> int:
    """Get MongoDB collection storage size in bytes."""
    if mongo_collection is None:
        return 0
    stats = mongo_collection.database.command('collStats', mongo_collection.name)
    return stats.get('storageSize', 0)

# =============================================================================
# Blockchain Operations
# =============================================================================

def insert_blockchain_single(w3: Any, audit_log: Any, event: Dict, account: Optional[str]) -> Tuple[float, int]:
    """Insert single event to blockchain, return (latency_ms, gas_used)."""
    if not audit_log:
        return 0.0, 0
    
    try:
        from_account = Web3.to_checksum_address(account)
        resource_bytes = Web3.to_bytes(hexstr=event['resourceIdHash'])
        action_hash = Web3.keccak(text=event['action'])
        
        start = time.perf_counter()
        tx = audit_log.functions.logAccess(
            Web3.to_checksum_address(event['subject']),
            resource_bytes,
            action_hash,
            event['allowed']
        ).transact({'from': from_account})
        receipt = w3.eth.wait_for_transaction_receipt(tx)
        latency = (time.perf_counter() - start) * 1000
        
        return latency, receipt.gasUsed
    except Exception as e:
        print(f"  Blockchain insert error: {e}")
        return 0.0, 0

def insert_blockchain_batch(w3: Any, audit_log: Any, events: List[Dict], account: Optional[str]) -> Tuple[float, float, int]:
    """Insert batch of events to blockchain, return (total_time_ms, tps, total_gas)."""
    if not audit_log:
        return 0.0, 0.0, 0
    
    total_gas = 0
    from_account = Web3.to_checksum_address(account)
    
    start = time.perf_counter()
    for event in events:
        try:
            resource_bytes = Web3.to_bytes(hexstr=event['resourceIdHash'])
            action_hash = Web3.keccak(text=event['action'])
            
            tx = audit_log.functions.logAccess(
                Web3.to_checksum_address(event['subject']),
                resource_bytes,
                action_hash,
                event['allowed']
            ).transact({'from': from_account})
            receipt = w3.eth.wait_for_transaction_receipt(tx)
            total_gas += receipt.gasUsed
        except Exception as e:
            print(f"  Blockchain batch insert error: {e}")
    
    total_time = (time.perf_counter() - start) * 1000
    tps = len(events) / (total_time / 1000) if total_time > 0 else 0
    
    return total_time, tps, total_gas

# =============================================================================
# Main Experiment
# =============================================================================

def run_experiment():
    """Run all additional metrics experiments."""
    print("\n" + "=" * 70)
    print("E5 Additional Metrics Experiment")
    print("Measuring: Write Throughput, Insertion Latency, Gas Cost, Storage Size")
    print("=" * 70)
    
    # Initialize connections
    pg_conn, mongo_collection, w3, audit_log = initialize_connections()
    
    if not any([pg_conn, mongo_collection, w3]):
        print("\nERROR: No database connections available. Exiting.")
        return
    
    account = w3.eth.accounts[0] if w3 else None
    
    results = {
        'throughput': [],
        'insertion_latency': [],
        'gas_cost': [],
        'storage_size': []
    }
    
    # =========================================================================
    # Experiment 1: Write Throughput (batch insertion)
    # =========================================================================
    print("\n" + "-" * 70)
    print("Experiment 1: Write Throughput (events/second)")
    print("-" * 70)
    
    for batch_size in BATCH_SIZES:
        print(f"\n  Batch size: {batch_size}")
        
        for rep in range(REPETITIONS):
            events = generate_audit_events(batch_size)
            
            # PostgreSQL
            if pg_conn:
                clear_postgres(pg_conn)
                pg_time, pg_tps = insert_postgres_batch(pg_conn, events)
                results['throughput'].append({
                    'system': 'PostgreSQL',
                    'batch_size': batch_size,
                    'repetition': rep,
                    'total_time_ms': pg_time,
                    'throughput_tps': pg_tps
                })
            
            # MongoDB
            if mongo_collection is not None:
                clear_mongo(mongo_collection)
                mg_time, mg_tps = insert_mongo_batch(mongo_collection, events)
                results['throughput'].append({
                    'system': 'MongoDB',
                    'batch_size': batch_size,
                    'repetition': rep,
                    'total_time_ms': mg_time,
                    'throughput_tps': mg_tps
                })
            
            # Blockchain (limit to smaller batches due to time)
            if audit_log and batch_size <= 100:
                bc_time, bc_tps, bc_gas = insert_blockchain_batch(w3, audit_log, events, account)
                results['throughput'].append({
                    'system': 'Blockchain',
                    'batch_size': batch_size,
                    'repetition': rep,
                    'total_time_ms': bc_time,
                    'throughput_tps': bc_tps,
                    'total_gas': bc_gas
                })
        
        # Print summary for this batch size
        for system in ['PostgreSQL', 'MongoDB', 'Blockchain']:
            system_results = [r for r in results['throughput'] 
                            if r['system'] == system and r['batch_size'] == batch_size]
            if system_results:
                avg_tps = mean([r['throughput_tps'] for r in system_results])
                print(f"    {system}: {avg_tps:.1f} tps")
    
    # =========================================================================
    # Experiment 2: Individual Insertion Latency
    # =========================================================================
    print("\n" + "-" * 70)
    print("Experiment 2: Individual Insertion Latency (ms per event)")
    print("-" * 70)
    
    # Clear databases
    if pg_conn:
        clear_postgres(pg_conn)
    if mongo_collection is not None:
        clear_mongo(mongo_collection)
    
    pg_latencies = []
    mg_latencies = []
    bc_latencies = []
    bc_gas_samples = []
    
    for i in range(INDIVIDUAL_LATENCY_SAMPLES):
        event = generate_audit_event()
        
        if pg_conn:
            lat = insert_postgres_single(pg_conn, event)
            pg_latencies.append(lat)
        
        if mongo_collection is not None:
            lat = insert_mongo_single(mongo_collection, event)
            mg_latencies.append(lat)
        
        if audit_log and i < 20:  # Limit blockchain samples
            lat, gas = insert_blockchain_single(w3, audit_log, event, account)
            if lat > 0:
                bc_latencies.append(lat)
                bc_gas_samples.append(gas)
        
        if (i + 1) % 10 == 0:
            print(f"  Completed {i + 1}/{INDIVIDUAL_LATENCY_SAMPLES} samples")
    
    # Store latency results
    if pg_latencies:
        results['insertion_latency'].append({
            'system': 'PostgreSQL',
            'samples': len(pg_latencies),
            'median_ms': median(pg_latencies),
            'mean_ms': mean(pg_latencies),
            'std_ms': stdev(pg_latencies) if len(pg_latencies) > 1 else 0,
            'p90_ms': sorted(pg_latencies)[int(len(pg_latencies) * 0.9)],
            'p99_ms': sorted(pg_latencies)[int(len(pg_latencies) * 0.99)]
        })
        print(f"\n  PostgreSQL: median={median(pg_latencies):.2f}ms, p90={sorted(pg_latencies)[int(len(pg_latencies) * 0.9)]:.2f}ms")
    
    if mg_latencies:
        results['insertion_latency'].append({
            'system': 'MongoDB',
            'samples': len(mg_latencies),
            'median_ms': median(mg_latencies),
            'mean_ms': mean(mg_latencies),
            'std_ms': stdev(mg_latencies) if len(mg_latencies) > 1 else 0,
            'p90_ms': sorted(mg_latencies)[int(len(mg_latencies) * 0.9)],
            'p99_ms': sorted(mg_latencies)[int(len(mg_latencies) * 0.99)]
        })
        print(f"  MongoDB: median={median(mg_latencies):.2f}ms, p90={sorted(mg_latencies)[int(len(mg_latencies) * 0.9)]:.2f}ms")
    
    if bc_latencies:
        results['insertion_latency'].append({
            'system': 'Blockchain',
            'samples': len(bc_latencies),
            'median_ms': median(bc_latencies),
            'mean_ms': mean(bc_latencies),
            'std_ms': stdev(bc_latencies) if len(bc_latencies) > 1 else 0,
            'p90_ms': sorted(bc_latencies)[int(len(bc_latencies) * 0.9)],
            'p99_ms': sorted(bc_latencies)[int(len(bc_latencies) * 0.99)]
        })
        print(f"  Blockchain: median={median(bc_latencies):.2f}ms, p90={sorted(bc_latencies)[int(len(bc_latencies) * 0.9)]:.2f}ms")
    
    # =========================================================================
    # Experiment 3: Gas Cost Analysis
    # =========================================================================
    print("\n" + "-" * 70)
    print("Experiment 3: Gas Cost Analysis")
    print("-" * 70)
    
    if bc_gas_samples:
        avg_gas = mean(bc_gas_samples)
        print(f"\n  Average gas per event: {avg_gas:.0f}")
        
        for gas_price in GAS_PRICES_GWEI:
            cost_eth = (avg_gas * gas_price) / 1e9
            cost_usd = cost_eth * ETH_PRICE_USD
            results['gas_cost'].append({
                'avg_gas_per_event': avg_gas,
                'gas_price_gwei': gas_price,
                'cost_eth': cost_eth,
                'cost_usd': cost_usd,
                'cost_per_1k_events_usd': cost_usd * 1000,
                'cost_per_10k_events_usd': cost_usd * 10000
            })
            print(f"  At {gas_price} gwei: {cost_eth:.6f} ETH (${cost_usd:.4f}) per event")
            print(f"    10K events: ${cost_usd * 10000:.2f}")
    else:
        print("  No blockchain samples available for gas analysis")
    
    # =========================================================================
    # Experiment 4: Storage Size
    # =========================================================================
    print("\n" + "-" * 70)
    print("Experiment 4: Storage Size Analysis")
    print("-" * 70)
    
    # Insert known number of events
    test_count = 1000
    events = generate_audit_events(test_count)
    
    if pg_conn:
        clear_postgres(pg_conn)
        insert_postgres_batch(pg_conn, events)
        pg_size = get_postgres_storage_size(pg_conn)
        results['storage_size'].append({
            'system': 'PostgreSQL',
            'event_count': test_count,
            'total_bytes': pg_size,
            'bytes_per_event': pg_size / test_count if test_count > 0 else 0
        })
        print(f"\n  PostgreSQL: {pg_size / 1024:.1f} KB for {test_count} events ({pg_size / test_count:.1f} bytes/event)")
    
    if mongo_collection is not None:
        clear_mongo(mongo_collection)
        insert_mongo_batch(mongo_collection, events)
        mg_size = get_mongo_storage_size(mongo_collection)
        results['storage_size'].append({
            'system': 'MongoDB',
            'event_count': test_count,
            'total_bytes': mg_size,
            'bytes_per_event': mg_size / test_count if test_count > 0 else 0
        })
        print(f"  MongoDB: {mg_size / 1024:.1f} KB for {test_count} events ({mg_size / test_count:.1f} bytes/event)")
    
    if bc_gas_samples:
        # Estimate blockchain storage cost based on gas
        # Ethereum storage: 20,000 gas per 32-byte slot (SSTORE)
        # Events are cheaper as they use log storage
        avg_gas = mean(bc_gas_samples)
        estimated_bytes = avg_gas / 20  # Rough estimate
        results['storage_size'].append({
            'system': 'Blockchain',
            'event_count': len(bc_gas_samples),
            'avg_gas_per_event': avg_gas,
            'estimated_bytes_per_event': estimated_bytes,
            'note': 'Gas-based estimate; actual storage is in event logs'
        })
        print(f"  Blockchain: ~{avg_gas:.0f} gas/event (event log storage)")
    
    # =========================================================================
    # Save Results
    # =========================================================================
    print("\n" + "-" * 70)
    print("Saving Results")
    print("-" * 70)
    
    os.makedirs('experiment_results', exist_ok=True)
    
    # Save as JSON for easy parsing
    output_file = 'experiment_results/e5_additional_metrics.json'
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    print(f"  Saved: {output_file}")
    
    # Save throughput as CSV
    if results['throughput']:
        csv_file = 'experiment_results/e5_throughput.csv'
        with open(csv_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=results['throughput'][0].keys())
            writer.writeheader()
            writer.writerows(results['throughput'])
        print(f"  Saved: {csv_file}")
    
    # Save insertion latency as CSV
    if results['insertion_latency']:
        csv_file = 'experiment_results/e5_insertion_latency.csv'
        with open(csv_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=results['insertion_latency'][0].keys())
            writer.writeheader()
            writer.writerows(results['insertion_latency'])
        print(f"  Saved: {csv_file}")
    
    # Save gas costs as CSV
    if results['gas_cost']:
        csv_file = 'experiment_results/e5_gas_cost.csv'
        with open(csv_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=results['gas_cost'][0].keys())
            writer.writeheader()
            writer.writerows(results['gas_cost'])
        print(f"  Saved: {csv_file}")
    
    # =========================================================================
    # Print Summary for Paper
    # =========================================================================
    print("\n" + "=" * 70)
    print("SUMMARY FOR PAPER (Copy these values)")
    print("=" * 70)
    
    print("\n## Write Throughput (tps)")
    for system in ['PostgreSQL', 'MongoDB', 'Blockchain']:
        system_results = [r for r in results['throughput'] 
                        if r['system'] == system and r.get('batch_size') == 100]
        if system_results:
            avg_tps = mean([r['throughput_tps'] for r in system_results])
            print(f"  {system}: {avg_tps:.1f} tps")
    
    print("\n## Insertion Latency (ms)")
    for r in results['insertion_latency']:
        print(f"  {r['system']}: median={r['median_ms']:.2f}ms, p90={r['p90_ms']:.2f}ms")
    
    print("\n## Gas Cost (at 50 gwei, ETH=$2000)")
    for r in results['gas_cost']:
        if r['gas_price_gwei'] == 50:
            print(f"  Per event: {r['avg_gas_per_event']:.0f} gas = ${r['cost_usd']:.4f}")
            print(f"  Per 10K events: ${r['cost_per_10k_events_usd']:.2f}")
    
    print("\n## Storage Size")
    for r in results['storage_size']:
        if 'bytes_per_event' in r:
            print(f"  {r['system']}: {r['bytes_per_event']:.1f} bytes/event")
        elif 'avg_gas_per_event' in r:
            print(f"  {r['system']}: {r['avg_gas_per_event']:.0f} gas/event")
    
    print("\n" + "=" * 70)
    print("Experiment Complete!")
    print("=" * 70)
    
    # Cleanup
    if pg_conn:
        pg_conn.close()
    if mongo_collection:
        mongo_collection.database.client.close()


if __name__ == '__main__':
    run_experiment()
