# PACE Journal Revision Master To-Do

Purpose: close all reviewer concerns with evidence-backed revisions (not argument-only), including reruns, new baselines, expanded analysis, and full manuscript rewrite.

How to use:
- Check items only when artifact evidence exists (tables, logs, scripts, figures, text edits).
- Treat each phase gate as mandatory before moving to the next phase.

---

## Phase 0 — Revision Program Setup

### 0.1 Scope lock and issue mapping
- [ ] Freeze reviewer concern list from all critiques + human review.
- [ ] Map each concern to one owner and one concrete evidence artifact.
- [ ] Create a concern-to-evidence matrix (Concern → New content/experiment/table/section).
- [ ] Define acceptance criterion per concern (what would convince a skeptical reviewer).
- [ ] Add a “won’t do now” list with rationale for non-critical stretch tasks.

### 0.2 Reproducible environment
- [ ] Pin Node, npm, Python versions used for all reruns.
- [ ] Pin dependency lockfiles and verify clean install from scratch.
- [ ] Snapshot hardware/software environment used for experiments.
- [ ] Ensure all experiment scripts are runnable from one top-level command set.
- [ ] Add a single experiment runbook document for end-to-end replication.

### 0.3 Data and artifact discipline
- [ ] Define canonical output folders for each experiment round.
- [ ] Add metadata sidecar per run (commit hash, date, config, seed, env).
- [ ] Add naming convention for figures/tables linked to manuscript sections.
- [ ] Add checksum or manifest file for final artifacts.

### Phase 0 Gate
- [ ] Every concern has a measurable evidence target.
- [ ] Any teammate can rerun the stack from clean checkout using the runbook.

---

## Phase 1 — Novelty/Incrementality (ClaimGuard Delta) Proof

### 1.1 Explicit delta from conference version
- [ ] Build a side-by-side table: ClaimGuard (conference) vs PACE (journal).
- [ ] Separate “reused components” from “new contributions”.
- [ ] Document architectural changes (if any) with precise scope.
- [ ] Document methodological changes: E1/E2/E3/E4(+new) additions.
- [ ] Document operational/deployment additions absent in conference version.

### 1.2 Contribution statement rewrite
- [ ] Rewrite contribution bullets to avoid overclaiming “entirely new architecture” unless proven.
- [ ] Frame novelty as generalized framework + expanded validation where appropriate.
- [ ] Add one paragraph defending scientific value of controlled extension work.
- [ ] Ensure abstract/introduction/conclusion use the same novelty language.

### 1.3 Prior work positioning
- [ ] Update related-work matrix to explicitly show what prior systems evaluate and what they do not.
- [ ] Add missing closest alternatives flagged by reviewers.
- [ ] Include quantitative comparison rows where possible (latency, throughput, revocation model, auditability).

### Phase 1 Gate
- [ ] A skeptical reviewer can clearly see what is new, what is reused, and why it matters.

---

## Phase 2 — Experimental Integrity Rebuild (Current E1–E4)

### 2.1 Measurement protocol hardening
- [ ] Standardize trial counts across experiments (or justify exceptions explicitly).
- [ ] Define warm-up, steady-state, cooldown protocol.
- [ ] Define concurrency levels and load profile per experiment.
- [ ] Include confidence intervals or dispersion metrics consistently.
- [ ] Clarify all symbols (N, runs, requests, subjects, policies) in each table caption.

### 2.2 Number consistency audit
- [ ] Recompute all manuscript numbers from source outputs.
- [ ] Reconcile any E1 vs E2 local discrepancies with explicit setup differences.
- [ ] Ensure every prose number appears in exactly one canonical source table/figure.
- [ ] Add a pre-submission consistency script/checklist.

### 2.3 E1 rerun (baseline comparison, local)
- [ ] Rerun local benchmark with fixed seeds and repeated trials.
- [ ] Capture p50/p95/p99, throughput, error rates for all baselines.
- [ ] Include resource usage (CPU/memory) with hardware context.
- [ ] Replot E1 figures from regenerated CSV outputs.

### 2.4 E2 rerun (public testnet realism)
- [ ] Rerun Sepolia tests with clear tx confirmation sampling.
- [ ] Report both median and tail behavior for access and policy updates.
- [ ] Separate read-path latency from policy-update finality latency.
- [ ] Add operational interpretation for incident-response windows.

### 2.5 E3 rerun (adversarial)
- [ ] Redesign role-spoofing test cases: malformed input vs valid-but-unauthorized identity.
- [ ] Report attack outcome taxonomy: blocked by validation, blocked by authorization, succeeded.
- [ ] Recompute false accept/false reject with strict definitions.
- [ ] Ensure no contradiction between E3 table and abstract/conclusion claims.

### 2.6 E4 rerun (policy churn/scale)
- [ ] Rerun with same and expanded policy/subject scales.
- [ ] Report latency drift under churn (create/update/revoke cycles).
- [ ] Add operationally relevant churn scenarios (burst updates, emergency revokes).

### Phase 2 Gate
- [ ] All published numbers are regenerated and reproducible from scripts + raw outputs.
- [ ] No unresolved numerical contradiction remains.

---

## Phase 3 — New Baselines and Fairness Upgrades

### 3.1 Hybrid-Audit fairness correction
- [ ] Implement asynchronous/batched audit variant (not only synchronous).
- [ ] Benchmark sync vs async hybrid under same workload.
- [ ] Report fairness caveat and interpretation boundaries.

### 3.2 Additional baseline families (at least one strong addition)
- [ ] Add one stronger modern baseline relevant to reviewer concerns (permissioned-chain ABAC, DID-based control, or cryptographic policy enforcement proxy).
- [ ] Document why selected baseline is representative and feasible.
- [ ] Normalize benchmarking assumptions across systems.

### 3.3 Baseline transparency
- [ ] Publish baseline implementation details and config knobs.
- [ ] Explicitly disclose where baseline design choices differ from production deployments.
- [ ] Add sensitivity analysis where baseline design materially changes results.

### Phase 3 Gate
- [ ] Comparative claims are robust against “strawman baseline” criticism.

---

## Phase 4 — Cross-Domain Validation Strengthening

### 4.1 From mapping-only to evidence-backed portability
- [ ] Keep configuration mapping tables for healthcare/legal/supply-chain.
- [ ] Add at least one empirical mini-run outside insurance (even reduced scale).
- [ ] Report whether performance/security trends hold in the added domain.

### 4.2 Claims calibration
- [ ] Replace universal language with scope-accurate wording where needed.
- [ ] Distinguish “demonstrated empirically” from “architecturally transferable”.

### Phase 4 Gate
- [ ] Cross-domain section includes at least one empirical anchor beyond configuration examples.

---

## Phase 5 — Security and Threat-Model Reinforcement

### 5.1 Threat model precision
- [ ] Standardize terms: honest-but-curious vs malicious vs compromised component.
- [ ] Add explicit assumptions for cloud configuration correctness and gateway trust.
- [ ] State what guarantees are architectural vs operational.

### 5.2 Residual risk and mitigations
- [ ] Add a clear residual-risk table (risk, condition, impact, mitigation).
- [ ] Include gateway availability and key-management failure modes.
- [ ] Include revocation-window risk due to token TTL and chain finality.

### 5.3 Security validation depth
- [ ] Expand adversarial suite where feasible (replay variants, token misuse, denial patterns).
- [ ] Add negative controls to prove test harness is not masking failures.
- [ ] Add attack reproducibility notes (exact inputs and expected outcomes).

### Phase 5 Gate
- [ ] Security claims and limits are explicit, test-backed, and non-contradictory.

---

## Phase 6 — Cost, Scalability, and Deployment Reality

### 6.1 Economic reporting
- [ ] Expand gas/cost reporting with network context (L1/L2/consortium assumptions).
- [ ] Include confidence ranges for cost estimates where volatility applies.
- [ ] Add per-operation cost table for policy lifecycle operations.

### 6.2 Scalability envelope
- [ ] State tested limits clearly (current max policies/subjects/workload).
- [ ] Add at least one larger-scale run if feasible within resources.
- [ ] Document expected bottlenecks and practical limits.

### 6.3 Production-readiness calibration
- [ ] Replace absolute production-readiness claims with evidence-based maturity level.
- [ ] Add deployment blueprint: pilot stage, hardening stage, consortium rollout stage.
- [ ] Add required controls list (HA gateway, monitoring, key custody, incident response).

### Phase 6 Gate
- [ ] Cost/scalability/deployment claims are bounded and operationally credible.

---

## Phase 7 — Full Manuscript Rewrite and Integration

### 7.1 Structural refactor (journal template alignment)
- [ ] Ensure final structure aligns with target journal format.
- [ ] Split implementation/observation from discussion/analysis cleanly.
- [ ] Remove duplicated text across abstract/introduction/results/discussion.

### 7.2 Section-by-section rewrite
- [ ] Introduction: gap, motivation, scoped contributions, paper roadmap.
- [ ] Related Work: sharpened matrix + quantitative/qualitative positioning.
- [ ] Methodology: architecture, protocol flow, threat model, assumptions.
- [ ] Implementation/Observation: setup, datasets, baselines, metrics, experiment outputs.
- [ ] Discussion: interpretation, limitations, deployment implications, transferability.
- [ ] Conclusion: contributions aligned to demonstrated evidence only.

### 7.3 Figures, tables, and captions
- [ ] Rebuild all plots from rerun outputs.
- [ ] Ensure table headers are complete and non-truncated.
- [ ] Ensure every figure/table is legible in print and referenced in text.
- [ ] Add appendix references for extended data where needed.

### 7.4 Language and claims pass
- [ ] Remove unsupported absolutes (first, universal, production-ready) unless substantiated.
- [ ] Ensure tense and terminology consistency throughout.
- [ ] Ensure claims match exact evidence source.

### Phase 7 Gate
- [ ] Manuscript reads as one coherent story, with no claim-evidence mismatch.

---

## Phase 8 — Reproducibility, Artifact, and Reviewer Package

### 8.1 Artifact package
- [ ] Prepare scripts for one-command rerun per experiment group.
- [ ] Include raw outputs + processed outputs + plotting scripts.
- [ ] Include environment and configuration manifests.
- [ ] Validate artifact package on a fresh machine/session.

### 8.2 Reviewer response packet
- [ ] Build a concern-by-concern response matrix (Concern → What changed → Where in paper → Evidence artifact).
- [ ] Include before/after claim wording for major disputed points.
- [ ] Include list of newly added baselines and why they address fairness concerns.

### 8.3 Final quality checks
- [ ] Full consistency pass for numbers, notation, and citations.
- [ ] Check bibliography completeness and formatting.
- [ ] Spell/grammar and style pass.
- [ ] PDF compile checks with no broken refs/citations.

### Phase 8 Gate
- [ ] Submission bundle is reproducible, auditable, and reviewer-ready.

---

## Optional Stretch Items (If Time Allows)
- [ ] Add formal verification plan or preliminary checks for critical contracts.
- [ ] Add extended-scale tests beyond current envelope (10k+ policy scenarios).
- [ ] Add user/admin workload study (policy authoring effort and operational burden).
- [ ] Add additional public network runs for variance across days/time windows.

---

## Master Definition of Done
- [ ] Every major reviewer concern has direct empirical or textual evidence.
- [ ] No major contradiction remains in results, claims, or threat model.
- [ ] Novelty vs ClaimGuard is explicit and defensible.
- [ ] Baseline comparisons are fair and transparently documented.
- [ ] Final paper can survive a hostile-but-fair rereview based on evidence.