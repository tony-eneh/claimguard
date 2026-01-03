"""
E5: Audit Log Query Performance Experiment

Compares blockchain (Ethereum) vs PostgreSQL vs MongoDB for audit log queries
in the ClaimGuard access control system.

Author: ClaimGuard Team
Date: January 2026
Target: KICS Winter 2026
"""

import asyncio
import aiohttp
import psycopg2
from pymongo import MongoClient
from web3 import Web3
import time
import json
import csv
import os
from datetime import datetime, timedelta
from statistics import median, stdev
from typing import List, Dict, Tuple
import random

# Configuration
EVENT_COUNTS = [100, 1000, 5000, 10000]
QUERY_PATTERNS = ['by_subject', 'by_resource', 'time_range', 'all_denials']
REPETITIONS = 10
ACTIONS = ['READ', 'APPEND', 'UPDATE', 'DELETE', 'ADJUDICATE', 'DISCLOSE']

# Database connection strings
PG_CONFIG = {
    'host': 'localhost',
    'database': 'audit_logs',
    'user': 'claimguard',
    'password': 'testpass',
    'port': 55432  # mapped host port to avoid conflict with local Postgres
}

MONGO_URI = 'mongodb://localhost:27017/'
MONGO_DB = 'audit_logs'

# Blockchain connection
HARDHAT_URL = 'http://127.0.0.1:8545'

# Load contract info
CONTRACT_NAME = 'AccessAuditLog'

def load_contract_abi(contract_name: str) -> dict:
    """Load contract ABI from artifacts."""
    artifact_path = f'artifacts/contracts/{contract_name}.sol/{contract_name}.json'
    with open(artifact_path, 'r') as f:
        artifact = json.load(f)
    return artifact['abi']

# Initialize connections
print("Initializing database connections...")
pg_conn = psycopg2.connect(**PG_CONFIG)
mongo_client = MongoClient(MONGO_URI)
mongo_db = mongo_client[MONGO_DB]
mongo_collection = mongo_db['audit_log']

w3 = Web3(Web3.HTTPProvider(HARDHAT_URL))
print(f"Connected to Hardhat: {w3.is_connected()}")

# Load AuditLog contract (assuming it exists)
# Note: Address should be loaded from deployment files
try:
    with open('deployments/latest.json', 'r') as f:
        deployment = json.load(f)
        raw_address = (
            deployment.get('AccessAuditLog', {}).get('address')
            or deployment.get('AuditLog', {}).get('address')
        )
        AUDIT_LOG_ADDRESS = Web3.to_checksum_address(raw_address) if raw_address else None
except Exception:
    AUDIT_LOG_ADDRESS = None
    print("Warning: AccessAuditLog contract address not found. Will skip blockchain queries.")

if AUDIT_LOG_ADDRESS:
    audit_log_abi = load_contract_abi(CONTRACT_NAME)
    audit_log = w3.eth.contract(address=AUDIT_LOG_ADDRESS, abi=audit_log_abi)
    print(f"AccessAuditLog contract loaded at {AUDIT_LOG_ADDRESS}")


# Data generation functions
def generate_random_address() -> str:
    """Generate random Ethereum checksum address."""
    raw = '0x' + ''.join(random.choices('0123456789abcdef', k=40))
    return Web3.to_checksum_address(raw)

def generate_random_hash() -> str:
    """Generate random keccak256 hash."""
    return '0x' + ''.join(random.choices('0123456789abcdef', k=64))

def generate_audit_events(count: int, subjects: List[str], resources: List[str]) -> List[Dict]:
    """Generate random audit events."""
    events = []
    for i in range(count):
        event = {
            'subject': random.choice(subjects),
            'resourceIdHash': random.choice(resources),
            'action': random.choice(ACTIONS),
            'allowed': random.random() < 0.8,  # 80% allowed, 20% denied
            'timestamp': datetime.now() - timedelta(days=random.randint(0, 365))
        }
        events.append(event)
    return events


# Event logging functions
def log_to_postgres(event: Dict):
    """Log event to PostgreSQL."""
    cursor = pg_conn.cursor()
    cursor.execute(
        """INSERT INTO audit_log (subject, resource_id_hash, action, allowed, timestamp)
           VALUES (%s, %s, %s, %s, %s)""",
        (event['subject'], event['resourceIdHash'], event['action'], 
         event['allowed'], event['timestamp'])
    )
    pg_conn.commit()
    cursor.close()

def log_to_mongo(event: Dict):
    """Log event to MongoDB."""
    mongo_collection.insert_one(event)

def log_to_blockchain(event: Dict, account):
    """Log event to blockchain (AccessAuditLog contract)."""
    if not AUDIT_LOG_ADDRESS:
        return
    
    try:
        from_account = Web3.to_checksum_address(account)
        resource_bytes = Web3.to_bytes(hexstr=event['resourceIdHash'])
        action_hash = Web3.keccak(text=event['action'])
        tx = audit_log.functions.logAccess(
            Web3.to_checksum_address(event['subject']),
            resource_bytes,
            action_hash,
            event['allowed']
        ).transact({'from': from_account})
        receipt = w3.eth.wait_for_transaction_receipt(tx)
        return receipt
    except Exception as e:
        print(f"Blockchain logging error: {e}")
        return None


# Query functions - PostgreSQL
def query_postgres_by_subject(subject: str) -> Tuple[float, int]:
    """Query PostgreSQL by subject."""
    cursor = pg_conn.cursor()
    start = time.time()
    cursor.execute("SELECT * FROM audit_log WHERE subject = %s", (subject,))
    results = cursor.fetchall()
    latency = (time.time() - start) * 1000  # ms
    cursor.close()
    return latency, len(results)

def query_postgres_by_resource(resource_hash: str) -> Tuple[float, int]:
    """Query PostgreSQL by resource."""
    cursor = pg_conn.cursor()
    start = time.time()
    cursor.execute("SELECT * FROM audit_log WHERE resource_id_hash = %s", (resource_hash,))
    results = cursor.fetchall()
    latency = (time.time() - start) * 1000
    cursor.close()
    return latency, len(results)

def query_postgres_time_range(start_date: datetime, end_date: datetime) -> Tuple[float, int]:
    """Query PostgreSQL by time range."""
    cursor = pg_conn.cursor()
    start = time.time()
    cursor.execute(
        "SELECT * FROM audit_log WHERE timestamp BETWEEN %s AND %s",
        (start_date, end_date)
    )
    results = cursor.fetchall()
    latency = (time.time() - start) * 1000
    cursor.close()
    return latency, len(results)

def query_postgres_all_denials() -> Tuple[float, int]:
    """Query PostgreSQL for all denials."""
    cursor = pg_conn.cursor()
    start = time.time()
    cursor.execute("SELECT * FROM audit_log WHERE allowed = false")
    results = cursor.fetchall()
    latency = (time.time() - start) * 1000
    cursor.close()
    return latency, len(results)


# Query functions - MongoDB
def query_mongo_by_subject(subject: str) -> Tuple[float, int]:
    """Query MongoDB by subject."""
    start = time.time()
    results = list(mongo_collection.find({'subject': subject}))
    latency = (time.time() - start) * 1000
    return latency, len(results)

def query_mongo_by_resource(resource_hash: str) -> Tuple[float, int]:
    """Query MongoDB by resource."""
    start = time.time()
    results = list(mongo_collection.find({'resourceIdHash': resource_hash}))
    latency = (time.time() - start) * 1000
    return latency, len(results)

def query_mongo_time_range(start_date: datetime, end_date: datetime) -> Tuple[float, int]:
    """Query MongoDB by time range."""
    start = time.time()
    results = list(mongo_collection.find({
        'timestamp': {'$gte': start_date, '$lte': end_date}
    }))
    latency = (time.time() - start) * 1000
    return latency, len(results)

def query_mongo_all_denials() -> Tuple[float, int]:
    """Query MongoDB for all denials."""
    start = time.time()
    results = list(mongo_collection.find({'allowed': False}))
    latency = (time.time() - start) * 1000
    return latency, len(results)


# Query functions - Blockchain
def query_blockchain_by_subject(subject: str, from_block: int, to_block: int) -> Tuple[float, int]:
    """Query blockchain by subject."""
    if not AUDIT_LOG_ADDRESS:
        return 0.0, 0
    start = time.time()
    events = audit_log.events.AccessChecked.get_logs(
        from_block=from_block,
        to_block=to_block,
        argument_filters={'subject': Web3.to_checksum_address(subject)}
    )
    latency = (time.time() - start) * 1000
    return latency, len(events)

def query_blockchain_by_resource(resource_hash: str, from_block: int, to_block: int) -> Tuple[float, int]:
    """Query blockchain by resource hash."""
    if not AUDIT_LOG_ADDRESS:
        return 0.0, 0
    start = time.time()
    resource_bytes = Web3.to_bytes(hexstr=resource_hash)
    events = audit_log.events.AccessChecked.get_logs(
        from_block=from_block,
        to_block=to_block,
        argument_filters={'resourceIdHash': resource_bytes}
    )
    latency = (time.time() - start) * 1000
    return latency, len(events)

def query_blockchain_time_range(from_block: int, to_block: int) -> Tuple[float, int]:
    """Query blockchain by block range."""
    if not AUDIT_LOG_ADDRESS:
        return 0.0, 0
    
    start = time.time()
    events = audit_log.events.AccessChecked.get_logs(
        from_block=from_block,
        to_block=to_block
    )
    latency = (time.time() - start) * 1000
    return latency, len(events)

def query_blockchain_all_denials(from_block: int, to_block: int) -> Tuple[float, int]:
    """Query blockchain for all denials."""
    if not AUDIT_LOG_ADDRESS:
        return 0.0, 0
    
    start = time.time()
    events = audit_log.events.AccessChecked.get_logs(
        from_block=from_block,
        to_block=to_block,
        argument_filters={'allow': False}
    )
    latency = (time.time() - start) * 1000
    return latency, len(events)


# Main experiment
async def run_experiment():
    """Main experiment loop."""
    print("\n" + "="*60)
    print("E5: Audit Log Query Performance Experiment")
    print("="*60)
    
    results = []
    
    # Generate test subjects and resources
    print("\nGenerating test data...")
    test_subjects = [generate_random_address() for _ in range(200)]
    test_resources = [generate_random_hash() for _ in range(1000)]
    
    for event_count in EVENT_COUNTS:
        print(f"\n{'='*60}")
        print(f"Testing with {event_count} events")
        print(f"{'='*60}")
        
        # Clear existing data
        print("Clearing existing data...")
        cursor = pg_conn.cursor()
        cursor.execute("TRUNCATE TABLE audit_log")
        pg_conn.commit()
        cursor.close()
        mongo_collection.delete_many({})
        
        # Generate and log events
        print(f"Generating {event_count} events...")
        events = generate_audit_events(event_count, test_subjects, test_resources)
        
        print("Logging to PostgreSQL...")
        for event in events:
            log_to_postgres(event)
        
        print("Logging to MongoDB...")
        for event in events:
            log_to_mongo(event)
        
        # Get blockchain block range (if available)
        start_block = w3.eth.block_number if AUDIT_LOG_ADDRESS else 0
        
        if AUDIT_LOG_ADDRESS:
            log_count = min(event_count, 500)  # cap to keep runtime reasonable
            print(f"Logging {log_count} events to blockchain...")
            accounts = w3.eth.accounts
            for event in events[:log_count]:
                log_to_blockchain(event, accounts[0])
        
        end_block = w3.eth.block_number if AUDIT_LOG_ADDRESS else 0
        
        # Choose subjects/resources that are guaranteed to exist in the logged set
        test_subject = events[0]['subject']
        test_resource = events[0]['resourceIdHash']
        test_start_date = datetime.now() - timedelta(days=180)
        test_end_date = datetime.now() - timedelta(days=90)

        # Run queries
        print("\nRunning query tests...")
        
        for pattern in QUERY_PATTERNS:
            print(f"  Testing pattern: {pattern}")
            
            for rep in range(REPETITIONS):
                result = {
                    'event_count': event_count,
                    'pattern': pattern,
                    'repetition': rep,
                    'blockchain_latency_ms': 0.0,
                    'postgres_latency_ms': 0.0,
                    'mongo_latency_ms': 0.0,
                    'result_count': 0
                }
                
                # Run queries based on pattern
                if pattern == 'by_subject':
                    pg_lat, pg_cnt = query_postgres_by_subject(test_subject)
                    mg_lat, mg_cnt = query_mongo_by_subject(test_subject)
                    bc_lat, bc_cnt = query_blockchain_by_subject(test_subject, start_block, end_block)
                    result['result_count'] = pg_cnt
                
                elif pattern == 'by_resource':
                    pg_lat, pg_cnt = query_postgres_by_resource(test_resource)
                    mg_lat, mg_cnt = query_mongo_by_resource(test_resource)
                    bc_lat, bc_cnt = query_blockchain_by_resource(test_resource, start_block, end_block)
                    result['result_count'] = pg_cnt
                
                elif pattern == 'time_range':
                    pg_lat, pg_cnt = query_postgres_time_range(test_start_date, test_end_date)
                    mg_lat, mg_cnt = query_mongo_time_range(test_start_date, test_end_date)
                    bc_lat, bc_cnt = query_blockchain_time_range(start_block, end_block)
                    result['result_count'] = pg_cnt
                
                elif pattern == 'all_denials':
                    pg_lat, pg_cnt = query_postgres_all_denials()
                    mg_lat, mg_cnt = query_mongo_all_denials()
                    bc_lat, bc_cnt = query_blockchain_all_denials(start_block, end_block)
                    result['result_count'] = pg_cnt
                
                result['postgres_latency_ms'] = pg_lat
                result['mongo_latency_ms'] = mg_lat
                result['blockchain_latency_ms'] = bc_lat
                
                results.append(result)
    
    # Save results
    os.makedirs('experiment_results', exist_ok=True)
    output_file = 'experiment_results/e5_audit_logs.csv'
    
    with open(output_file, 'w', newline='') as f:
        fieldnames = ['event_count', 'pattern', 'repetition', 'blockchain_latency_ms', 
                      'postgres_latency_ms', 'mongo_latency_ms', 'result_count']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    
    print(f"\n{'='*60}")
    print("Experiment complete!")
    print(f"Results saved to: {output_file}")
    print(f"{'='*60}")
    
    # Cleanup
    pg_conn.close()
    mongo_client.close()


if __name__ == '__main__':
    asyncio.run(run_experiment())
