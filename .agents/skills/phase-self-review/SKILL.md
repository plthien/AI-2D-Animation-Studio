---
name: phase-self-review
description: Mandatory audit, evidence collection and blocking-gate review for any AI 2D Studio implementation PR P0–P11.
---

# Skill — phase-self-review

## Required references

Read `docs/rules/REVIEW_RULES.md`, `TESTING_RULES.md`, `CODING_RULES.md`; `MASTER_SPEC.md` §14–§17 and Appendix E; actual phase tests.

## Procedure

1. List all normative requirements in phase and matching Appendix A, map each to committed code path, schema/API and running test.
2. Inspect git diff and inherited upstream files for banned prototype/Genielabs/static-image pipeline, unapproved LLM API, code duplication and unversioned data.
3. Run contract validation, tests and full build; use actual output and exact command/CI link, never estimates.
4. Break own change with malicious JSON/image, stale versions, concurrent/misordered tasks, cancellation/restart, media timeout, unsupported rig/action, sample/frame mismatch as appropriate.
5. Inspect visual screenshots when phase touches rig/motion/render. Distinguish structural schema proofs from rendered proof and paid live G-Labs provider truth.
6. Fix blocking findings, rerun, publish `docs/qa/PHASE_Pxx_REVIEW.md`, include remaining BLOCKED/NOT_RUN gates.
7. Open PR (never auto merge) with file provenance and traceability; stop at requested phase.

## Acceptance

PASS requires observed commands/tests and no BLOCKER/HIGH. Incomplete tests must be reported NOT_RUN, not guessed green.


## Mandatory animation-first v1.2 amendment

Audit against `docs/audits/ANIMATION_CONTRACT_AUDIT_v1_2.md`, inspect `docs/contracts/*`, run `tools/test_animation_contract_semantics.py`, and report unresolved license/real-render gates explicitly.
