## Critique of "PACE: Policy Anchor and Capability Enforcement for Multi-Stakeholder Digital Evidence Governance"

### Strengths

The paper addresses a genuine and important gap — binding on-chain authorization to off-chain storage across organizational boundaries — and the architecture is coherent. The four experimental dimensions (E1–E4) meaningfully expand on the prior conference version, and the adversarial test suite is a welcome addition often absent from systems papers. The cross-domain policy examples are concrete and useful.

---

### Significant Weaknesses

**1. Experimental Rigor is Shallow**

This is the most serious concern. The experiments are run on a single "commodity multi-core host" in Docker, which means all components — blockchain nodes, gateway, storage, and load generator — share resources. This fundamentally invalidates throughput and latency claims as representative of any real deployment. The authors report N=1000 for latency measurements but only N=10 for policy update benchmarks, with no justification for this asymmetry. Five repetitions for the core latency experiment is marginal for a systems paper claiming production readiness.

**2. The "Partial" Role Spoofing Result is Underexplained and Concerning**

Table VII reports only a 50% block rate for role spoofing, which the authors quickly attribute to "input-validation differences for malformed addresses." This explanation is inadequate. If an attacker submits a well-formed spoofed address with invalid credentials, the paper claims these were "consistently rejected" — but this is stated in prose rather than shown in the data. A 50% block rate in a security paper requires far more rigorous analysis, not reassuring hand-waving.

**3. The Hybrid-Audit Baseline is Poorly Designed**

The authors present the counterintuitive result that Hybrid-Audit (136 ms P50) is *slower* than PACE (61 ms P50), attributing it to "two sequential operations." This is an artifact of their implementation choice to make audit logging synchronous, which no real system would do. A properly implemented async audit baseline would likely show 2–5 ms latency, making PACE's overhead look considerably worse. The baseline is constructed in a way that flatters PACE.

**4. Security Analysis Overstates Guarantees**

The threat model claims resistance to "honest-but-curious cloud providers," but the capability token mechanism only works if cloud storage is correctly configured to reject requests lacking valid tokens. This is an operational assumption, not an architectural guarantee. In practice, misconfigurations of S3 bucket policies are extremely common and represent exactly the insider threat vector the paper claims to solve. This dependency on correct cloud-side configuration deserves explicit acknowledgment as a critical limitation rather than a footnote.

**5. The Sepolia Results are Misrepresented**

Policy update confirmation times on Sepolia average 24.8 seconds and reach 89.4 seconds. The authors frame this as acceptable because "policy changes are infrequent." However, in a multi-stakeholder environment — a legal case closure, a medical emergency requiring immediate access revocation, a fraud investigation — a 90-second window before a policy takes effect is a meaningful security vulnerability. The paper does not engage seriously with this attack surface.

**6. Cross-Domain Generalizability is Asserted, Not Demonstrated**

Section IV.P.7 is essentially theoretical. The authors acknowledge that "empirical validation of cross-domain generality would require E6 experiments" but then proceed to claim the architecture "applies universally." The JSON policy examples for healthcare and legal discovery are illustrative but untested. Claiming production readiness across four domains based on one tested domain is a significant overreach.

**7. Gas Cost Analysis is Incomplete**

The paper reports 128k gas for policy updates but acknowledges it "could not report a gas value for a view function" for `checkAccess`. Since `checkAccess` is called on every single access request, its gas cost (even if zero on-chain for a pure view call) and its RPC cost are critical to the economic feasibility argument. This gap is particularly notable given the paper's emphasis on production deployability.

---

### Minor Issues

- The comparison with Liu et al.'s 47/102 ms encryption costs is not apples-to-apples; encryption and access control evaluation serve different purposes.
- Resource utilization figures (18–35% CPU per node) are reported without specifying node count or hardware, making them uninterpretable.
- The PureChain results are mentioned in the setup section but essentially absent from the results, despite being listed as a deployment environment.
- The paper claims "zero false accepts or rejects" as a strength, but this is expected behavior for any correctly implemented access control system, not a differentiating result.

---

### Summary Assessment

PACE presents a architecturally sound and well-motivated system, and the writing is generally clear. However, the gap between its claims ("production-ready," "validated against real adversaries," applicable across four domains) and its evidence (single-machine Docker experiments, one domain tested, a partial security block rate left unexplained) is substantial. The paper would be considerably stronger if it either narrowed its claims to match the evidence or significantly expanded the experimental scope — particularly with distributed deployments, real cloud backends, and cross-domain policy validation.