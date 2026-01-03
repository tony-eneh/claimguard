# E5 Experiment: Audit Log Query Performance

This directory contains the setup for the E5 experiment comparing blockchain, PostgreSQL, and MongoDB audit log query performance.

## Quick Start

### 1. Start Infrastructure

```bash
# Start Docker containers
docker-compose up -d

# Verify databases are running
docker ps | grep -E 'postgres|mongo'

# Check database health
docker exec claimguard-postgres pg_isready -U claimguard
docker exec claimguard-mongo mongosh --eval "db.adminCommand('ping')"
```

### 2. Verify Database Schemas

```bash
# PostgreSQL
docker exec -it claimguard-postgres psql -U claimguard -d audit_logs -c "\d audit_log"

# MongoDB
docker exec -it claimguard-mongo mongosh audit_logs --eval "db.audit_log.getIndexes()"
```

### 3. Run Experiment

```bash
# Install Python dependencies
pip install psycopg2-binary pymongo web3 pandas matplotlib

# Run experiment (takes 15-30 minutes)
python e5_audit_query_performance.py
```

### 4. Analyze Results

```bash
# Generate figures and tables
python analyze_e5.py

# View results
cat experiment_results/e5_audit_logs.csv
```

### 5. Compile Paper

```bash
cd papers/3_conference
pdflatex paper.tex
bibtex paper
pdflatex paper.tex
pdflatex paper.tex
```

## Directory Structure

```
papers/3_conference/
├── paper.tex           # Main LaTeX source
├── paper.bib           # References
├── figures/            # Generated figures
│   ├── e5_query_latency.pdf
│   └── e5_comparison_bar.pdf
└── README.md           # This file
```

## Experiment Details

- **Event Counts**: 100, 1K, 5K, 10K
- **Query Patterns**: by_subject, by_resource, time_range, all_denials
- **Repetitions**: 10 per pattern
- **Baselines**: PostgreSQL 16, MongoDB 7, Ethereum (Hardhat)

## Troubleshooting

### Docker containers won't start
```bash
# Check logs
docker-compose logs postgres
docker-compose logs mongo

# Restart
docker-compose down
docker-compose up -d
```

### Database connection errors
```bash
# Test PostgreSQL
psql postgresql://claimguard:testpass@localhost:5432/audit_logs

# Test MongoDB
mongosh mongodb://localhost:27017/audit_logs
```

### Python dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt  # If requirements.txt exists
```

## Expected Results

- Blockchain queries: 2-10x slower than databases
- PostgreSQL: Fastest for indexed queries
- MongoDB: Flexible, moderate performance
- Time-range queries: Most expensive for blockchain

## Timeline

- Day 1: Infrastructure setup (today)
- Day 2-3: Run experiments
- Day 4-5: Analyze results
- Day 6-8: Write paper
- Day 9-10: Review and submit
