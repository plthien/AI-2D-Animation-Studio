---
name: external-authoring
description: Implement strict external ChatGPT/DeepSeek authoring and ID-reserved import for topic, script, shot plan and animation plan stages.
---

# Skill — external-authoring

## Required references

`MASTER_SPEC.md` §4, §5, §9 and §12, Appendices A P1/P6; `contracts/schemas/{topic_ideas,script,shot_plan,animation_plan}.schema.json`; `app/core/external_authoring.py` from allowed YTB subset.

## Procedure

1. Use prompt package with reserved Artifact IDs, immutable source hashes, schema bundle, frozen source context and explicit stage. Never call LLM APIs. UI copy / paste or upload only.
2. Validate unknown/duplicate fields/keys, maximum bytes, schema and per-stage semantic rules. Enforce exact narration substring source, distinct IDs, nonoverlap and complete ShotPlan coverage.
3. Validate project pointer freshness and reservation ownership at final import, not just validate-only call; publish via CAS transaction, then consume reservation. Validation-only endpoint has no mutations.
4. For Director include approved asset + rig capability snapshot; only action names in Master Spec §9.2, no placeholders for unknown behaviors. Force import errors with stable code/path.
5. Add tests for consumed/stale reservations, schema mismatch, snippet tampering, duplicate shot IDs, invalid action window, invalid rig capability and concurrent import.

## Output

Approved immutable `topic_ideas.v1`, `script.v1`, `shot_plan.v1` and, when P6 reached, `animation_plan.v1`. No direct asset generation in authoring phase.


## Mandatory animation-first v1.2 amendment

Use `channel_dna.v2` and separate channel identity hashes; Script is narration-only and ShotPlan has required `shot_purpose`. Empty narration is valid only for visual-only shots with `section_start=section_end`. Director shot performance must match approved ChannelDNA defaults, not prompt hallucinations.
