# Before/After Sequence Note

## ClaimGuard conference sequence

1. Client authenticates to the gateway.
2. Gateway maps the identity to a blockchain subject.
3. Gateway calls on-chain `checkAccess`.
4. If allowed, the gateway issues a short-lived capability.
5. Storage validates the capability and serves the evidence.

## PACE journal sequence

1. Client authenticates to the gateway.
2. Gateway maps the identity to a blockchain subject.
3. Gateway calls the same on-chain `checkAccess` path.
4. If allowed, the gateway issues a short-lived capability.
5. Storage validates the capability and serves the evidence.
6. The surrounding evaluation package now includes baseline comparison, public-network validation, adversarial testing, policy-churn analysis, and bounded edge-ingest profiling around that same path.

## Meaning of the delta

The runtime authorization sequence remains intentionally stable across conference and journal versions. The journal delta is therefore best understood as:

- broader empirical validation around the existing sequence,
- stronger framing of domain-neutral applicability, and
- clearer separation between measured behavior and future architectural extensions.

## Explicit future sequence extensions

If the next revision implements the planned deltas, the sequence would change in three places:

1. A PEG-side emergency deny overlay would run before the on-chain allow path.
2. Audit persistence could move off the synchronous decision path into an async queue or batch anchor stage.
3. The contract decision path could replace linear scan evaluation with indexed candidate selection before full rule matching.

Those sequence changes are documented for planning only and are not presented as current implementation behavior.