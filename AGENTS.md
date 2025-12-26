# Agent Guidelines for ClaimGuard

This document provides coding agents with essential information about building, testing, and maintaining the ClaimGuard blockchain-based access control system.

## Project Overview

ClaimGuard is an Attribute-Based Access Control (ABAC) system for insurance claim evidence using Ethereum smart contracts. The project consists of:
- **Solidity contracts** (`contracts/`) - On-chain policy engine and registries
- **Policy Enforcement Gateway (PEG)** (`claimguard-peg/src/`) - Express.js API server
- **Deployment scripts** (`scripts/`) - Contract deployment automation
- **Python experiments** (`*_run.py`, `analyze_*.py`) - Performance testing and analysis

## Build, Test & Run Commands

### Smart Contracts
```bash
# Compile contracts
npx hardhat compile

# Run all tests
npx hardhat test

# Run a single test file
npx hardhat test test/Counter.ts

# Start local development node (port 8545)
npx hardhat node

# Deploy contracts to local network
npm run deploy

# Deploy to Sepolia testnet
npx hardhat ignition deploy ignition/modules/ClaimguardContracts.ts --network sepolia
```

### Policy Enforcement Gateway (PEG)
```bash
cd claimguard-peg

# Development mode (auto-reload)
npm run dev

# Build TypeScript to JavaScript
npm run build

# Run production build
npm start

# Seed blockchain with test data
npm run seed:viem
```

### Python Experiments
```bash
# Set up environment (first time only)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Run experiments
python e2_run.py
python e3_run.py
python e4_run.py

# Analyze results
python analyze_e2.py
python analyze_e3_improved.py
python analyze_e4.py
```

## Code Style Guidelines

### TypeScript/JavaScript

#### Imports
- Use ES6 imports: `import { foo } from './bar'`
- Import types separately: `import type { Server } from 'http'`
- Group imports: stdlib → external packages → local modules
- Use named imports for clarity

Example:
```typescript
import fs from 'fs';
import path from 'path';
import express from 'express';
import { ethers } from 'ethers';
import type { Request, Response } from 'express';
import { config } from './config';
```

#### Formatting
- **Indentation**: 2 spaces (no tabs)
- **Quotes**: Single quotes for strings
- **Semicolons**: Always use semicolons
- **Line length**: Keep under 100 characters where practical
- **Trailing commas**: Use in multi-line objects/arrays

#### Types
- Always use TypeScript strict mode (`"strict": true`)
- Prefer explicit types for function parameters and returns
- Use `interface` for object shapes, `type` for unions/aliases
- Define enums that match Solidity enums (see `types.ts`)
- Use `bigint` (not `BigInt`) for Ethereum uint256 values

Example:
```typescript
export interface AccessRequestBody {
  subject: string;      // EVM address
  resourceId: number;   // uint256
  action: keyof typeof Action;
}

export function getContracts(
  providerOrSigner: ethers.Provider | ethers.Signer
): { apm: ethers.Contract; evidenceReg: ethers.Contract } {
  // implementation
}
```

#### Naming Conventions
- **Variables/functions**: camelCase (`accessRouter`, `createProvider`)
- **Types/interfaces**: PascalCase (`AccessRequestBody`, `Capability`)
- **Constants**: UPPER_SNAKE_CASE for env vars, camelCase for others
- **Private functions**: Prefix with underscore if needed
- **Enums**: PascalCase for enum name, UPPER_CASE for values

#### Error Handling
- Use try-catch for async operations
- Return appropriate HTTP status codes (400, 403, 404, 500)
- Log errors with context: `console.error('[ERROR] Context:', err)`
- Include error details in development: `details: String(err.message || err)`
- Validate input early and return clear error messages

Example:
```typescript
try {
  const allowed = await apm.checkAccess(subject, resourceId, actionEnum);
  if (!allowed) {
    return res.status(403).json({
      allowed: false,
      reason: "Access denied by on-chain policy"
    });
  }
} catch (err: any) {
  console.error('[ERROR] Access check failed:', err);
  return res.status(500).json({ 
    error: "Internal error", 
    details: String(err.message || err) 
  });
}
```

#### Async/Await
- Always use async/await over promises.then()
- Use `await` for blockchain calls (they return promises)
- Handle deployment transaction receipts: `.deploymentTransaction()?.wait()`
- Add delays between transactions if needed: `await sleep(500)`

### Solidity

#### Version & License
```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
```

#### Formatting
- **Indentation**: 4 spaces
- **Visibility**: Always explicit (public, external, internal, private)
- **Order**: State variables → events → modifiers → constructor → functions
- **Comments**: Use NatSpec format (`///` or `/** */`)

#### Naming
- **Contracts**: PascalCase (`AccessPolicyManager`)
- **Functions**: camelCase (`checkAccess`, `getResource`)
- **State variables**: camelCase with underscore prefix for private (`_policies`)
- **Constants**: UPPER_SNAKE_CASE
- **Events**: PascalCase (`PolicyCreated`, `AccessGranted`)

#### Types
- Use explicit uint256, uint8, etc. (not uint)
- Use custom enums from Types.sol (Role, Action, ResourceType)
- Use structs for complex data (PolicyRule, Resource, SubjectAttrs)

### Python

- Follow PEP 8 style guide
- Use 4-space indentation
- Type hints for function parameters when practical
- Use `if __name__ == "__main__":` for entry points

## Project-Specific Patterns

### Blockchain Interaction
1. Create provider: `new ethers.JsonRpcProvider(url)`
2. Create wallet/signer: `new ethers.Wallet(privateKey, provider)`
3. Load contract artifacts from `artifacts/contracts/`
4. Instantiate contracts with `new ethers.Contract(address, abi, signer)`

### Environment Configuration
- Store sensitive data in `.env` files (never commit!)
- Use `dotenv` to load: `import dotenv from 'dotenv'; dotenv.config();`
- Validate required env vars on startup (see `config.ts:validateConfig()`)
- Support multiple modes: claimguard, rbac, hybrid

### Express Routes
- Export router factory functions that accept dependencies
- Validate request body before processing
- Use typed request/response: `Request<Params, Response, Body>`
- Return JSON with consistent structure

## Common Pitfalls

1. **BigInt conversion**: Use `BigInt()` when passing JS numbers to contracts as uint256
2. **Nonce management**: Manually track nonces during rapid deployments
3. **Transaction waiting**: Always `.wait()` for transaction receipts before proceeding
4. **Contract addresses**: Update `.env` after each deployment
5. **Module type**: Package is ESM (`"type": "module"`), use `.js` in imports if needed

## Testing Workflow

1. Start Hardhat node: `npx hardhat node`
2. Deploy contracts: `npm run deploy`
3. Update `claimguard-peg/.env` with deployed addresses
4. Start PEG: `cd claimguard-peg && npm run dev`
5. Seed data: `npm run seed:viem`
6. Run experiments or tests

## Paper Writing

The project has two academic papers documenting the research:

### Conference Paper (COMPLETED)
Located in `conference/` directory. This is the **completed** conference version.

```bash
cd conference

# Compile LaTeX (with BibTeX)
pdflatex paper.tex
bibtex paper
pdflatex paper.tex
pdflatex paper.tex

# Or use latexmk for automatic compilation
latexmk -pdf paper.tex

# View the PDF
# Output: paper.pdf
```

**Content**: Initial ClaimGuard system, basic experiments (E1), architecture description.

### Journal Paper (ONGOING)
Located in `journal/` directory. This is the **extended journal version** currently in progress.

```bash
cd journal

# Compile LaTeX
pdflatex paper.tex
bibtex paper
pdflatex paper.tex
pdflatex paper.tex

# Or use latexmk
latexmk -pdf paper.tex

# Analyze paper length
python analyze_paper_length.py

# Convert E2 figures from PDF to PNG
python convert_e2_pdfs_to_png.py
```

**Experiments completed** (extended from conference):
- **E1**: Quantitative RBAC baseline comparison
- **E2**: Real-world network conditions with latency injection
- **E3**: Security stress experiments (DoS, replay attacks, etc.)
- **E4**: Policy churn and scale tests (100-1k policies, 500-1k subjects)

**Key differences from conference**:
- Extended experimental evaluation with RBAC baseline
- Dedicated security analysis section
- Network realism experiments
- Scale testing with larger datasets
- Quantitative security metrics

**Remaining work for journal submission**:
1. **Refactor section arrangement** - Adapt to journal best practices for improved readability and flow
2. **Convert enumeration-heavy style to prose** - Transform bullet-point heavy sections into narrative format
3. **Apply new template** - Migrate from current format to `claimguard_target_journal_template.tex`

**Do NOT** add to journal paper (marked as future work):
- ML-based risk scoring
- Anomaly detection models
- Cross-chain or Fabric integration

### LaTeX Style Guidelines
- Use IEEEtran document class for both papers
- Figures go in `conference/figures/` or `journal/figures/`
- References in `refs.bib` using BibTeX
- Follow IEEE citation style
- Keep figures as PNG or PDF format

## File Locations

- Contract artifacts: `artifacts/contracts/<Name>.sol/<Name>.json`
- Deployment records: `deployments/deployment-<timestamp>.json`
- Test data outputs: `claimguard-peg/outputs/subjects.json`, `resources.json`
- Experiment results: `experiment_results/claimguard/*.csv`
- Conference paper: `conference/paper.tex` (completed)
- Journal paper: `journal/paper.tex` (ongoing)
- Paper figures: `conference/figures/`, `journal/figures/`
