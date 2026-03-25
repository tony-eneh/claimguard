# Consolidated Journal Critique Issues (Action Master List)

This document compiles and deduplicates highlighted concerns from:
- `claude_sonnet_4.6.md`
- `deepseek.md`
- `gemini_3_thinking.md`
- `grok_4.0_expert.md`
- `kimi_2.5_thinking.md`
- `perplexity.md`

## Priority 1 — Must Fix Before Submission

### 1) Resolve contradictory/ambiguous security result (Role Spoofing = 50% / PARTIAL)
**Issue:** Multiple critiques flag that reporting role spoofing as “PARTIAL (50%)” conflicts with claims like “attacks are blocked” and “zero false accepts/rejects.”

**Why it matters:** This is a credibility-critical contradiction in the core security narrative.

**Required actions:**
- Precisely define what “PARTIAL (50%)” means (e.g., malformed-input rejection path vs authorization bypass).
- Separate input-validation failures from authorization-logic outcomes.
- Recompute and report clean metrics: false accept, false reject, malformed-input reject, and attack-success rate.
- Update abstract, results, and conclusion language so claims exactly match data.

---

### 2) Reconcile numerical inconsistencies across experiments
**Issue:** Critiques identify inconsistent latency figures between sections/tables (especially local E1 vs local values referenced in E2 context).

**Why it matters:** Inconsistent numbers undermine trust in all experimental findings.

**Required actions:**
- Perform a full table/figure/prose consistency audit for every metric (P50/P95/P99, throughput, update latency, N, runs).
- Add one canonical “measurement settings” paragraph per experiment (workload, concurrency, hardware, repetitions).
- State explicitly when metrics are not directly comparable due to changed setup.

---

### 3) Tone down or qualify “production-ready” and “first” claims
**Issue:** Several critiques say “production-ready,” “first systematic comparison,” and broad universality claims are stronger than evidence supports.

**Why it matters:** Overclaiming is likely to trigger reviewer pushback even if the system is technically solid.

**Required actions:**
- Replace absolute claims with scoped wording (e.g., “production-oriented prototype,” “evaluated on local and public testnet settings”).
- Qualify novelty against prior ClaimGuard work with an explicit “what is new vs reused” list.
- Keep universality claims conditional unless empirically validated cross-domain.

---

### 4) Address incremental-contribution concern vs prior ClaimGuard
**Issue:** Human review explicitly flags that the main technical work may already have been done in ClaimGuard, making this journal version appear incremental.

**Why it matters:** If novelty is not crisply separated from prior work, reviewers may downgrade the contribution regardless of evaluation quality.

**Required actions:**
- Add a dedicated “Delta from ClaimGuard” subsection (intro or methodology) with a side-by-side comparison table.
- Enumerate concrete additions in this journal version (new threat model scope, new experiments E1–E4, new baselines, new metrics, new artifacts).
- Identify reused components honestly and explain why reuse is scientifically valid (continuity + controlled extension).
- Reframe contribution language from “new architecture” to “generalized and rigorously validated framework” unless architectural changes are demonstrably new.

---

### 5) Strengthen methodology transparency and rigor
**Issue:** Critiques question single-host Docker realism, low repeat counts in some experiments (e.g., policy updates), and ambiguous sample definitions.

**Why it matters:** Methodological opacity weakens acceptance chances more than moderate performance overhead does.

**Required actions:**
- Expand experiment setup details (node count, host specs, resource isolation, network shaping).
- Justify repetition counts and align across experiments where possible.
- Clarify all “N” definitions and confidence statistics.
- Add explicit threats-to-validity subsection if not already comprehensive.

---

### 6) Improve baseline fairness framing
**Issue:** Some critiques view Hybrid-Audit as potentially implementation-biased (e.g., synchronous logging design inflating latency).

**Why it matters:** If reviewers perceive unfair baselines, all comparative claims become suspect.

**Required actions:**
- Explicitly document baseline implementation choices and rationale.
- Add sensitivity note (or extra run) for asynchronous/batched audit logging to show effect size.
- Reframe claims to avoid implying universal dominance when architecture choices differ.

---

### 7) Address policy update delay risk on public networks
**Issue:** Sepolia policy update confirmation tail latency (up to ~90s) is repeatedly flagged as a practical security/operations risk.

**Why it matters:** Revocation/update delay is central in high-stakes incident response scenarios.

**Required actions:**
- Add explicit risk discussion for urgent revocation windows.
- Distinguish access-check latency vs policy-change finalization latency.
- Provide operational mitigations (e.g., staged emergency controls, consortium/L2 recommendations, temporary deny overlays).

## Priority 2 — Important Technical/Clarity Improvements

### 8) Clarify action enforcement semantics end-to-end
**Issue:** Critiques ask how action types (read/append/modify/delete/disclose) are enforced at storage/proxy layer.

**Required actions:**
- Add a concise enforcement flow for each action class.
- State whether gateway is mandatory proxy for write/delete paths.
- Clarify token claims-to-storage-operation mapping.

---

### 9) Tighten generalization claim (cross-domain evidence)
**Issue:** Cross-domain applicability is argued mostly by mapping/examples, with limited empirical replication beyond insurance.

**Required actions:**
- Reframe as “architecturally transferable, empirically demonstrated in insurance.”
- Move broad “universal” statements to conditional language.
- If no new experiments are added, clearly mark other domains as validated by configuration mapping, not measured performance.

---

### 10) Expand cost/scalability reporting
**Issue:** Critiques ask for fuller economics (especially beyond local gas snapshots) and larger-scale evidence.

**Required actions:**
- Add or expand cost table (policy operations + environment assumptions; include network context).
- Report any available RPC/operational overhead discussion for frequent access checks.
- Clarify current tested scale envelope and what remains untested.

---

### 11) Strengthen deployment realism discussion
**Issue:** Gateway availability/centrality, key management, and operational complexity are noted as residual risks.

**Required actions:**
- Add clear reliability model (gateway HA assumptions, failover posture).
- Clarify trust boundaries and what decentralization does and does not guarantee.
- Expand residual-risk section with concrete mitigations (HSM, rate limiting, circuit breakers, monitoring).

## Priority 3 — Presentation and Manuscript Quality

### 12) Reduce repetition and improve narrative flow
**Issue:** Multiple critiques mention dense/repetitive exposition and overlapping abstract/introduction content.

**Required actions:**
- Remove repeated architecture and claim language.
- Tighten intro-to-method-to-results progression.
- Keep cross-domain mappings concise; move long examples to appendix/supplement if needed.

---

### 13) Fix table/figure readability and formatting issues
**Issue:** Critiques flag truncated/unclear tables and small/blurry figures.

**Required actions:**
- Verify all table headers/captions are complete and consistent.
- Ensure figure resolution and legibility in final PDF.
- Confirm every figure/table reference is accurate and discussed in text.

---

### 14) Tighten terminology precision
**Issue:** “Honest-but-curious” vs “malicious cloud,” and broad security wording can blur threat model boundaries.

**Required actions:**
- Standardize threat-model terminology throughout.
- Avoid implying guarantees beyond defined assumptions.

## Suggested Revision Sequence
1. Fix contradictions and numeric consistency first (Items 1–2).
2. Resolve novelty/delta framing vs ClaimGuard (Item 4).
3. Re-scope claims and fairness framing (Items 3, 6, 9).
4. Strengthen methods and operational risk analysis (Items 5, 7, 8, 11).
5. Improve cost/scalability disclosure (Item 10).
6. Final polish on writing/format/figures (Items 12–14).

## Quick Win Checklist (if time is limited)
- [ ] Resolve role spoofing contradiction with explicit metric definitions.
- [ ] Run full number consistency pass (tables/figures/prose).
- [ ] Add a "Delta from ClaimGuard" table (new vs reused).
- [ ] Replace “production-ready/first/universal” with scoped claims.
- [ ] Add baseline fairness caveat + async logging sensitivity note.
- [ ] Add explicit Sepolia update-delay risk and mitigation text.
- [ ] Fix formatting/readability defects in tables/figures.
