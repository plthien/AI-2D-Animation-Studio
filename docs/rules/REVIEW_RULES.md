# REVIEW RULES — Mandatory Codex self-review and PR release policy

## At the end of every PR

1. Map each requirement in `MASTER_SPEC.md` phase and Appendix A to changed path(s), schema(s), test(s) and evidence. No omitted requirement.
2. Run type checks, unit tests, integration tests, contract checks and applicable browser/runtime checks; capture exact commands/outputs.
3. Independently audit incorrect dependencies, prohibited prototype/Genielabs content, background LLM calls, static-image fallback paths and copied obsolete YTB migrations.
4. Audit error recovery, timeout/cancel, resource limits, credential redaction, state fencing, concurrency and project cross-talk.
5. Audit semantic constraints beyond JSON shape: story-to-action mapping, rig capability and Spine load, actor/prop world position, action half-open interval, voice sample timings and final frame manifest.
6. Fix review findings and rerun the affected test(s). Do not mark complete with defects classified critical/high or blocked acceptance proof.
7. Write `docs/qa/PHASE_Pxx_REVIEW.md`: requirement traceability, diff scope, evidence, unexpected changes, performance/cost, pass/fail and remaining risks.
8. Open PR with **phase only**, base current approved branch, no auto merge. A Draft PR or red/missing required CI is **not a passed phase**.

## Review-grade defect categories

- **BLOCKER:** banned code/API path, wrong repository/phase, schema violation, old DB migration, fake success, incorrect or missing actual Spine render, paid ambiguous retry, no 48k audio, cross-project data leak.
- **HIGH:** missing end-to-end proof for phase, IK/prop discontinuity, unapproved asset publish, nonrepeatable render, resource leak or cancellation bug.
- **MEDIUM:** missing noncritical UI affordance or optional optimization. Document; never hide.

## Hand-off report format

Include `base_sha`, `head_sha`, `phase`, `upstream_sha`, changed file list, exact test commands, observed counts, screenshots/video artifacts, blocked gates, explicit non-goals and next recommended phase. Claim PASS only for execution you actually observed.


## Additional self-review proof: animation-first

Inspect `channel_dna.v2` cross-field and effective animation preset tests, verify that visual hash is not recomputed from performance-only edits, inspect actual rig bone name validation and official Spine 4.2 matched runtime, and verify per-voiced-shot cue completeness with silent-shot sample insertion. Note any YTB V3 fields that were deliberately not ported. `docs/audits/ANIMATION_CONTRACT_AUDIT_v1_2.md` is review scope, not a substitute for running tests.

## Implementation-plan authority (v1.3)

Every PR P0–P11 must implement the corresponding `docs/implementation/Pxx_*.md`, report task-by-task proofs in phase QA, and execute `tools/validate_implementation_pack.py` plus `tools/test_cross_phase_contracts.py`. Master Spec §20 controls canonical voice final-extension limits (768 final frames/shot, 23040 final frames maximum); raw voice length in P8 is not the final scheduling authority. Contract collisions are blockers, not choices left to agents.
