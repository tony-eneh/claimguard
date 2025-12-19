Below is a **concrete, execution-oriented plan** to take the journal paper from its current state to a **publishable journal submission**, clearly separating what is *missing*, what must be *extended beyond the conference*, and what must be *rewritten or strengthened*.

---

## 1. Experiments to Run (Journal-Only, Not in Conference)

### E1. Quantitative RBAC Baseline Comparison **(Mandatory)**

**Why:** This is the single biggest gap vs. a journal standard and was explicitly raised by reviewers.

**What to implement**

* Cloud-only RBAC deployment (e.g., S3/MinIO + IAM/RBAC table)
* Same workload generator, same subjects/resources
* No blockchain in decision path

**Metrics to collect**

* End-to-end latency (P50 / P90 / P99)
* Throughput vs concurrency
* False accepts / false rejects under policy changes
* Revocation latency

**Outputs**

* **Table:** Latency comparison (RBAC vs Hybrid-Audit vs ClaimGuard)
* **Figure:** Throughput vs concurrency (3 curves)
* **Table:** Authorization errors (FAR/FRR)

---

### E2. Real-World–Like Network Conditions **(Strongly Recommended)**

**Why:** Journal reviewers will question local single-host results.

**What to add**

* Inject artificial latency and packet loss (e.g., `tc netem`)
* Simulate WAN conditions (20–100 ms RTT)

**Metrics**

* Latency inflation factor
* Throughput degradation
* Stability under burst loads

**Outputs**

* **Figure:** Latency under LAN vs WAN
* **Discussion subsection** on deployment realism

---

### E3. Security Stress Experiments **(New)**

**Why:** Current security discussion is qualitative.

**Experiments**

* Gateway DoS (rate flooding)
* Token replay at scale
* Expired-token brute reuse
* Direct cloud access attempts

**Outputs**

* **Table:** Attack → Outcome → Mitigation
* **Quantified rejection rates**

---

### E4. Policy Churn & Scale Test **(Extend Existing)**

**Why:** Journals expect scale analysis.

**Extend**

* Increase policies to 100 / 1k
* Increase subjects to 500–1k
* Measure `checkAccess` gas + latency growth

**Outputs**

* **Figure:** Policy count vs evaluation latency
* **Table:** Gas growth trends

---

## 2. Charts & Tables to Generate (Journal Additions)

### New Figures

1. **Throughput comparison:** RBAC vs Hybrid-Audit vs ClaimGuard
2. **Latency distribution (CDF):** ClaimGuard vs RBAC
3. **Policy evaluation latency vs number of rules**
4. **Latency under network delay (LAN vs WAN)**

### New Tables

1. **Comprehensive latency table (3 systems)**
2. **Authorization correctness (FAR/FRR)**
3. **Attack resilience summary**
4. **Resource utilization at scale**

---

## 3. Sections That Must Be Rewritten or Expanded

### Section III – Problem Definition

* Explicitly formalize **RBAC failure cases**
* Add **threat taxonomy table** (insider, cloud admin, replay, DoS)

---

### Section IV – Architecture

**Rewrite needed**

* Explicitly explain **R3 (Cloud Insider Resistance)**:

  * Capability-bound access
  * Optional envelope encryption (DEK wrapped via gateway)
  * Why IPFS/S3 alone is insufficient

---

### Section V – Simulation → **Rename to “Experimental Evaluation”**

**Major rewrite**

* Split into:

  * Experimental Setup
  * Baselines
  * Metrics
  * Workloads
* Clearly distinguish **synthetic vs real-world approximation**

---

### Results Section

**Must expand**

* Add RBAC baseline results
* Quantify “negligible” false rejects
* Reference all new figures/tables explicitly

---

### Security Analysis Section **(New Dedicated Section)**

Add a standalone section:

* Gateway DoS
* Smart contract upgrade risk
* Key compromise
* Residual risks and assumptions

---

## 4. Methodological Improvements (Low Effort, High Impact)

* Add **confidence intervals** or std dev to latency results
* Clarify **hardware specs and OS tuning**
* Add **reproducibility appendix** or link to repo

---

## 5. What Stays Conference-Only (Do NOT Expand Further)

* ML-based risk scoring
* Anomaly detection models
* Cross-chain or Fabric integration
* Full real-world insurer dataset (can be future work)

These should remain **explicitly framed as future work**.

---

## 6. Recommended Execution Order (Practical Timeline)

**Week 1**

* Implement RBAC baseline
* Run latency + throughput comparisons

**Week 2**

* Network-delay experiments
* Security stress tests

**Week 3**

* Policy scale tests
* Generate all final plots/tables

**Week 4**

* Rewrite Sections IV–VI
* Add Security Analysis
* Final polish and journal formatting

---

## Bottom Line

To reach journal quality, the paper needs:

* **One strong baseline (RBAC)**
* **One realism upgrade (network + scale)**
* **One explicit security section**
* **Clear quantitative backing for all claims**

Once those are in, the paper is **well within publishable range** for a systems/security journal.
