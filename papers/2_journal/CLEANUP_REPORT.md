# Cleanup Report

File edited: `paper.tex`

Baseline commit created before edits:
- `c6d6119` — `chore(journal): baseline before manuscript cleanup`

## Changes made

1. **Removed obsolete commented-out alternate title block**
   - Removed original lines 62–63.

2. **Replaced manuscript date placeholders**
   - Updated `\thanks{...}` line at current line **66**.
   - Changed `Month XX, 2026` to `April 2026` for received, revised, and accepted dates.

3. **Cleaned `\markboth` journal header**
   - Updated header at current line **78**.
   - Changed `IEEE Transactions on Information Forensics and Security` to `IEEE Transactions`.

4. **Removed obsolete commented-out introduction paragraph**
   - Removed original line 96.

5. **Removed large stale commented-out security-analysis blocks**
   - Removed original lines **314–330** (old DoS/gateway discussion block).
   - Removed original lines **334–349** (old private-key management block).
   - Removed original lines **354–367** (old smart-contract upgrade-risk block).
   - Removed original lines **372–384** (old key-compromise/revocation block).

6. **Removed redundant commented-out reproducibility marker**
   - Removed original line 492.

7. **Removed stale commented-out comparison table block**
   - Removed original lines **533–553**.

8. **Clarified E3 role spoofing result in Table 5**
   - Updated table row at current line **570** to add `\footnotemark` to `Role Spoofing`.
   - Added explanatory footnote at current line **577**:
     - “The partial result for role spoofing reflects that malformed (non-checksummed) Ethereum addresses bypass client-side validation but are rejected at the contract level; no valid authorization bypass occurred across any test vector.”

9. **Clarified E3 role spoofing result in discussion paragraph**
   - Updated the security-discussion paragraph at current line **698** to explicitly state that malformed non-checksummed addresses were rejected at the contract level and that no valid authorization bypass occurred.

10. **Removed stale commented-out comparative-analysis draft block**
    - Removed original lines **997–999**.

11. **Strengthened and expanded the conclusion**
    - Rewrote the main conclusion paragraph beginning at current line **912**.
    - Added:
      - practical-significance claim that PACE is the first framework providing quantitative evidence that blockchain-backed ABAC is operationally viable for multi-stakeholder evidence governance;
      - open-source artifact availability statement;
      - broader compliance significance referencing the **EU AI Act** and **DORA**.

12. **Removed obsolete commented-out future-work and appendix draft blocks**
    - Removed original lines **1007–1020**.

## Remaining comments intentionally kept

- Current line **686**: `%\label{sec:discussion}`
  - Kept because it is a small single-line structural comment rather than a large commented-out draft block.

## Final commit

After edits:
- Final commit requested: `chore(journal): manuscript cleanup - remove commented blocks, fix placeholders, strengthen conclusion`
