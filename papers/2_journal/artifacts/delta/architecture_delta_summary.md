# Architectural Delta Summary

## ClaimGuard core retained

The journal manuscript intentionally preserves the core ClaimGuard execution model:

- Ethereum-compatible smart contracts remain the policy anchor.
- The Policy Enforcement Gateway remains the off-chain mediation point.
- Short-lived capability issuance remains the mechanism that binds on-chain authorization to storage access.
- Subject and evidence registries remain the primary metadata sources for access evaluation.

This continuity is deliberate. The journal contribution is an extension and hardening effort, not a claim of a wholly new trust boundary or contract topology.

## What changed in the journal revision

The concrete journal-era delta is mainly evaluation depth and framing quality:

- Added explicit comparison against RBAC-DB and Hybrid-Audit baselines.
- Added public-network validation on Sepolia to capture confirmation and RPC costs.
- Added adversarial stress experiments instead of relying only on narrative security arguments.
- Added policy-churn and scale measurements up to 1000 policies and 1000 subjects.
- Added a bounded IoT/edge deployment profile experiment without turning the paper into a separate IoT framework.

## What is not claimed as implemented

Repository inspection shows that the current contract path still uses a linear scan over policies with first-match allow semantics in `AccessPolicyManager.checkAccess`. The manuscript therefore treats the following as extension paths, not shipped deltas:

- Emergency revocation overlay at the PEG boundary
- Asynchronous or batched audit plane
- Indexed policy evaluation engine

These remain valid next-step engineering directions, but they are not reported as completed architectural replacements in the revised manuscript.

## Defensible journal novelty

The defensible claim is that PACE preserves the ClaimGuard core while broadening the work into a more rigorously evaluated, domain-neutral, empirically grounded framework for multi-stakeholder digital evidence governance.

That novelty comes from evidence quality, public-network realism, adversarial testing, scale analysis, and cross-domain framing, not from overstating unimplemented architectural changes.