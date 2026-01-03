# Paper Plan: Audit Log Query Performance in ClaimGuard

**Title**: Query Performance Analysis of Blockchain-Based Audit Trails for Insurance Access Control

**Target Venue**: KICS (Korea Information and Communications Society) Winter 2026  
**Format**: IEEE Xplore 2-column, 2 pages maximum (~1400 words)  
**Experiment**: E5 - Audit Log Query Performance  
**Status**: Planning phase (not yet implemented)

---

## Research Question

**Primary RQ**: What are the query performance characteristics and storage costs of blockchain-based audit trails compared to traditional database systems for insurance access control compliance reporting?

**Sub-questions**:
1. How does audit log query latency scale with event count (100 → 10K events)?
2. What is the performance difference between blockchain (Ethereum) vs. PostgreSQL vs. MongoDB for audit queries?
3. Which query patterns (by subject, by resource, by time range, all denials) are most expensive?
4. What are the storage cost implications for long-term audit retention?

---

## Motivation & Novelty

### Why This Paper Matters

**Problem Context:**
- Insurance regulations require comprehensive audit trails (SOX, GDPR, HIPAA, state insurance codes)
- Conference & journal papers claim "immutable audit trails" and "comprehensive auditability" but **never quantify query performance**
- Compliance reporting requires fast queries: "Show me all denials for subject X in Q4 2025"
- Storage costs for blockchain audit logs are unclear

**Novelty:**
- ✅ First quantification of audit query costs in blockchain-based ABAC
- ✅ First comparison of blockchain vs. relational vs. document database audit logs
- ✅ Realistic insurance compliance query patterns
- ✅ Storage cost analysis for long-term retention

**Gap in Literature:**
- Journal paper (Section 5.2) mentions "long-term audit log management" as deployment concern but provides no data
- No prior work measures audit log query performance in blockchain access control systems

---

## Paper Structure (2 Pages, ~1400 Words)

### Abstract (100 words)
- **Problem**: Insurance access control requires queryable audit trails for compliance
- **Approach**: Benchmark blockchain audit logs (Ethereum) vs. PostgreSQL vs. MongoDB
- **Method**: Generate 100-10K access events, measure query latency across 4 patterns
- **Key Results**: [To be filled after experiment]
  - Example: "Blockchain queries average 2.5x slower but provide cryptographic verifiability"
  - Example: "Time-range queries scale sub-linearly up to 10K events"
- **Conclusion**: Trade-offs identified between performance and immutability

### 1. Introduction (200 words)
**Paragraph 1: Problem Context**
- Insurance claims involve sensitive evidence (medical records, police reports, telematics)
- Regulations mandate comprehensive audit trails for access control decisions
- Compliance officers need to query: "Who accessed what, when, and was it allowed?"

**Paragraph 2: Blockchain for Access Control**
- ClaimGuard (prior work) implements blockchain-based ABAC for insurance evidence
- Audit events emitted on-chain via `AccessChecked` events
- Claims: immutable, tamper-proof, cryptographically verifiable audit trails

**Paragraph 3: Research Gap**
- Prior work demonstrates correctness but not queryability
- Practitioners need to know: Can blockchain audit logs support real-time compliance queries?
- This paper provides first quantitative analysis

**Paragraph 4: Contributions**
1. Benchmark blockchain audit log queries across 4 patterns
2. Compare against PostgreSQL and MongoDB baselines
3. Analyze storage costs and scalability limits
4. Provide deployment recommendations

### 2. System Methodology (250 words)

**Section 2.1: ClaimGuard Audit Architecture (120 words)**

**Smart Contract Design:**
```solidity
contract AuditLog {
    event AccessChecked(
        address indexed subject,
        bytes32 indexed resourceIdHash,
        string action,
        bool allowed,
        uint256 timestamp
    );
    
    function logAccess(...) external { emit AccessChecked(...); }
}
```

- Every access decision triggers `AccessChecked` event
- Indexed fields (subject, resourceIdHash) enable efficient filtering
- Events stored permanently on blockchain (cannot be deleted)
- Query via Web3 `getPastEvents()` with filter parameters

**Architecture Components:**
1. **On-Chain**: AuditLog.sol emits events, stored in transaction logs
2. **Gateway (PEG)**: Calls `logAccess()` after every authorization check
3. **Query Interface**: Web3.py event filtering API

**Section 2.2: Baseline Systems (130 words)**

**PostgreSQL Audit Log:**
```sql
CREATE TABLE audit_log (
    id SERIAL PRIMARY KEY,
    subject VARCHAR(42) INDEXED,
    resource_id_hash VARCHAR(66) INDEXED,
    action VARCHAR(20),
    allowed BOOLEAN INDEXED,
    timestamp TIMESTAMP DEFAULT NOW()
);
CREATE INDEX idx_subject ON audit_log(subject);
CREATE INDEX idx_resource ON audit_log(resource_id_hash);
CREATE INDEX idx_timestamp ON audit_log(timestamp);
CREATE INDEX idx_denied ON audit_log(allowed) WHERE allowed = false;
```

**MongoDB Audit Log:**
```javascript
db.createCollection("audit_log", {
    validator: { /* schema */ }
});
db.audit_log.createIndex({ "subject": 1 });
db.audit_log.createIndex({ "resourceIdHash": 1 });
db.audit_log.createIndex({ "timestamp": 1 });
db.audit_log.createIndex({ "allowed": 1 });
```

**Deployment:**
- Docker containers (postgres:16-alpine, mongo:7)
- Same machine as Ethereum node (Hardhat local network)
- Comparable indexing strategies

### 3. Experimental Design (150 words)

**Section 3.1: Methodology**

**Event Generation:**
- Reuse existing `access_test.py` load generator
- Concurrency: 50 clients
- Event counts: 100, 1K, 5K, 10K access decisions
- Distribution: 80% allowed, 20% denied (realistic ratio)
- 200 unique subjects, 1000 unique resources

**Query Patterns (4 types):**
1. **By Subject**: `filter={subject: 0x123...}` - "What did Alice access?"
2. **By Resource**: `filter={resourceIdHash: hash(456)}` - "Who accessed medical report #456?"
3. **By Time Range**: `fromBlock: N, toBlock: M` - "All accesses in December 2025"
4. **All Denials**: `filter={allowed: false}` - "Compliance audit: show all unauthorized attempts"

**Metrics:**
- **Query Latency**: P50, P90, P99, average (milliseconds)
- **Result Size**: Number of events returned, payload bytes
- **Storage Cost**: Disk space (PostgreSQL/MongoDB) vs. gas costs (Ethereum)
- **Query Complexity**: Simple (single filter) vs. compound (subject AND time range)

**Repetition**: 10 runs per query pattern, report median and variance

### 4. Results and Discussion (500 words)

**Section 4.1: Query Latency Analysis (200 words)**

[Figure 1: Query Latency vs. Event Count - 4 line plots for each query pattern across 100, 1K, 5K, 10K events]

**Expected Results Structure:**
- Table 1: Median query latency (ms) comparison

| Query Pattern | Blockchain (10K) | PostgreSQL (10K) | MongoDB (10K) | Ratio (BC/PG) |
|---------------|------------------|------------------|---------------|---------------|
| By Subject    | TBD              | TBD              | TBD           | TBD           |
| By Resource   | TBD              | TBD              | TBD           | TBD           |
| Time Range    | TBD              | TBD              | TBD           | TBD           |
| All Denials   | TBD              | TBD              | TBD           | TBD           |

**Discussion Points:**
- Blockchain queries likely 2-10x slower due to RPC overhead and sequential block scanning
- PostgreSQL benefits from B-tree indexes on subject/resource
- MongoDB flexible schema but potentially less efficient for range queries
- Time-range queries most expensive for blockchain (must scan blocks)
- Scaling behavior: Linear? Sub-linear? Log(n)?

**Section 4.2: Storage Cost Analysis (150 words)**

[Table 2: Storage Costs per 10K Events]

| System      | Storage Size | Cost per Event | Retrieval Cost | Notes               |
|-------------|--------------|----------------|----------------|---------------------|
| Blockchain  | TBD gas      | ~$X USD        | Free (RPC)     | Permanent, immutable|
| PostgreSQL  | TBD MB       | Negligible     | Free (query)   | Deletable, mutable  |
| MongoDB     | TBD MB       | Negligible     | Free (query)   | Flexible schema     |

**Discussion:**
- Ethereum gas: ~2K-5K gas per event emission (~$0.XX at current prices)
- PostgreSQL/MongoDB: pennies per GB, negligible per event
- **Trade-off**: Blockchain 100-1000x more expensive but cryptographically verifiable
- Long-term retention: 1M events = $X,XXX on blockchain vs. $XX on database
- Hybrid approach: Critical events on-chain, detailed logs off-chain

**Section 4.3: Query Pattern Efficiency (100 words)**

[Figure 2: Query Latency Breakdown by Pattern - Bar chart comparing 4 patterns]

**Findings:**
- Indexed queries (by subject/resource) fast in all systems
- Time-range queries expensive for blockchain (block iteration)
- Denial audits efficient if `allowed` field indexed
- Compound queries (subject + time) challenging for blockchain

**Recommendations:**
- Use subject/resource filters when possible
- Limit time-range queries to specific block ranges
- Consider off-chain indexing (The Graph, Dune Analytics)

**Section 4.4: Implications for Deployment (50 words)**

**When to Use Blockchain Audit Logs:**
- ✅ High-value transactions requiring immutability (claim settlements, legal disputes)
- ✅ Multi-party systems needing trust-minimization
- ❌ High-frequency, low-value accesses (internal dashboards, routine queries)

**Hybrid Recommendation:**
- Critical access decisions → on-chain audit
- Routine access logs → PostgreSQL/MongoDB
- Sync periodically for comprehensive compliance reports

### 5. Conclusion (100 words)

**Summary:**
- First quantitative analysis of blockchain audit log query performance
- Blockchain 2-10x slower than databases but provides verifiability
- Storage costs 100-1000x higher for blockchain
- Query patterns matter: indexed lookups efficient, time-range expensive

**Trade-offs:**
- Performance vs. immutability
- Cost vs. trust guarantees

**Deployment Guidance:**
- Hybrid approach recommended for production
- On-chain for high-value audits, off-chain for routine logs

**Future Work:**
- Off-chain indexing solutions (The Graph)
- Layer 2 deployment for lower costs
- Zero-knowledge audit proofs for privacy

### References (10-15 citations)

**Categories:**
1. **ClaimGuard Papers** (2):
   - Conference paper (2024)
   - Journal paper (2025)

2. **Blockchain Access Control** (3-4):
   - MedRec, PatientSphere, other ABAC systems

3. **Audit Log Systems** (2-3):
   - Traditional audit log architectures
   - Compliance reporting systems

4. **Blockchain Performance** (2-3):
   - Ethereum event filtering
   - Storage cost analysis papers

5. **Insurance Regulations** (1-2):
   - GDPR audit requirements
   - Insurance compliance standards

---

## Implementation Plan

### Phase 1: Infrastructure Setup (Day 1)

**1.1: Docker Environment**
```yaml
# docker-compose.yml
version: '3.8'
services:
  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: audit_logs
      POSTGRES_USER: claimguard
      POSTGRES_PASSWORD: testpass
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
  
  mongo:
    image: mongo:7
    ports:
      - "27017:27017"
    environment:
      MONGO_INITDB_DATABASE: audit_logs
    volumes:
      - mongo_data:/data/db

volumes:
  postgres_data:
  mongo_data:
```

**Commands:**
```bash
cd claimguard
docker-compose up -d postgres mongo

# Verify running
docker ps | grep -E 'postgres|mongo'
```

**1.2: Database Schema Setup**
```bash
# PostgreSQL
docker exec -it claimguard-postgres-1 psql -U claimguard -d audit_logs

# Run schema creation
\i scripts/setup_postgres_audit.sql

# MongoDB
docker exec -it claimguard-mongo-1 mongosh

# Run collection setup
load('scripts/setup_mongo_audit.js')
```

**1.3: Blockchain Node**
```bash
# Terminal 1: Start Hardhat node
npx hardhat node

# Terminal 2: Deploy contracts
npm run deploy

# Update .env with AuditLog address
echo "AUDIT_LOG_ADDRESS=0x..." >> claimguard-peg/.env
```

### Phase 2: Experiment Implementation (Day 2-3)

**2.1: Create Scripts (6 files)**

**File 1: `scripts/setup_postgres_audit.sql`**
```sql
CREATE TABLE audit_log (
    id SERIAL PRIMARY KEY,
    subject VARCHAR(42) NOT NULL,
    resource_id_hash VARCHAR(66) NOT NULL,
    action VARCHAR(20) NOT NULL,
    allowed BOOLEAN NOT NULL,
    timestamp TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_subject ON audit_log(subject);
CREATE INDEX idx_resource ON audit_log(resource_id_hash);
CREATE INDEX idx_timestamp ON audit_log(timestamp);
CREATE INDEX idx_allowed ON audit_log(allowed);
CREATE INDEX idx_denied ON audit_log(allowed) WHERE allowed = false;

-- Analyze for query optimization
ANALYZE audit_log;
```

**File 2: `scripts/setup_mongo_audit.js`**
```javascript
db = db.getSiblingDB('audit_logs');

db.createCollection('audit_log', {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['subject', 'resourceIdHash', 'action', 'allowed', 'timestamp'],
      properties: {
        subject: { bsonType: 'string', pattern: '^0x[a-fA-F0-9]{40}$' },
        resourceIdHash: { bsonType: 'string' },
        action: { bsonType: 'string' },
        allowed: { bsonType: 'bool' },
        timestamp: { bsonType: 'date' }
      }
    }
  }
});

db.audit_log.createIndex({ subject: 1 });
db.audit_log.createIndex({ resourceIdHash: 1 });
db.audit_log.createIndex({ timestamp: 1 });
db.audit_log.createIndex({ allowed: 1 });
```

**File 3: `e5_audit_query_performance.py`** (~200 LOC)
```python
"""
E5: Audit Log Query Performance Experiment

Compares blockchain (Ethereum) vs PostgreSQL vs MongoDB for audit log queries.
"""

import asyncio
import aiohttp
import psycopg2
from pymongo import MongoClient
from web3 import Web3
import time
import json
import csv
from datetime import datetime
from statistics import median, stdev

# Configuration
EVENT_COUNTS = [100, 1000, 5000, 10000]
QUERY_PATTERNS = ['by_subject', 'by_resource', 'time_range', 'all_denials']
REPETITIONS = 10

# Database connections
pg_conn = psycopg2.connect(
    host='localhost',
    database='audit_logs',
    user='claimguard',
    password='testpass'
)

mongo_client = MongoClient('mongodb://localhost:27017/')
mongo_db = mongo_client['audit_logs']
mongo_collection = mongo_db['audit_log']

# Blockchain connection
w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8545'))
audit_log_address = '0x...'  # From deployment
audit_log_abi = json.load(open('artifacts/contracts/AuditLog.sol/AuditLog.json'))['abi']
audit_log = w3.eth.contract(address=audit_log_address, abi=audit_log_abi)

async def generate_events(count: int):
    """Generate audit events across all three systems."""
    print(f"Generating {count} events...")
    
    # Reuse access_test.py pattern
    # TODO: Implement event generation
    pass

def query_blockchain_by_subject(subject: str, from_block: int, to_block: int):
    """Query blockchain events by subject."""
    start = time.time()
    events = audit_log.events.AccessChecked.get_logs(
        fromBlock=from_block,
        toBlock=to_block,
        argument_filters={'subject': subject}
    )
    latency = (time.time() - start) * 1000  # ms
    return latency, len(events)

def query_postgres_by_subject(subject: str):
    """Query PostgreSQL by subject."""
    cursor = pg_conn.cursor()
    start = time.time()
    cursor.execute(
        "SELECT * FROM audit_log WHERE subject = %s",
        (subject,)
    )
    results = cursor.fetchall()
    latency = (time.time() - start) * 1000  # ms
    cursor.close()
    return latency, len(results)

def query_mongo_by_subject(subject: str):
    """Query MongoDB by subject."""
    start = time.time()
    results = list(mongo_collection.find({'subject': subject}))
    latency = (time.time() - start) * 1000  # ms
    return latency, len(results)

# TODO: Implement remaining query patterns
# - query_*_by_resource()
# - query_*_time_range()
# - query_*_all_denials()

async def run_experiment():
    """Main experiment loop."""
    results = []
    
    for event_count in EVENT_COUNTS:
        print(f"\n=== Testing with {event_count} events ===")
        
        # Generate events
        await generate_events(event_count)
        
        for pattern in QUERY_PATTERNS:
            print(f"Testing pattern: {pattern}")
            
            for rep in range(REPETITIONS):
                # Run queries across all systems
                bc_latency, bc_count = run_blockchain_query(pattern)
                pg_latency, pg_count = run_postgres_query(pattern)
                mg_latency, mg_count = run_mongo_query(pattern)
                
                results.append({
                    'event_count': event_count,
                    'pattern': pattern,
                    'repetition': rep,
                    'blockchain_latency_ms': bc_latency,
                    'postgres_latency_ms': pg_latency,
                    'mongo_latency_ms': mg_latency,
                    'result_count': bc_count
                })
    
    # Save results
    with open('experiment_results/e5_audit_logs.csv', 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)
    
    print("\nExperiment complete! Results saved to experiment_results/e5_audit_logs.csv")

if __name__ == '__main__':
    asyncio.run(run_experiment())
```

**File 4: `analyze_e5.py`** (~150 LOC)
```python
"""
E5 Analysis: Generate figures and tables for paper.
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Read results
df = pd.read_csv('experiment_results/e5_audit_logs.csv')

# Calculate statistics
stats = df.groupby(['event_count', 'pattern']).agg({
    'blockchain_latency_ms': ['median', 'std'],
    'postgres_latency_ms': ['median', 'std'],
    'mongo_latency_ms': ['median', 'std']
}).reset_index()

# Figure 1: Query Latency vs Event Count
fig, axes = plt.subplots(2, 2, figsize=(12, 10))
patterns = ['by_subject', 'by_resource', 'time_range', 'all_denials']

for idx, pattern in enumerate(patterns):
    ax = axes[idx // 2, idx % 2]
    data = stats[stats['pattern'] == pattern]
    
    ax.plot(data['event_count'], data[('blockchain_latency_ms', 'median')], 
            marker='o', label='Blockchain')
    ax.plot(data['event_count'], data[('postgres_latency_ms', 'median')], 
            marker='s', label='PostgreSQL')
    ax.plot(data['event_count'], data[('mongo_latency_ms', 'median')], 
            marker='^', label='MongoDB')
    
    ax.set_xlabel('Event Count')
    ax.set_ylabel('Median Latency (ms)')
    ax.set_title(f'Query Pattern: {pattern}')
    ax.legend()
    ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('short_paper/figures/e5_query_latency.png', dpi=300)
plt.savefig('short_paper/figures/e5_query_latency.pdf')

# Table 1: LaTeX comparison table
print("\n=== LaTeX Table 1: Query Latency at 10K Events ===")
data_10k = stats[stats['event_count'] == 10000]
print("\\begin{table}[h]")
print("\\caption{Median Query Latency (ms) at 10K Events}")
print("\\begin{tabular}{lrrrc}")
print("\\toprule")
print("Query Pattern & Blockchain & PostgreSQL & MongoDB & Ratio \\\\")
print("\\midrule")
for _, row in data_10k.iterrows():
    pattern = row['pattern']
    bc = row[('blockchain_latency_ms', 'median')]
    pg = row[('postgres_latency_ms', 'median')]
    mg = row[('mongo_latency_ms', 'median')]
    ratio = bc / pg
    print(f"{pattern} & {bc:.1f} & {pg:.1f} & {mg:.1f} & {ratio:.1f}x \\\\")
print("\\bottomrule")
print("\\end{tabular}")
print("\\end{table}")

# Storage cost analysis
# TODO: Calculate gas costs, database sizes

print("\n=== Analysis Complete ===")
print("Figures saved to short_paper/figures/")
```

**File 5: `experiment_tests/audit_helper.py`** (~100 LOC)
```python
"""
Helper functions for E5 experiment.
"""

from web3 import Web3
import psycopg2
from pymongo import MongoClient
from datetime import datetime

def log_to_all_systems(event_data: dict):
    """Log an access event to all three systems."""
    
    # 1. Blockchain
    w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8545'))
    # Call audit_log.logAccess(...)
    
    # 2. PostgreSQL
    conn = psycopg2.connect(...)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO audit_log (subject, resource_id_hash, action, allowed, timestamp)
        VALUES (%s, %s, %s, %s, %s)
    """, (event_data['subject'], event_data['resourceIdHash'], 
          event_data['action'], event_data['allowed'], datetime.now()))
    conn.commit()
    
    # 3. MongoDB
    client = MongoClient('mongodb://localhost:27017/')
    db = client['audit_logs']
    db.audit_log.insert_one({
        'subject': event_data['subject'],
        'resourceIdHash': event_data['resourceIdHash'],
        'action': event_data['action'],
        'allowed': event_data['allowed'],
        'timestamp': datetime.now()
    })

def clear_all_audit_logs():
    """Clear audit logs from all systems (for clean runs)."""
    # PostgreSQL
    conn = psycopg2.connect(...)
    cursor = conn.cursor()
    cursor.execute("TRUNCATE TABLE audit_log")
    conn.commit()
    
    # MongoDB
    client = MongoClient('mongodb://localhost:27017/')
    db = client['audit_logs']
    db.audit_log.delete_many({})
    
    # Blockchain: cannot delete (need to deploy new contract or track starting block)
```

**File 6: `short_paper/README.md`**
```markdown
# E5 Paper: Audit Log Query Performance

## Directory Structure
```
short_paper/
├── paper.tex          # Main LaTeX source
├── paper.bib          # References
├── figures/           # Generated figures
│   ├── e5_query_latency.pdf
│   └── e5_storage_cost.pdf
├── tables/            # LaTeX table includes
└── README.md          # This file
```

## Compilation

```bash
cd short_paper
pdflatex paper.tex
bibtex paper
pdflatex paper.tex
pdflatex paper.tex
```

## IEEE Format

- Template: IEEEtran.cls (2-column)
- Page limit: 2 pages
- Font: 10pt Times Roman
```

### Phase 3: Experiment Execution (Day 4-5)

**3.1: Run Experiments**
```bash
# Start infrastructure
docker-compose up -d
npx hardhat node &
cd claimguard-peg && npm run dev &

# Run experiment
python e5_audit_query_performance.py

# Expected output files:
# - experiment_results/e5_audit_logs.csv
# - experiment_results/e5_storage_costs.json
```

**3.2: Analyze Results**
```bash
python analyze_e5.py

# Generates:
# - short_paper/figures/e5_query_latency.png/pdf
# - short_paper/figures/e5_storage_cost.png/pdf
# - LaTeX table code (printed to console)
```

**3.3: Validate Results**
- Check for anomalies in latency measurements
- Verify event counts match across systems
- Compare query result correctness (same events returned)
- Calculate statistical significance (t-tests if needed)

### Phase 4: Paper Writing (Day 6-8)

**4.1: Setup Paper Directory**
```bash
mkdir -p short_paper/{figures,tables}
cd short_paper

# Download IEEEtran template
wget http://www.ieee.org/conferences_events/conferences/publishing/templates/IEEEtran.zip
unzip IEEEtran.zip
```

**4.2: Write Sections (Order)**

**Day 6:**
- ✍️ Abstract (100 words) - after results known
- ✍️ Introduction (200 words) - problem, gap, contributions
- ✍️ System Methodology (250 words) - architecture, baselines

**Day 7:**
- ✍️ Experimental Design (150 words) - methodology, metrics
- ✍️ Results and Discussion (500 words) - figures, tables, analysis
- 📊 Integrate figures and tables

**Day 8:**
- ✍️ Conclusion (100 words) - summary, future work
- 📚 Write references (~12-15 citations)
- 🔍 Proofread and format

**4.3: LaTeX Structure**
```latex
\documentclass[conference]{IEEEtran}

\usepackage{graphicx}
\usepackage{booktabs}
\usepackage{amsmath}
\usepackage{cite}

\title{Query Performance Analysis of Blockchain-Based Audit Trails for Insurance Access Control}

\author{
\IEEEauthorblockN{[Your Name]}
\IEEEauthorblockA{[Your Institution]\\
Email: [your@email]}
}

\begin{document}

\maketitle

\begin{abstract}
[100 words]
\end{abstract}

\section{Introduction}
[200 words]

\section{System Methodology}
[250 words]
\subsection{ClaimGuard Audit Architecture}
\subsection{Baseline Systems}

\section{Experimental Design}
[150 words]

\section{Results and Discussion}
[500 words]
\subsection{Query Latency Analysis}
\subsection{Storage Cost Analysis}
\subsection{Query Pattern Efficiency}
\subsection{Deployment Implications}

\begin{figure}[t]
\centering
\includegraphics[width=\columnwidth]{figures/e5_query_latency.pdf}
\caption{Query latency vs event count across four patterns.}
\label{fig:latency}
\end{figure}

\begin{table}[t]
\caption{Median Query Latency at 10K Events}
\label{tab:latency}
\centering
\begin{tabular}{lrrrc}
\toprule
Pattern & BC & PG & Mongo & Ratio \\
\midrule
Subject & XX & YY & ZZ & A.Bx \\
... \\
\bottomrule
\end{tabular}
\end{table}

\section{Conclusion}
[100 words]

\bibliographystyle{IEEEtran}
\bibliography{paper}

\end{document}
```

**4.4: Reference Collection**

**Create `paper.bib`:**
```bibtex
@article{claimguard_journal,
  title={Evaluating Action-Aware Attribute-Based Access Control for Secure Insurance Evidence Management},
  author={[Your Name]},
  journal={Journal of Information Security and Applications},
  year={2025}
}

@inproceedings{claimguard_conf,
  title={ClaimGuard: A Blockchain-Backed Access Control Gateway for Privacy-Preservation in Auto-Insurance Claims},
  author={[Your Name]},
  booktitle={IEEE Conference},
  year={2024}
}

@article{medrec,
  title={MedRec: Using blockchain for medical data access and permission management},
  author={Azaria, Asaph and others},
  journal={OBD},
  year={2016}
}

% TODO: Add 10-12 more references
```

### Phase 5: Review & Submission (Day 9-10)

**5.1: Internal Review Checklist**
- [ ] Abstract clearly states problem, approach, results
- [ ] Introduction motivates the work and cites ClaimGuard papers
- [ ] System Methodology explains architecture with code snippets
- [ ] Experimental Design is reproducible
- [ ] Results include 2 figures and 1-2 tables
- [ ] Discussion interprets results and provides recommendations
- [ ] Conclusion summarizes contributions and future work
- [ ] All figures have captions and are referenced in text
- [ ] All tables have captions and are referenced in text
- [ ] References formatted correctly (IEEE style)
- [ ] Page limit: exactly 2 pages
- [ ] Figures are high quality (300 DPI minimum)
- [ ] No orphan lines or widows
- [ ] All acronyms defined on first use

**5.2: Professor Review**
- Share draft with lab professor
- Address feedback
- Revise based on comments

**5.3: Submission Preparation**
- Compile final PDF
- Prepare supplementary materials if allowed (code repository link)
- Check KICS submission guidelines
- Submit before deadline

---

## Implementation Notes & Best Practices

### Docker Considerations
**Your Idea is GOOD** ✅

**Advantages:**
- ✅ Isolated database instances (no conflicts with existing databases)
- ✅ Easy cleanup (`docker-compose down -v`)
- ✅ Reproducible environment
- ✅ Can share docker-compose.yml with reviewers
- ✅ Similar to production deployment patterns

**Potential Issues:**
- ⚠️ Docker overhead may add 1-2ms to query latency
- ⚠️ Network mode: use `network_mode: host` for minimal overhead
- ⚠️ Volume persistence: ensure data survives between runs

**Mitigation:**
```yaml
# docker-compose.yml adjustments
services:
  postgres:
    network_mode: host  # Reduce Docker network overhead
    shm_size: 256mb     # Increase shared memory for PostgreSQL
  mongo:
    network_mode: host
```

### Query Complexity Judgment

**Recommendation: Test 3 complexity levels**

**Level 1 - Simple (single filter):**
```python
# Blockchain
filter={'subject': '0x123...'}

# PostgreSQL
WHERE subject = '0x123...'

# MongoDB
{'subject': '0x123...'}
```

**Level 2 - Moderate (two filters):**
```python
# Blockchain
filter={'subject': '0x123...', 'allowed': False}

# PostgreSQL
WHERE subject = '0x123...' AND allowed = false

# MongoDB
{'subject': '0x123...', 'allowed': false}
```

**Level 3 - Complex (time range + filter):**
```python
# Blockchain
fromBlock=N, toBlock=M, filter={'allowed': False}

# PostgreSQL
WHERE timestamp BETWEEN '2025-12-01' AND '2025-12-31' AND allowed = false

# MongoDB
{'timestamp': {'$gte': ..., '$lte': ...}, 'allowed': false}
```

**Rationale:**
- Level 1: Most common (compliance officer looks up specific user)
- Level 2: Frequent (find all denials for a user)
- Level 3: Periodic (quarterly compliance reports)

This gives a representative range without overcomplicating the paper.

### Expected Timeline

| Phase | Duration | Deliverables |
|-------|----------|--------------|
| Phase 1: Infrastructure | 1 day | Docker running, schemas created |
| Phase 2: Implementation | 2 days | Scripts written, tested |
| Phase 3: Execution | 2 days | Data collected, analyzed |
| Phase 4: Writing | 3 days | Draft paper complete |
| Phase 5: Review | 2 days | Final paper ready |
| **Total** | **10 days** | **Submittable paper** |

### Potential Challenges & Solutions

**Challenge 1: Blockchain queries too slow**
- **Solution**: Limit event count to 5K instead of 10K
- **Solution**: Use Hardhat's `--no-mining` for instant blocks

**Challenge 2: Docker overhead too high**
- **Solution**: Use `network_mode: host`
- **Solution**: Compare with native PostgreSQL/MongoDB install

**Challenge 3: Experiment runs too long**
- **Solution**: Reduce repetitions from 10 to 5
- **Solution**: Parallelize query execution

**Challenge 4: Results not interesting**
- **Solution**: Emphasize trade-offs (cost vs. trust)
- **Solution**: Add hybrid architecture recommendation

**Challenge 5: 2-page limit too tight**
- **Solution**: Move detailed methodology to GitHub repo
- **Solution**: Use 2-column format efficiently (fewer whitespaces)
- **Solution**: Shrink figures slightly, combine subplots

---

## Success Metrics

### Experiment Success Criteria
- ✅ 100-10K events generated successfully across all systems
- ✅ All 4 query patterns tested with 10 repetitions each
- ✅ Results show clear trends (latency increases with event count)
- ✅ Statistical significance (p < 0.05 for blockchain vs. database differences)

### Paper Success Criteria
- ✅ Exactly 2 pages in IEEE format
- ✅ 2 figures + 1-2 tables
- ✅ Novel results not in existing papers
- ✅ Reproducible methodology
- ✅ Clear contributions and recommendations
- ✅ Accepted to KICS Winter 2026 🎯

---

## Next Steps

### Immediate Actions (Start Today)
1. ✅ Create `docker-compose.yml` (15 minutes)
2. ✅ Start Docker containers (5 minutes)
3. ✅ Create database schemas (30 minutes)
4. ✅ Verify infrastructure working (15 minutes)

### Tomorrow
5. ⏳ Implement `e5_audit_query_performance.py` (4-6 hours)
6. ⏳ Implement `analyze_e5.py` (2-3 hours)
7. ⏳ Test scripts with 100 events (1 hour)

### This Week
8. ⏳ Run full experiments (Day 4-5)
9. ⏳ Write paper draft (Day 6-8)
10. ⏳ Review and submit (Day 9-10)

---

## Questions to Resolve

### Before Starting Experiment
1. ✅ Target venue: KICS Winter 2026
2. ✅ Format: IEEE Xplore 2-column
3. ✅ Baseline comparison: PostgreSQL + MongoDB
4. ✅ Deployment: Docker containers
5. ✅ Query complexity: 3 levels (simple, moderate, complex)

### During Experiment
6. ⏳ What event count is maximum feasible? (Test up to 10K, can reduce if needed)
7. ⏳ Should we test compound queries? (Yes, Level 3 complexity)
8. ⏳ Include gas cost breakdown? (Yes, in storage cost section)

### During Writing
9. ⏳ Include code snippets in paper? (Yes, Solidity event definition + SQL schema)
10. ⏳ Emphasize cost or performance? (Both, with trade-off analysis)
11. ⏳ Reference journal paper or conference? (Both, as prior work)

---

## Contact & Resources

**KICS Submission Portal**: [To be added]  
**KICS Winter 2026 Deadline**: [To be confirmed]  
**IEEE Template**: http://www.ieee.org/conferences_events/conferences/publishing/templates.html

**Tools Needed:**
- Python 3.10+ with packages: web3.py, psycopg2, pymongo, matplotlib, pandas
- Docker Desktop / Docker Engine
- LaTeX distribution (TeX Live, MiKTeX)
- Git for version control

---

*Last Updated: January 3, 2026*
*Status: Planning Phase - Ready to Begin Implementation*
