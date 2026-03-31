# Concern-to-Evidence Matrix

This matrix ties the main journal rewrite concerns to concrete manuscript locations and repository artifacts.

| Concern | Revision response | Evidence artifact | Manuscript anchor | Status |
|---|---|---|---|---|
| Paper is too insurance-specific. | Reframed the problem as multi-stakeholder digital evidence governance across healthcare, legal, insurance, and supply chain, while retaining insurance as the validation domain. | Cross-domain framing and mapping tables in the manuscript; bounded E6-lite profile. | Introduction, Related Work, Cross-Domain Applicability, E6-lite | Closed |
| Novelty vs. conference ClaimGuard is unclear. | Added an explicit delta subsection separating preserved ClaimGuard core from journal-era evaluation broadening and planned future architectural extensions. | `artifacts/delta/architecture_delta_summary.md`; `artifacts/delta/before_after_sequence.md` | Architectural Delta from ClaimGuard | Closed for manuscript positioning |
| Evaluation lacks strong baselines. | Added RBAC-DB and Hybrid-Audit baselines for latency, throughput, and policy-operation comparison. | Existing paper tables/figures; outputs under `claimguard-peg/experiment_results/` | E1 result sections | Closed |
| Results do not reflect public-network conditions. | Added Sepolia E2 measurements and discussion of RPC and confirmation overhead. | `claimguard-peg/experiment_results/e2-sepolia/`; generated figures under `claimguard-peg/figures/` | E2 result section | Closed |
| Security claims are not empirically stress-tested. | Added E3 attack suite covering cloud bypass, gateway abuse, role spoofing, replay, and revocation evasion. | `claimguard-peg/experiment_results/e3/` | E3 result section | Closed |
| Scalability language overstates implementation maturity. | Revised the manuscript to report stable measured behavior without claiming an indexed evaluator that the contract does not implement. | `contracts/AccessPolicyManager.sol`; E4 outputs under `claimguard-peg/experiment_results/e4/` | E4 result section; Comparative Analysis; Conclusion | Closed with calibrated wording |
| Revocation wording overstates storage-boundary behavior. | Revised the manuscript to distinguish prompt policy-layer denial from residual capability lifetime at the storage boundary. | E4 revocation summary CSV; revised manuscript prose | Abstract, Methodology, Discussion, Conclusion | Closed with bounded claim |
| IoT/edge scope is absent or overbroad. | Added E6-lite as a bounded deployment profile with exactly four reported metrics and explicit limitations. | `papers/2_journal/artifacts/experiments/e6_summary.json` | IoT/Edge Deployment Profile (E6-lite) | Closed |
| Reproducibility package is incomplete. | Added a single rerun script for the documented setup, experiments, analytics, and paper build, with Sepolia kept optional. | `scripts/run_journal_revision_bundle.sh`; `artifacts/env/toolchain.txt`; `artifacts/env/system_profile.md` | Runbook support artifact | Closed for repository packaging |

Notes:

- The manuscript now avoids claiming an implemented indexed policy engine, emergency gateway overlay, or async audit plane that does not exist in the current repository.
- Remaining architectural deltas are documented as future engineering paths rather than reported implementation facts.