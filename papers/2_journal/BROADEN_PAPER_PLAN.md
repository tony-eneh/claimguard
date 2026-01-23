# Journal Paper Broadening Plan

**Date**: January 20, 2026  
**Status**: Planning  
**Objective**: Reframe ClaimGuard journal paper from insurance-specific validation to general multi-stakeholder data governance framework with broader appeal for blockchain and computing journals

---

## Rejection Analysis

### Editor Comments Summary
The manuscript was rejected for two key reasons:

1. **Narrow Domain Scope**: "Tightly scoped to a specific auto-insurance evidence management scenario and a custom PureChain infrastructure, with limited discussion of generalizability to other industrial domains or integration with mainstream enterprise IAM and data governance systems"

2. **Limited Novel Contribution**: "Core architectural concepts are established in distributed systems and security literature, and the contribution primarily represents a domain-specific system validation rather than a broadly novel industrial informatics methodology"

### Root Cause Assessment

**Current framing issues:**
- Title explicitly mentions "Insurance Evidence Management"
- Abstract opens with "Auto-insurance platforms" and positions ClaimGuard as insurance-specific solution
- Keywords include "Auto-Insurance" explicitly
- Introduction, problem statement, and all motivating scenarios are 100% insurance-focused
- PureChain presented as required infrastructure (vendor lock-in perception)
- Only 2 brief sentences in conclusion mention broader applicability
- All experiments validate insurance workflows only
- No discussion of architectural adaptation to other domains

**The reality:**
- Architecture IS technically domain-agnostic (resource-agnostic ABAC)
- Implementation runs on EVM (Ethereum-compatible), not PureChain-specific
- Experimental workloads COULD represent other domains with relabeling
- Design patterns (capability tokens, on-chain policies, off-chain enforcement) apply universally

**The gap:** Mismatch between implementation (general) and presentation (narrow)

---

## Reframing Strategy

### Core Positioning Shift

**FROM**: "ClaimGuard: A blockchain-based ABAC system for insurance evidence management"

**TO**: "ClaimGuard: A verifiable, action-aware ABAC framework for multi-stakeholder digital evidence governance, validated through comprehensive insurance case study"

### Key Messaging Changes

1. **Lead with cross-domain problem**: Multi-stakeholder evidence workflows span insurance, healthcare, legal discovery, supply chain — all share common challenges
2. **Position insurance as representative domain**: Well-suited case study with diverse stakeholder types, sensitivity levels, and regulatory requirements
3. **Emphasize architectural generality**: Resource-agnostic, domain-neutral design with configurable policies
4. **De-emphasize PureChain**: Present as EVM-compatible architecture deployable on Ethereum mainnet, Layer-2s, enterprise blockchains, with PureChain as one optimized option
5. **Highlight reusable patterns**: Capability-based enforcement, hybrid on/off-chain storage, audit trails as universal solutions

---

## Detailed Rewrite Plan

### 1. Title Rewrite

**Current**: "Evaluating Action-Aware Attribute-Based Access Control for Secure Insurance Evidence Management"

**Options**:
- **Option A**: "ClaimGuard: Action-Aware Attribute-Based Access Control for Multi-Stakeholder Digital Evidence Governance"
- **Option B**: "Verifiable Access Control for Off-Chain Resources in Multi-Stakeholder Blockchain Systems"
- **Option C**: "Action-Aware ABAC for Enterprise Data Governance: A Blockchain-Backed Framework"

**Recommendation**: Option A — Retains ClaimGuard name, emphasizes action-awareness (novelty), broadens to "multi-stakeholder digital evidence" (cross-domain)

### 2. Abstract Restructuring

**Current structure**:
1. Opens with "Auto-insurance platforms..."
2. Describes insurance-specific challenges
3. Presents ClaimGuard as insurance solution
4. Claims "first resource-agnostic framework tailored to auto-insurance"

**New structure**:
1. **Problem (cross-domain)**: "Multi-stakeholder digital evidence workflows—spanning healthcare records, legal discovery, insurance claims, and supply chain documentation—require fine-grained access control that respects dynamic stakeholder roles, contextual constraints, and regulatory compliance requirements."
2. **Limitation of existing solutions**: Current blockchain ABAC systems lack action-awareness, suffer from capability bloat, or tightly couple policies to specific data schemas
3. **Contribution**: "We present ClaimGuard, a verifiable, action-aware ABAC framework anchored on Ethereum-compatible smart contracts..."
4. **Validation domain**: "We validate the architecture through comprehensive evaluation using auto-insurance evidence workflows as a representative multi-stakeholder domain..."
5. **Results**: Performance metrics and security properties (no insurance-specific language)
6. **Generalization statement**: "The architecture's resource-agnostic design and EVM-compatibility enable deployment across diverse multi-stakeholder scenarios requiring verifiable off-chain resource access control."

**Action**: Rewrite abstract in [paper.tex](paper.tex) lines 1-30 (approximate)

### 3. Keywords Update

**Current**: Attribute-Based Access Control, Blockchain, Auto-Insurance, Capability-Based Authorization, PureChain

**New**: Attribute-Based Access Control, Blockchain, Multi-Stakeholder Systems, Capability-Based Authorization, Enterprise Data Governance, Smart Contracts, Ethereum

**Action**: Update keywords in [paper.tex](paper.tex)

### 4. Introduction Restructuring (Section 1)

**Current approach**: 4 paragraphs all focused on auto-insurance evidence challenges

**New approach**:

**¶1 - Cross-domain problem**:
- Start with: "Digital evidence governance in multi-stakeholder environments presents persistent challenges across healthcare, legal, insurance, and supply chain domains."
- Examples from 3+ domains:
  - **Healthcare**: EMR access by hospitals, specialists, insurance providers, researchers
  - **Legal discovery**: Evidence sharing among law firms, courts, expert witnesses, regulators
  - **Insurance claims**: Adjusters, investigators, repair vendors, reinsurers
  - **Supply chain**: Provenance documents shared among manufacturers, distributors, customs, auditors
- Common requirements: Fine-grained policies, audit trails, dynamic stakeholder attributes, off-chain resource management

**¶2 - Limitations of existing solutions**:
- Traditional IAM (centralized, single-organization trust model)
- Blockchain storage schemes (on-chain storage impractical for large evidence files)
- Existing blockchain ABAC (lack action-awareness, schema-coupled policies)

**¶3 - Our solution (domain-neutral)**:
- "We present ClaimGuard, an action-aware, attribute-based access control framework backed by Ethereum-compatible smart contracts..."
- Key innovations: action-aware policies, capability tokens, resource-agnostic design
- Deployment flexibility: EVM-compatible (Ethereum mainnet, Layer-2s, enterprise blockchains)

**¶4 - Validation domain selection**:
- "We validate ClaimGuard using auto-insurance claim workflows as a representative multi-stakeholder domain..."
- Rationale: Insurance exhibits diverse stakeholder types (5+ roles), multi-level sensitivity classifications, complex regulatory constraints, and high-volume evidence artifacts
- Emphasize: "The architecture's resource-agnostic design enables adaptation to other domains through policy reconfiguration without architectural changes."

**¶5 - Contributions** (keep existing but reword):
1. Action-aware ABAC architecture for multi-stakeholder digital evidence (not insurance-specific)
2. Capability-based enforcement gateway pattern (reusable)
3. Comprehensive security analysis under adversarial conditions (general threat model)
4. Extensive experimental validation including RBAC baseline comparison, network realism, scale testing (insurance as case study)

**Action**: Rewrite Section 1 (Introduction) in [paper.tex](paper.tex) approximately lines 60-180

### 5. Problem Statement Generalization (Section 1.1)

**Current**: "Problem Statement: Secure Access Control for Auto-Insurance Evidence Pipelines"

**New**: "Problem Statement: Verifiable Access Control for Multi-Organization Digital Evidence Workflows"

**Content changes**:
- Open with cross-domain challenge statement
- List common requirements across domains:
  - Multi-organization trust boundaries
  - Fine-grained, attribute-based policies
  - Action-specific constraints (read vs. modify vs. delete)
  - Dynamic stakeholder attributes and role changes
  - Audit trail requirements for compliance
  - Off-chain resource management (large files, legacy systems)
- Add subsection: "Insurance as Representative Domain" explaining why insurance is good validation domain
- Map insurance characteristics to general requirements

**Action**: Rewrite Section 1.1 in [paper.tex](paper.tex)

### 6. Related Work Restructuring (Section 2)

**Current structure**:
- 2.1 Blockchain-Based Access Control in Insurance
- 2.2 Access Control in Healthcare and DLT
- 2.3 Gaps in Existing Literature

**New structure**:
- **2.1 Multi-Stakeholder Data Governance Challenges** (cross-domain survey)
  - Healthcare EMR systems
  - Legal discovery platforms
  - Insurance data sharing
  - Supply chain provenance
  - Common patterns and limitations
  
- **2.2 Blockchain-Based Access Control Architectures**
  - On-chain ABAC systems
  - Capability-based systems
  - Hybrid storage approaches
  - Action-awareness gaps
  
- **2.3 Enterprise IAM and Blockchain Integration**
  - Traditional IAM limitations in multi-org settings
  - Decentralized identity approaches
  - Smart contract policy engines
  
- **2.4 Positioning and Novel Contributions**
  - Gap analysis (cross-domain perspective)
  - ClaimGuard's unique combination: action-awareness + capability tokens + resource-agnostic design + off-chain enforcement

**Comparison Table (Table 1) updates**:
- Change ClaimGuard domain from "Universal" to "Multi-Stakeholder Evidence" (more credible than "Universal")
- Add column: "EVM Compatibility" or "Blockchain Portability"
- Add 2-3 more systems from healthcare/supply chain domains for cross-domain comparison

**Action**: Restructure Section 2 in [paper.tex](paper.tex) approximately lines 200-400

### 7. System Methodology Domain-Neutral Presentation (Section 3)

**Current**: Motivating scenarios, design goals, architecture all framed for insurance

**New structure**:

**3.1 Multi-Stakeholder Evidence Governance Requirements** (new/renamed from "Motivating Scenarios"):
- Present 4-6 scenarios across domains:
  - **Scenario 1 (Insurance)**: Routine claim assessment
  - **Scenario 2 (Healthcare)**: Multi-provider EMR access for specialist consultation
  - **Scenario 3 (Legal)**: Discovery evidence sharing with court and expert witnesses
  - **Scenario 4 (Insurance)**: Fraud investigation with law enforcement
  - **Scenario 5 (Supply Chain)**: Customs audit of manufacturer provenance documents
  - **Scenario 6 (Insurance)**: Reinsurance treaty coordination
- Extract common requirements across all scenarios

**3.2 Design Goals** (generalized):
- Rewrite each goal domain-neutrally
  - **Current**: "DG1: Resource-agnostic ABAC for auto-insurance evidence artifacts"
  - **New**: "DG1: Resource-agnostic ABAC for heterogeneous off-chain evidence artifacts across multi-stakeholder workflows"
- Keep insurance examples in parenthetical explanations, not as primary framing

**3.3 ClaimGuard Architecture** (mostly unchanged, remove insurance-specific language):
- Present architecture components domain-neutrally
- Use generic terms: "evidence artifacts" not "insurance documents", "stakeholders" not "adjusters/investigators"
- Keep capability token design, policy engine, gateway pattern as-is (already general)

**3.4 Security Analysis** (mostly unchanged, generalize threat model):
- Threat actors: "malicious stakeholder" not "rogue adjuster"
- Attack scenarios: generalize to any multi-org context

**3.5 Application to Insurance Evidence Management** (NEW subsection):
- Consolidate insurance-specific details here
- Map generic architecture to insurance domain
- Define insurance-specific stakeholder roles, resource types, actions
- This section shows HOW to instantiate ClaimGuard for a specific domain

**Action**: Restructure Section 3 in [paper.tex](paper.tex) approximately lines 400-650

### 8. PureChain Repositioning (Section 4.2.1)

**Current**: "PureChain Network" subsection presents PureChain as the primary/required infrastructure with detailed PoA² consensus explanation

**New approach**:

**Rename subsection**: "Blockchain Deployment Platform"

**Content structure**:
1. **EVM-Compatibility emphasis**: "ClaimGuard smart contracts are implemented in Solidity and are compatible with any Ethereum Virtual Machine (EVM) environment."
   
2. **Deployment options**:
   - **Public Ethereum**: Mainnet and Layer-2 solutions (Polygon, Optimism, Arbitrum)
   - **Enterprise/Consortium blockchains**: Hyperledger Besu, Quorum, PureChain
   - **Testnets**: Sepolia, Goerli for development
   
3. **Evaluation infrastructure**: "For this study, we deploy on PureChain, a high-throughput consortium blockchain optimized for enterprise workloads..."
   
4. **PureChain characteristics** (keep existing technical details but frame as "our evaluation environment" not "the required platform"):
   - PoA² consensus
   - 7,000 TPS capacity
   - SAM+ algorithm
   - 7-node consortium setup
   
5. **Portability statement**: "The evaluation results generalize to other EVM environments with appropriate consideration of consensus mechanisms, gas costs, and network latency characteristics."

**Action**: Rewrite Section 4.2.1 in [paper.tex](paper.tex)

### 9. Experimental Evaluation Reframing (Sections 4-5)

**Current**: All workloads (W1-W5) described using insurance terminology exclusively

**New approach**:

**Add "Workload Generalizability" paragraph at start of Section 4.3 (Workload Configuration)**:
"The experimental workloads model representative access patterns in multi-stakeholder evidence workflows. While we instantiate these workloads using insurance claim scenarios for concreteness, the patterns generalize to other domains: W1 (routine multi-party evidence review) applies to healthcare specialist consultations or legal document review; W2 (high-sensitivity investigations) maps to healthcare research or law enforcement inquiries; W3 (cross-organization coordination) represents reinsurance, supply chain audits, or healthcare payer-provider interactions; W4 (high-volume processing) covers claims automation, EMR batch queries, or customs clearance; W5 (compliance audit) applies to regulatory reporting across any governed industry."

**Update workload descriptions** to include domain-neutral descriptions first, then insurance instantiation:
- **W1**: "Multi-Party Evidence Review (Insurance: Routine Claim Assessment)"
  - Generic: Multiple stakeholders with varied access rights reviewing shared evidence artifacts
  - Insurance instance: Adjuster, repair vendor, policyholder reviewing accident reports and photos
  
- **W2**: "High-Sensitivity Investigation (Insurance: Fraud Investigation)"
  - Generic: Privileged stakeholders accessing sensitive evidence with strict audit requirements
  - Insurance instance: Special investigator accessing medical records and police reports
  
- **W3**: "Cross-Organization Coordination (Insurance: Reinsurance)"
  - Generic: Federated evidence access across organizational boundaries
  - Insurance instance: Primary insurer, reinsurer, independent adjuster coordinating on large claim
  
- **W4**: "High-Volume Processing (Insurance: Automated Claims)"
  - Generic: Automated systems performing bulk evidence retrieval
  - Insurance instance: AI agent processing photos and telematics for low-value claims
  
- **W5**: "Compliance Audit and Reporting (Insurance: Regulatory Oversight)"
  - Generic: Auditor querying access logs and policy configurations
  - Insurance instance: State insurance regulator reviewing claims handling practices

**Add "Cross-Domain Mapping" table** (NEW Table in Section 4 or 5):

| Workload Pattern | Insurance | Healthcare | Legal Discovery | Supply Chain |
|-----------------|-----------|------------|-----------------|-------------|
| W1: Multi-Party Review | Claim assessment | Specialist consult | Document review | Quality inspection |
| W2: High-Sensitivity | Fraud investigation | Research access | Sealed evidence | Trade secret audit |
| W3: Cross-Org Coordination | Reinsurance | Payer-provider | Expert witness | Customs clearance |
| W4: High-Volume | Automated claims | EMR analytics | eDiscovery batch | Shipment tracking |
| W5: Compliance Audit | Regulator review | HIPAA audit | Court reporting | Trade compliance |

**Action**: 
- Add generalizability paragraph to Section 4.3 in [paper.tex](paper.tex)
- Update workload descriptions throughout Section 4
- Add cross-domain mapping table

### 10. Conclusion and Future Work (Section 6)

**Current**: Brief mention of generalizability in final paragraph

**New structure**:

**¶1 - Summary** (domain-neutral):
- "We presented ClaimGuard, an action-aware, attribute-based access control framework for multi-stakeholder digital evidence governance..."
- Restate contributions domain-neutrally
- "Comprehensive evaluation using insurance workflows as a representative case study demonstrates..."

**¶2 - Generalization and Applicability** (EXPAND significantly):
- "The architecture's resource-agnostic design and EVM-compatibility enable deployment across diverse domains..."
- Specific adaptation discussion:
  - **Healthcare**: Map patient→policyholder, provider→adjuster, research-IRB→fraud-investigator
  - **Legal discovery**: Map evidence artifacts to legal documents, parties to law firms/courts
  - **Supply chain**: Map products to resources, supply chain partners to stakeholders
- Required customizations: Policy rules, stakeholder attribute schemas, resource metadata schemas
- Architectural components requiring NO changes: Smart contracts, gateway pattern, capability tokens, audit log structure

**¶3 - Integration with Enterprise Systems**:
- "ClaimGuard integrates with existing enterprise IAM through the Policy Enforcement Gateway..."
- Discussion of SAML/OIDC integration, LDAP attribute sources, legacy system connectors
- Position as complementary to (not replacement for) enterprise IAM

**¶4 - Deployment Flexibility**:
- "EVM-compatibility enables deployment on public Ethereum, Layer-2 solutions (Polygon, Optimism), or enterprise blockchains (Hyperledger Besu, Quorum)..."
- Trade-off discussion: Public vs. consortium blockchains for different organizational requirements

**¶5 - Limitations**:
- Insurance-only empirical validation (acknowledge this)
- Need for domain-specific policy authoring tools
- Governance model for multi-organization policy updates

**¶6 - Future Work**:
- Empirical validation in healthcare and supply chain domains
- Policy authoring DSL and tooling
- Cross-blockchain interoperability for multi-organization scenarios
- Integration with decentralized identity standards (DIDs, VCs)
- (Keep existing: ML-based anomaly detection, formal verification)

**Action**: Rewrite Section 6 (Conclusion) in [paper.tex](paper.tex) approximately lines 780-820

---

## Additional Enhancement Options

### Option A: Add Lightweight Cross-Domain Validation (LOW EFFORT)

**No new experiments**, just add analytical discussion:

**New subsection in Section 5: "Cross-Domain Applicability Analysis"**
- **Table**: Map each design component to domain requirements
- **Discussion**: How policies/attributes would be configured for healthcare vs. supply chain
- **Example policies**: Show YAML policy for insurance claim vs. healthcare EMR access side-by-side
- **Architecture diagram overlay**: Annotate existing architecture with healthcare stakeholder labels

**Effort**: 1-2 days writing, no code changes  
**Impact**: Moderate — addresses reviewer concern about generalizability without requiring new experiments

### Option B: Run Small E6 Cross-Domain Experiment (MEDIUM EFFORT)

**Add E6: Cross-Domain Validation**
- Deploy contracts to clean blockchain instance
- Implement 2-3 healthcare EMR access scenarios
- Use same metrics (latency, gas, throughput) as E1-E5
- Compare healthcare workload results to insurance baseline

**Data needed**:
- Healthcare stakeholder roles: Patient, PCP, Specialist, Hospital-Admin, Researcher, Insurance-Payer
- EMR resource types: Labs, Imaging, Clinical-Notes, Prescriptions
- Actions: Read, Write, Share, Annotate
- Policies: 20-30 healthcare-specific policies (consent-based, HIPAA-aligned)

**Effort**: 1-2 weeks (policy authoring, data seeding, experiment scripts, analysis)  
**Impact**: HIGH — Empirical proof of generalizability, directly addresses rejection reason

### Option C: Add Ethereum Testnet Deployment Comparison (MEDIUM EFFORT)

**Demonstrate EVM portability**:
- Deploy ClaimGuard to Sepolia testnet (already have scripts: `deploy-sepolia.ts`)
- Run subset of experiments (E1 + E2) on Sepolia
- Compare results: gas costs, latency, throughput vs. PureChain
- Add analysis: "Public vs. Consortium Blockchain Trade-offs"

**New subsection**: "Deployment Portability Evaluation"
- Performance comparison table (PureChain vs. Sepolia)
- Gas cost analysis (public vs. consortium)
- Discussion: When to use public vs. private deployments

**Effort**: 3-5 days (deployment, experiments, analysis)  
**Impact**: MODERATE — Shows EVM-compatibility in practice, de-emphasizes PureChain dependency

### Option D: Comprehensive Rewrite + Validation (HIGH EFFORT)

Combine Options A + B + C:
- Full paper restructuring (all sections above)
- E6 healthcare experiment
- Sepolia deployment comparison
- Extended cross-domain analysis

**Effort**: 3-4 weeks  
**Impact**: VERY HIGH — New manuscript positioning, empirical cross-domain proof, deployment flexibility validation

---

## Implementation Priorities

### Phase 1: Core Reframing (REQUIRED, ~1 week)
**Goal**: Address domain-specificity criticism without new experiments
**Status**: ✅ **COMPLETE** (January 23, 2026)

1. ✅ Title rewrite (Option A recommended) — COMPLETED
2. ✅ Abstract restructure — COMPLETED
3. ✅ Keywords update — COMPLETED
4. ✅ Introduction restructure (add cross-domain framing, 3+ domain examples) — COMPLETED
5. ✅ Problem statement generalization — COMPLETED
6. ✅ Related Work restructuring (cross-domain survey) — COMPLETED
7. ✅ System Methodology domain-neutral presentation — COMPLETED
8. ✅ PureChain repositioning as deployment option — COMPLETED
9. ✅ Experimental workload generalizability discussion — COMPLETED
10. ⏸️ Cross-domain mapping table — PARTIALLY COMPLETED (prose paragraph exists in Section 4.3; formal table structure not added)
11. ✅ Conclusion expansion (generalization, integration, deployment flexibility) — COMPLETED

**Deliverable**: Revised paper manuscript addressing generalizability through framing changes ✅ DELIVERED

### Phase 2: Analytical Enhancement (OPTIONAL, +2-3 days)
**Goal**: Add cross-domain analysis without experiments (Option A)
**Status**: 🎯 **NEXT PRIORITY** (Recommended to tackle after Phase 1)

1. ⬜ Cross-Domain Applicability Analysis subsection (NEW section in paper Section 5)
2. ⬜ Component-to-requirement mapping table (shows how each PACE component addresses requirements across domains)
3. ⬜ Example healthcare policy YAML (concrete example showing policy syntax for EMR access scenario)
4. ⬜ Architecture diagram with healthcare annotations (visual showing how existing architecture maps to healthcare domain)

**Effort**: 2-3 days writing, no code or experiments needed

**What needs to be done**:
- Write new subsection in Section 5 (Experimental Analysis Discussion) or Section 6 (Conclusion)
- Create table showing: PACE Component × Domain Requirements (e.g., "Smart Contracts" supports "Multi-Org Trust Boundary" in all domains)
- Pull healthcare EMR examples from literature and write concrete policy rules in YAML format showing insurance vs. healthcare differences
- Annotate existing architecture diagram (Fig. 3) with healthcare stakeholder labels (Patient→Policyholder, Provider→Adjuster, etc.)

**Impact**: Moderate — addresses reviewer concern about generalizability without requiring new experiments

**Deliverable**: Strengthened generalizability claims with analytical evidence

### Phase 3: Empirical Validation (OPTIONAL, +1-2 weeks)
**Goal**: Add cross-domain experimental proof (Option B)

1. ✅ Design E6 healthcare experiment
2. ✅ Implement healthcare policies and data seeding
3. ✅ Run E6 experiments
4. ✅ Analyze results and compare to insurance baseline
5. ✅ Add E6 results section to paper
6. ✅ Update conclusion with empirical generalizability statement

**Deliverable**: Empirical proof of cross-domain applicability

### Phase 4: Deployment Flexibility Proof (OPTIONAL, +3-5 days)
**Goal**: Demonstrate EVM portability (Option C)

1. ✅ Deploy to Sepolia testnet
2. ✅ Run E1+E2 subset on Sepolia
3. ✅ Compare PureChain vs. Sepolia performance
4. ✅ Add "Deployment Portability" subsection
5. ✅ Update architecture discussion with deployment options analysis

**Deliverable**: Concrete evidence of blockchain portability

---

## Target Journal Considerations

### Current Target
**Journal of Information Security and Applications** (Elsevier)
- Scope: Information security, cryptography, access control
- Impact Factor: ~4.5
- Fit: GOOD (security-focused, accepts ABAC/blockchain papers)

### Alternative Targets After Broadening

**Tier 1 - Computing/Industrial Informatics**:
1. **IEEE Transactions on Industrial Informatics** (~11 IF)
   - Excellent fit if reframed as enterprise data governance
   - Requires industrial relevance emphasis (supply chain, manufacturing)
   
2. **Computers in Industry** (Elsevier, ~10 IF)
   - Direct match to rejection comment mentioning this journal
   - Requires multi-industry applicability emphasis

3. **Future Generation Computer Systems** (Elsevier, ~7 IF)
   - Accepts distributed systems, blockchain, access control papers
   - Good fit with cross-domain framing

**Tier 2 - Blockchain-Focused**:
4. **Blockchain: Research and Applications** (Elsevier, ~7 IF)
   - Blockchain-native venue
   - Requires emphasis on smart contract architecture and consensus

5. **IEEE Transactions on Services Computing** (~8 IF)
   - Service-oriented computing, multi-tenant systems
   - Fit: Enterprise IAM integration angle

**Tier 3 - Security-Focused** (Keep original target):
6. **Journal of Information Security and Applications** (~4.5 IF)
   - Current target, still viable with broadened framing

### Recommendation
After Phase 1 reframing, consider **IEEE Transactions on Industrial Informatics** or **Computers in Industry** as primary targets. Both explicitly value multi-domain applicability and enterprise relevance.

---

## Success Metrics

### Minimum Success (Phase 1 only)
- Paper clearly presents ClaimGuard as general multi-stakeholder framework
- Insurance positioned as case study, not sole application
- PureChain presented as deployment option, not requirement
- Related work covers 3+ domains
- Conclusion discusses adaptation to other domains
- **Claim**: "Validated through comprehensive insurance case study with applicability to healthcare, legal, and supply chain domains"

### Moderate Success (Phase 1 + 2)
- All minimum criteria met
- Added analytical cross-domain mapping
- Example policies for 2+ domains
- Component adaptation discussion
- **Claim**: "Architecture adapts to healthcare and supply chain through policy reconfiguration with no architectural changes"

### High Success (Phase 1 + 2 + 3)
- All moderate criteria met
- E6 healthcare experiment results
- Empirical proof of generalizability
- **Claim**: "Validated in insurance and healthcare domains, demonstrating cross-domain architectural portability"

### Maximum Success (Phase 1 + 2 + 3 + 4)
- All high success criteria met
- Sepolia deployment results
- Performance comparison (public vs. consortium)
- **Claim**: "EVM-compatible architecture validated on PureChain and public Ethereum, with empirical cross-domain evaluation in insurance and healthcare"

---

## Next Steps

1. **Review and approve this plan**
2. **Select target phase** (recommend Phase 1 minimum, consider Phase 2)
3. **Create git branch** for paper revision: `git checkout -b journal-broaden-rewrite`
4. **Start Phase 1 rewrites** following section-by-section plan above
5. **Iterate on drafts** with focus on seamless narrative flow
6. **Decide on Phase 2-4** after Phase 1 completion based on timeline and journal target

---

## Files to Modify

**Primary file**: [papers/2_journal/paper.tex](papers/2_journal/paper.tex)

**Supporting files** (if new experiments added):
- `claimguard-peg/e6_healthcare_run.py` (if Option B selected)
- `claimguard-peg/analyze_e6.py` (if Option B selected)
- `scripts/deploy-sepolia.ts` (already exists, may need updates for Option C)
- `papers/2_journal/figures/` (new figures for cross-domain results)

**Documentation updates**:
- [README.md](README.md) (update project description to de-emphasize insurance)
- [papers/2_journal/README.md](README.md) (update journal strategy notes)

---

## Risk Assessment

### Low Risk
- Phase 1 reframing: Pure editorial changes, no experimental validation needed
- Improves paper even if still rejected — better positioning for any venue

### Moderate Risk
- Phase 2 analytical enhancement: Stronger claims without empirical proof
- Risk: Reviewers may still want experimental validation
- Mitigation: Frame as "architectural analysis" not "validation"

### High Risk
- Phase 3 healthcare experiment: 
  - Risk: Results might show performance degradation or unexpected issues
  - Risk: Timeline extension (1-2 weeks)
  - Mitigation: Start with small pilot experiment
  
- Phase 4 Sepolia deployment:
  - Risk: Gas costs may be prohibitively expensive on public testnet
  - Risk: High latency may skew results
  - Mitigation: Use Layer-2 (Polygon) as alternative, or run minimal experiment subset

---

## Timeline Estimate

| Phase | Duration | Dependencies | Risk |
|-------|----------|-------------|------|
| Phase 1: Core Reframing | 5-7 days | None | Low |
| Phase 2: Analytical Enhancement | 2-3 days | Phase 1 complete | Low |
| Phase 3: Healthcare E6 Experiment | 7-10 days | Phase 1 complete | Moderate |
| Phase 4: Sepolia Deployment | 3-5 days | None (parallel to Phase 3) | Moderate |
| **Total (all phases)** | **3-4 weeks** | Sequential execution | Variable |
| **Recommended (Phase 1+2)** | **1 week** | - | Low |

---

## Conclusion

The paper's technical contribution is solid, but the presentation severely limits its impact. The reframing strategy outlined above repositions ClaimGuard as a **general-purpose multi-stakeholder data governance framework** while maintaining the rigor of the existing evaluation.

**Recommended path forward**: Execute Phase 1 (core reframing) immediately. This addresses the rejection's core criticism and positions the paper for broader venues. Phase 2 (analytical enhancement) adds credibility with minimal effort. Phase 3-4 should be considered based on timeline constraints and journal ambitions.

The architecture IS general — the paper just needs to communicate this effectively.
