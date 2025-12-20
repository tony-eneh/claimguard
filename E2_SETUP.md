# E2 Setup Guide: Deploying to Sepolia Testnet

## Prerequisites

1. **Sepolia ETH**: Get test ETH from a Sepolia faucet
   - https://sepoliafaucet.com/
   - https://www.alchemy.com/faucets/ethereum-sepolia
   - You'll need ~0.05 ETH for deployment + testing

2. **Environment Variables**: Create `.env` file in project root
   ```bash
   cp .env.example .env
   ```

3. **Configure .env**: Add your private key and RPC URL
   ```
   SEPOLIA_RPC_URL=https://sepolia.drpc.org
   SEPOLIA_PRIVATE_KEY=0x... # Your private key (DO NOT COMMIT!)
   SEPOLIA_ADDRESS=0x...     # Your wallet address
   ```

## Deployment Steps

### Step 1: Deploy Contracts to Sepolia

```bash
npx hardhat run scripts/deploy-sepolia.ts --network sepolia
```

This will:
- Deploy EvidenceRegistry, SubjectAttributeRegistry, AccessPolicyManager, AccessAuditLog
- Save deployment info to `deployments/deployment-{timestamp}.json`
- Display contract addresses for .env update

### Step 2: Update .env with Contract Addresses

After deployment completes, copy the contract addresses into `.env`:
```
EVIDENCE_REGISTRY_ADDRESS=0x...
SUBJECT_ATTRIBUTE_REGISTRY_ADDRESS=0x...
ACCESS_POLICY_MANAGER_ADDRESS=0x...
ACCESS_AUDIT_LOG_ADDRESS=0x...
```

### Step 3: Configure PEG Gateway for Sepolia

Update `claimguard-peg/.env`:
```bash
cd claimguard-peg
cp .env.example .env
```

Add:
```
RPC_URL=https://sepolia.drpc.org
CHAIN_ID=11155111
EVIDENCE_REGISTRY_ADDRESS=0x...
SUBJECT_ATTRIBUTE_REGISTRY_ADDRESS=0x...
ACCESS_POLICY_MANAGER_ADDRESS=0x...
ACCESS_AUDIT_LOG_ADDRESS=0x...
```

### Step 4: (Optional) Seed Test Data

⚠️ **Warning**: This will consume Sepolia ETH. Only seed minimal data for E2.

```bash
cd claimguard-peg
npm run seed:viem
```

Or seed manually via scripts:
```typescript
// Create a test subject
await subjectRegistry.registerSubject("alice", ["researcher"], ...)

// Create a test resource
await evidenceRegistry.registerEvidence("evidence-001", ...)

// Create a test policy
await policyManager.createPolicy(...)
```

### Step 5: Start PEG Gateway

```bash
cd claimguard-peg
npm run dev
```

Gateway will connect to Sepolia and serve on `http://localhost:4000`

### Step 6: Run E2 Tests

```bash
cd claimguard-peg
python e2_run.py --base-url http://localhost:4000/api --output-dir experiment_results/e2
```

This will run:
- **Access Latency**: 100 samples, measures P50/P90/P99 with RPC round-trip
- **Throughput**: Concurrency 10/50/100, req/s under real blockchain
- **Policy Confirmation**: 10 samples, tx submission to block inclusion time

Expected runtime: 5-10 minutes (due to real block times)

### Step 7: Analyze E2 Results

```bash
cd claimguard-peg
python analyze_e2.py \
  --e1-dir experiment_results/e1 \
  --e2-dir experiment_results/e2 \
  --output-dir experiment_results/e2 \
  --fig-dir figures/e2
```

Generates:
- `e2_latency_comparison.csv` (Local vs Sepolia)
- `e2_latency_comparison.tex` (LaTeX table)
- `e2_policy_confirmation.csv` (Confirmation times)
- `e2_policy_confirmation.tex` (LaTeX table)
- `e2_latency_comparison.png` (Bar chart)

### Step 8: Wire E2 into Journal

Copy tables/figures to journal directory:
```bash
cp experiment_results/e2/*.tex journal/figures/
cp figures/e2/*.png journal/figures/
```

Add to `journal/paper.tex`:
- E2 subsection after E3
- Latency comparison table
- Policy confirmation table
- Optional: Latency comparison figure
- Interpretation paragraph

## Expected Results

### Latency
- **Local (E1)**: ~60ms P50
- **Sepolia (E2)**: ~200-500ms P50 (includes RPC round-trip)

### Throughput
- **Local (E1)**: 700-820 req/s
- **Sepolia (E2)**: ~5-10 req/s (limited by block time)

### Policy Confirmation
- **Local (E1)**: ~22ms
- **Sepolia (E2)**: ~12-15 seconds (real block time)

## Troubleshooting

### "Insufficient funds"
- Get more Sepolia ETH from faucet
- Check balance: `npx hardhat run scripts/check-balance.ts --network sepolia`

### "Nonce too low"
- Wait for pending transactions to confirm
- Or reset nonce manually

### "RPC timeout"
- Sepolia RPC may be slow during high traffic
- Try alternative RPC: `https://eth-sepolia.g.alchemy.com/v2/YOUR_API_KEY`

### Gateway not connecting
- Verify contract addresses in `.env`
- Check RPC_URL is correct
- Ensure CHAIN_ID=11155111

## Cleanup

After E2 is complete, you can:
1. Keep contracts deployed (no cost for idle contracts)
2. Switch gateway back to local: Update `claimguard-peg/.env` to use `http://127.0.0.1:8545`
3. Archive deployment info for reference
