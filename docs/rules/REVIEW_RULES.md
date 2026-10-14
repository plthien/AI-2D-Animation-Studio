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
