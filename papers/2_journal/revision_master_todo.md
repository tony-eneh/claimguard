# PACE Journal Revision Master To-Do (Execution Runbook)

Purpose: close reviewer concerns with evidence-backed revisions and implement concrete architectural deltas (not only expanded evaluation) so novelty vs ClaimGuard is explicit and defensible.

Execution status note (latest run):
- E1/E2/E3/E4/E5/E6 runs were executed with fresh outputs in this workspace.
- Sepolia E2 was executed and outputs were written to `claimguard-peg/experiment_results/e2-sepolia/`.
- Local-chain E4 and E5 were re-run after enabling native Docker in WSL and starting PostgreSQL/Mongo via `docker compose`.
- E4 1000-policy seeding required serialized policy creation (`e4_seed_policies.py --concurrency 1`) to avoid nonce-collision failures under automining.
- E5 scripts now complete end-to-end; `e5_audit_query_performance.py` port mapping and `e5_additional_metrics.py` CSV/cleanup issues were fixed.

How to use:
- Check items only when artifact evidence exists (code diffs, logs, tables, figures, manuscript edits).
- Execute phases in order unless a task is explicitly marked parallelizable.
- Treat each phase gate as mandatory before moving to the next phase.

---

## Quick Start (One-Session Bootstrap)

Run these first from repo root:

```bash
npm install
npx hardhat compile
npx hardhat test
cd claimguard-peg && npm install && npm run build && cd ..
python -m pip install -r requirements.txt
```

Create a revision artifacts workspace:

```bash
mkdir -p papers/2_journal/artifacts/{env,delta,experiments,figures,tables,responses}
```

---

## Phase 0 — Revision Program Setup

### 0.1 Scope lock and issue mapping
- [ ] Freeze reviewer concern list from all critiques + human review.
- [x] Create `papers/2_journal/artifacts/responses/concern_to_evidence_matrix.md`.
- [ ] Map each concern to owner + concrete evidence artifact + acceptance criterion.
- [ ] Add a “won’t do now” list with rationale for non-critical stretch tasks.

### 0.2 Reproducible environment
- [x] Record Node/npm/Python versions in `papers/2_journal/artifacts/env/toolchain.txt`.
- [x] Verify clean install + compile + test on fresh shell session.
- [x] Snapshot hardware/software environment in `papers/2_journal/artifacts/env/system_profile.md`.
- [ ] Ensure all experiment scripts can run from top-level command set (Phase 8).

### 0.3 Data and artifact discipline
- [ ] Define canonical output folders per experiment round under `experiment_results/`.
- [ ] Add metadata sidecar per run (commit hash, date, config, seed, env).
- [ ] Add a manifest file for final artifacts:
	- [x] `papers/2_journal/artifacts/manifest.sha256`

### Phase 0 Gate
- [ ] Every concern has measurable evidence target.
- [ ] Any teammate can rerun stack from clean checkout.

---

## Phase 1 — ClaimGuard vs PACE Delta Proof (Truthful Baseline)

### 1.1 Explicit current-state delta
- [ ] Build side-by-side table: ClaimGuard (conference) vs PACE (journal) in `papers/2_journal/artifacts/delta/claimguard_vs_pace_table.md`.
- [ ] Separate reused components from new contributions.
- [ ] Mark current architecture status explicitly: “core architecture reused; journal currently extends evaluation.”

### 1.2 Contribution language correction
- [ ] Rewrite claims to avoid overcalling “new architecture” before Phase 2 implementation.
- [ ] Align abstract/introduction/conclusion wording.

### 1.3 Prior work positioning
- [ ] Update related-work matrix to show what prior systems evaluate vs omit.
- [ ] Add quantitative rows where possible: latency, throughput, revocation model, auditability.

### Phase 1 Gate
- [ ] Skeptical reviewer can see exactly what is reused and what is newly added.

---

## Phase 2 — Architectural Delta Implementation (NEW)

Goal: introduce concrete architecture changes beyond ClaimGuard.

### 2.0 Required implementation order
1. Emergency Revocation Overlay (mandatory)
2. Async/Batched Audit Plane (mandatory)
3. Indexed Policy Evaluation Engine (mandatory)
4. Federated PEG signing (optional in this revision unless time permits)

### 2.1 Delta A — Emergency Revocation Overlay (mandatory)

Problem addressed: public-network policy-finality window creates revocation lag risk.

Code targets:
- `contracts/AccessPolicyManager.sol`
- `claimguard-peg/src/` (access path + middleware)
- New: `claimguard-peg/src/revocation_overlay.ts`

Implementation tasks:
- [ ] Add subject-level emergency deny overlay checked before token issuance.
- [ ] Overlay precedence rule: emergency deny overrides on-chain allow.
- [ ] Add admin endpoint for emergency deny/unset + audit emission.
- [ ] Add TTL/expiry semantics for emergency overlays to avoid stale lockout.
- [ ] Add explicit manuscript threat-model update: “fast revocation path vs eventual on-chain finalization.”

Validation tasks:
- [ ] Add test: compromised subject denied immediately without waiting for chain finality.
- [ ] Add experiment: measure emergency revoke propagation latency (target sub-second at PEG boundary).

Run:

```bash
npx hardhat test
cd claimguard-peg && npm run build && cd ..
python claimguard-peg/e4_revocation_test.py
```

### 2.2 Delta B — Async/Batched Audit Plane (mandatory)

Problem addressed: baseline fairness criticism from synchronous audit coupling.

Code targets:
- `contracts/AccessAuditLog.sol`
- `claimguard-peg/src/` (audit pipeline)
- New: `claimguard-peg/src/audit_queue.ts`
- New: `claimguard-peg/src/audit_batcher.ts`

Implementation tasks:
- [ ] Split decision path from audit persistence path.
- [ ] Add asynchronous queue with bounded retries + dead-letter handling.
- [ ] Add batch anchor mode (Merkle root or grouped hashes) for periodic on-chain anchoring.
- [ ] Keep compatibility mode: synchronous audit toggle for A/B experiments.

Validation tasks:
- [ ] Benchmark sync vs async under same workload.
- [ ] Report decision latency, audit lag, dropped-event rate, retry success rate.

Run:

```bash
cd claimguard-peg && npm run build && cd ..
python e5_audit_query_performance.py
python e5_additional_metrics.py
python analyze_e5.py
```

### 2.3 Delta C — Indexed Policy Evaluation Engine (mandatory)

Problem addressed: linear rule scan architecture does not scale cleanly.

Code targets:
- `contracts/AccessPolicyManager.sol`
- `contracts/Types.sol` (if index key struct needed)

Implementation tasks:
- [ ] Add policy indexing strategy (e.g., role+action+resourceType buckets).
- [ ] Preserve existing policy semantics and conflict resolution.
- [ ] Add migration path for existing policies.
- [ ] Add gas and latency comparison with previous linear scan mode.

Validation tasks:
- [ ] Add tests for equivalence: old vs new evaluator decisions match.
- [ ] Add E4 extension run up to higher policy counts.

Run:

```bash
npx hardhat test
cd claimguard-peg && python e4_seed_policies.py && python e4_run.py && cd ..
python claimguard-peg/analyze_e4.py
```

### 2.4 Delta D — Federated PEG Signing (optional / stretch)

Problem addressed: single gateway signing key as concentration risk.

Code targets:
- `claimguard-peg/src/` auth/signing modules
- Optional new contract for signer set governance

Implementation tasks:
- [ ] Implement M-of-N signer policy (or staged dual-signature fallback).
- [ ] Add signer rotation and failover procedure.
- [ ] Add key-compromise blast-radius analysis.

Validation tasks:
- [ ] Simulate one signer compromise/unavailability while preserving service.

### 2.5 Delta artifacts to produce
- [x] `papers/2_journal/artifacts/delta/architecture_delta_summary.md`
- [x] `papers/2_journal/artifacts/delta/before_after_sequence.md`
- [ ] `papers/2_journal/artifacts/delta/delta_experiment_results.csv`

### Phase 2 Gate
- [ ] At least 3 mandatory architectural deltas implemented and tested (A, B, C).
- [ ] Manuscript can claim concrete architecture changes, not only broader evaluation.

---

## Phase 3 — Experimental Integrity Rebuild (E1–E4 + Delta Experiments)

### 3.1 Measurement protocol hardening
- [ ] Standardize trial counts, warm-up, steady-state, cooldown.
- [ ] Define concurrency/load profile per experiment.
- [ ] Include confidence intervals/dispersion metrics consistently.
- [ ] Clarify all symbols (N, runs, requests, subjects, policies) in captions.

### 3.2 Number consistency audit
- [ ] Recompute all manuscript numbers from source outputs.
- [ ] Reconcile E1 vs E2 local discrepancies with setup differences.
- [ ] Ensure every prose number maps to canonical source artifact.
- [ ] Add pre-submission consistency script/checklist.

### 3.3 Core reruns
- [x] E1 rerun with fixed seeds + repeated trials.
- [x] E2 rerun on Sepolia with tail latency and confirmation sampling.
- [x] E3 rerun with role-spoof split: malformed vs well-formed unauthorized.
- [x] E4 rerun with churn + emergency revoke scenarios.

### 3.4 New delta-focused experiments
- [ ] E5-A: emergency overlay revoke latency vs on-chain-only revoke.
- [ ] E5-B: sync vs async audit latency + reliability.
- [ ] E5-C: indexed vs linear policy evaluation at scale.
- [ ] E6-lite (IoT/Edge): attestation-aware edge ingest profile vs standard ingest.

E6-lite output requirements:
- [x] Create `experiment_results/e6/` outputs + metadata sidecar.
- [x] Report exactly 4 metrics: ingest latency overhead, replay block rate, invalid-attestation reject rate, decision latency under burst.
- [x] Keep workload bounded (100-500 simulated edge producers) and avoid broad IoT claims.

Run:

```bash
cd claimguard-peg
python e2_run.py
python e3_run.py
python e4_run.py
python run_experiments.py
cd ..
python analyze_e5.py
python analyze_e6.py
```

### Phase 3 Gate
- [ ] All published numbers regenerated from scripts + raw outputs.
- [ ] No unresolved numerical contradiction.

---

## Phase 4 — Baselines and Fairness Upgrades

### 4.1 Hybrid-Audit fairness correction
- [ ] Keep synchronous variant.
- [ ] Add asynchronous/batched variant.
- [ ] Benchmark both and report caveats/interpretation boundaries.

### 4.2 Additional baseline family
- [ ] Add one stronger modern baseline (permissioned-chain ABAC or DID-mediated control).
- [ ] Document representativeness and feasibility assumptions.

### 4.3 Baseline transparency
- [ ] Publish baseline implementation/config knobs.
- [ ] Add sensitivity analysis for design choices that change outcomes.

### Phase 4 Gate
- [ ] Comparative claims robust against strawman-baseline criticism.

---

## Phase 5 — Cross-Domain Validation Strengthening

### 5.1 Empirical anchor beyond mapping
- [ ] Keep mapping tables.
- [ ] Add at least one reduced-scale empirical run outside insurance (healthcare or legal).
- [ ] Report whether trend directions hold.

### 5.2 Claims calibration
- [ ] Replace universal language with scoped wording.
- [ ] Distinguish “empirically shown” vs “architecturally transferable.”

### 5.3 IoT/Edge inclusion track (bounded scope)

Scope guardrails (must keep):
- [ ] Position IoT as a deployment profile of PACE, not a new standalone IoT framework.
- [ ] Do not add unrelated IoT features (routing, device scheduling, edge ML, federated learning).
- [ ] Constrain contribution to “edge-generated evidence governance with attestation-aware ingest.”

Architecture/profile tasks:
- [ ] Add an Edge Evidence Ingress Adapter concept to methodology text.
- [ ] Define minimal edge attributes: `deviceClass`, `attestationLevel`, `firmwareEpoch`, `ingestWindow`.
- [ ] Specify verification path: device/edge -> gateway verification -> on-chain policy decision -> capability.

Implementation tasks (minimal viable):
- [ ] Add edge ingest endpoint in `claimguard-peg/src/` (new module `edge_ingest.ts` or equivalent).
- [ ] Add attestation verification stub/interface (deterministic mock acceptable for journal experiment).
- [ ] Bind verified edge metadata into access/policy context without breaking existing flows.

Experiment tasks:
- [ ] Implement E6-lite harness script(s) under `claimguard-peg/` for bounded edge bursts.
- [ ] Compare standard ingest vs attestation-aware ingest under identical load profile.
- [ ] Add explicit limitations: simulation-based edge clients; no hardware-rooted attestation in this revision.

### Phase 5 Gate
- [ ] Cross-domain section has at least one empirical anchor.
- [ ] IoT/Edge addition remains tightly scoped and does not change paper thesis.

---

## Phase 6 — Security, Cost, Scalability, Deployment Reality

### 6.1 Threat model precision
- [ ] Standardize terms: honest-but-curious vs malicious vs compromised component.
- [ ] Explicitly state cloud-config assumptions.
- [ ] Separate architectural guarantees from operational controls.

### 6.2 Residual risk table
- [ ] Add risk/condition/impact/mitigation table.
- [ ] Include gateway availability, key management, and token TTL windows.

### 6.3 Economic + scale reporting
- [ ] Expand gas/cost table with L1/L2/consortium assumptions.
- [ ] Report tested envelope and practical bottlenecks.
- [ ] Add per-operation lifecycle costs (create/update/revoke/access/audit).

### 6.4 Production-readiness calibration
- [ ] Replace absolute production-ready claims with maturity-level wording.
- [ ] Add deployment blueprint: pilot → hardening → consortium rollout.

### Phase 6 Gate
- [ ] Security/cost/scale/deployment claims are bounded and credible.

---

## Phase 7 — Manuscript Rewrite and Integration

### 7.1 Structural refactor
- [ ] Align with target journal structure.
- [ ] Split implementation/observation from discussion.
- [ ] Remove duplicated claims across sections.

### 7.2 New required subsection
- [ ] Add “Architectural Delta from ClaimGuard” subsection with:
	- [ ] explicit reused components
	- [ ] explicit new components (A/B/C deltas)
	- [ ] before/after sequence diagram reference
	- [ ] evidence references to experiments
- [ ] Add “IoT/Edge Deployment Profile (E6-lite)” subsection with:
	- [ ] bounded scope statement
	- [ ] edge ingest sequence and trust assumptions
	- [ ] E6-lite metrics and limitations

### 7.3 Figures/tables/captions
- [ ] Rebuild all plots from rerun outputs.
- [ ] Ensure complete headers and legibility.
- [ ] Reference every figure/table in text.

### 7.4 Language pass
- [ ] Remove unsupported absolutes (first, universal, production-ready).
- [ ] Ensure claims map to exact evidence artifact.

Compile:

```bash
cd papers/2_journal
pdflatex paper.tex
bibtex paper
pdflatex paper.tex
pdflatex paper.tex
cd ../..
```

### Phase 7 Gate
- [ ] Manuscript is coherent with no claim-evidence mismatch.

---

## Phase 8 — Reproducibility, Artifact, Reviewer Package

### 8.1 One-command rerun package
- [x] Add script `scripts/run_journal_revision_bundle.sh` that executes all required runs.
- [ ] Include raw + processed outputs + plotting scripts + manifests.
- [ ] Validate on fresh session.

### 8.2 Reviewer response packet
- [ ] Concern-by-concern response matrix with exact paper locations.
- [ ] Before/after wording snippets for disputed claims.
- [ ] Baseline fairness explanation with async/sync evidence.

### 8.3 Final quality checks
- [ ] Consistency pass for numbers/notation/citations.
- [ ] Bibliography completeness and formatting check.
- [ ] Grammar/style pass.
- [ ] PDF compile with no broken references.

### Phase 8 Gate
- [ ] Submission bundle is reproducible, auditable, reviewer-ready.

---

## Optional Stretch Items
- [ ] Federated PEG signing (if not completed in Phase 2.4).
- [ ] Formal verification checks for critical contracts.
- [ ] Extended-scale tests (10k+ policies).
- [ ] Additional public-network variance runs across days/time windows.

---

## Master Definition of Done
- [ ] Every major reviewer concern has direct empirical/textual evidence.
- [ ] No contradiction remains in results, claims, or threat model.
- [ ] Novelty vs ClaimGuard is explicit with implemented architectural deltas.
- [ ] Baseline comparisons are fair and transparently documented.
- [ ] Final paper can survive hostile-but-fair rereview based on evidence.