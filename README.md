# ClaimGuard - Blockchain-Based Access Control Experiment

This project implements an Attribute-Based Access Control (ABAC) system for insurance claim evidence using smart contracts on Ethereum. It includes a Policy Enforcement Gateway (PEG) service and experimental infrastructure for performance testing.

## Project Structure

```
claimguard/
├── contracts/              # Solidity smart contracts
│   ├── Types.sol          # Shared enums and structs
│   ├── SubjectAttributeRegistry.sol
│   ├── EvidenceRegistry.sol
│   └── AccessPolicyManager.sol
├── scripts/               # Deployment scripts
│   └── deploy.ts
├── claimguard-peg/        # Policy Enforcement Gateway service
│   ├── src/
│   │   ├── server.ts      # Express API server
│   │   ├── blockchain.ts  # Blockchain interaction layer
│   │   └── seed-viem.ts   # Data seeding script
│   └── outputs/           # Generated seed data (subjects.json, resources.json)
├── experiments/           # Python experiment scripts
│   ├── run_experiments.py
│   ├── analyze_results.py
│   └── requirements.txt
└── experiment_results/    # Output CSV files from experiments
```

## Prerequisites

- Node.js >= 18.x
- Python >= 3.8
- npm or yarn

## Installation

1. **Clone the repository and install dependencies:**

```shell
npm install
cd claimguard-peg
npm install
cd ..
```

2. **Set up Python environment for experiments:**

```shell
cd experiments
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
cd ..
```

## Running the Experiment

**You will need at least 3 terminal windows open simultaneously.**

### Terminal 1: Hardhat Node (Local Development Only)

If you're testing on a local blockchain, start the Hardhat node:

```shell
npx hardhat node
```

> **Note:** Skip this step if connecting to a real chain like Sepolia or PureChain. The node will display 20 pre-funded accounts and their private keys. Keep this terminal running.

### Terminal 2: Policy Enforcement Gateway (PEG) Service

1. **Create environment configuration:**

Create a `.env` file in the `claimguard-peg` directory:

```shell
cd claimguard-peg
```

Add the following configuration (adjust for your network):

```env
# Local Hardhat Network
RPC_URL=http://127.0.0.1:8545
CHAIN_ID=31337

# For Sepolia or PureChain, use appropriate values:
# RPC_URL=https://rpc.sepolia.org
# CHAIN_ID=11155111

# Deployer account (use one of Hardhat's test accounts or your own)
PRIVATE_KEY=0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80

# Contract addresses (will be populated after deployment)
SUBJECT_ATTRIBUTE_REGISTRY_ADDRESS=
EVIDENCE_REGISTRY_ADDRESS=
ACCESS_POLICY_MANAGER_ADDRESS=

# PEG Server Configuration
PORT=3000
```

2. **Start the PEG service:**

```shell
npm run dev
```

The service will start on `http://localhost:3000`. Keep this terminal running.

### Terminal 3: Deployment and Experiments

1. **Deploy smart contracts:**

```shell
npm run deploy
```

This will deploy the contracts and output their addresses. **Copy these addresses to your `.env` file** in the `claimguard-peg` directory:

```
SUBJECT_ATTRIBUTE_REGISTRY_ADDRESS=0x...
EVIDENCE_REGISTRY_ADDRESS=0x...
ACCESS_POLICY_MANAGER_ADDRESS=0x...
```

2. **Restart the PEG service** (in Terminal 2) to load the new contract addresses:

```shell
# Press Ctrl+C to stop, then:
npm run dev
```

3. **Seed the blockchain with test data:**

```shell
cd claimguard-peg
npm run seed:viem
```

This will:
- Create 200 subjects with various roles (insurers, adjusters, police, etc.)
- Register 1000 resources across 200 insurance cases
- Define 11 ABAC policies for access control
- Save the seeded data to `outputs/subjects.json` and `outputs/resources.json`

4. **Run the experiments:**

```shell
cd ../experiments

# Activate Python virtual environment if not already active
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Run experiments (example: 200 read requests with 10 concurrent workers)
python run_experiments.py --test-type read --num-requests 200 --concurrency 10

# Run additional experiments as needed
python run_experiments.py --test-type read --num-requests 500 --concurrency 10
python run_experiments.py --test-type write --num-requests 50 --concurrency 5
```

5. **Analyze results:**

```shell
python analyze_results.py --input ../experiment_results/latency_read_n200_c10.csv
```

## Experiment Parameters

### `run_experiments.py` Options

- `--test-type`: Type of test (`read`, `write`, `policy-update`)
- `--num-requests`: Total number of requests to execute
- `--concurrency`: Number of concurrent workers
- `--peg-url`: PEG service URL (default: `http://localhost:3000`)
- `--output-dir`: Directory for CSV results (default: `../experiment_results`)

### `analyze_results.py` Options

- `--input`: Path to the CSV file to analyze
- `--output`: Optional path for analysis summary output

## Understanding the Results

Experiment results are saved as CSV files in `experiment_results/`:

- **Read experiments**: `latency_read_n{num}_c{concurrency}.csv`
  - Contains: worker_id, timestamp, latency_ms, status, access decision
  
- **Write experiments**: `latency_write_n{num}_c{concurrency}.csv`
  - Contains: worker_id, timestamp, latency_ms, status, tx_hash, gas_used
  
- **Policy update experiments**: `policy_updates_{num}.csv`
  - Contains: worker_id, index, timestamp, latency_ms, status, tx_hash, gas_used

Key metrics:
- **Latency**: Response time in milliseconds
- **Gas used**: Ethereum gas consumed (for write operations)
- **P50/P90/P99**: Percentile latencies for performance analysis

## Testing Smart Contracts

To run the smart contract tests:

```shell
npx hardhat test
```

## Troubleshooting

### PEG Service Won't Start
- Verify contract addresses in `.env` are correct
- Ensure Hardhat node is running (for local testing)
- Check that no other service is using port 3000

### Seeding Script Fails
- Confirm contracts are deployed
- Verify `.env` configuration in `claimguard-peg`
- Check that the deployer account has sufficient funds

### Experiment Connection Errors
- Ensure PEG service is running on the correct port
- Verify the `--peg-url` parameter matches your PEG service URL
- Check network connectivity

### Python Environment Issues
- Make sure virtual environment is activated
- Re-run `pip install -r requirements.txt` if packages are missing
- Use Python 3.8 or higher

## Clean Restart

To start fresh:

1. Stop all running services (Hardhat node, PEG)
2. Delete `claimguard-peg/outputs/*` if you want fresh seed data
3. Restart from Terminal 1 (Hardhat node)

## Network Configuration

### Local Hardhat Network
- Chain ID: 31337
- RPC URL: http://127.0.0.1:8545
- Pre-funded accounts with 10,000 ETH each

### Sepolia Testnet
- Chain ID: 11155111
- RPC URL: https://rpc.sepolia.org
- Requires testnet ETH (get from faucet)

### PureChain
- Configure according to your PureChain deployment
- Update RPC_URL and CHAIN_ID in `.env`
