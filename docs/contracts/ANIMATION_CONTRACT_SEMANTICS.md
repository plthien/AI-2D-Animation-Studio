# Cross-contract semantics — AI 2D Animation v1.2

`MASTER_SPEC.md` §19 is authoritative; this document is an implementation checklist for backend semantic validators in P0–P9. JSON Schema 2020-12 enforces shape only; **all cross-file invariants must be executable**. No production data exists yet, so no compatibility reader or migration for old draft schema versions is authorized.

## Dependency and authority chain

`channel_dna.v2` → `topic_ideas.v1` → `script.v1` → `shot_plan.v1` → `asset_requirements.v1` → `asset_resolution.v1` + approved asset images → `parts_manifest.v1` → `rig_layout.v1` → `rig_joints.v1` → `rig_profile.v1` + `rig_manifest.v1` → `animation_plan.v1` → `compiled_film.v1` → `frame_sequence_manifest.v1` → `voice_manifest.v1` → `final_timeline.v1` + `qc_report.v1`.

Every input artifact ID and SHA must be equal to the exact currently-approved dependency when publishing its immediate child. Unrelated historical artifact IDs can never satisfy an `approved` requirement.

## Validator decisions by schema

| Schema | Owner | Mandatory semantic validation (shape is not enough) |
|---|---|---|
| channel_dna | platform | channel IDs, render values, WPM min < max, hash partitions, unique/valid visual+acting rules |
| topic_ideas | authoring | same project, unique IDs, no selected duplicate topic, source snapshot current |
| script | authoring | exact concatenated narration from ordered sections, no inferred character dialogue in narrated MVP |
| shot_plan | authoring | order/IDs unique, exact quote windows, purpose and silence consistent, same actor/prop identity, location anchors, min one voiced shot per film |
| asset_requirements | assets | deterministic sorted unique keys, `required_actions` mapping from semantic story actions, style hash from approved visual fields |
| asset_resolution | assets | one decision per requirement, exact approved same-channel binding + compatible view/rig action support |
| asset_version | assets | verified PNG bytes/geometry/coordinate conventions; character reference distinguishes approved image from derivative atlas |
| generation_request | media | a paid request needs confirmation and backend credential; atlas/expression generation pins non-null approved source ref and channel lineage |
| parts_manifest | rigging | reference and atlas artifact IDs distinct; both SHA match exact downloaded images; masks nonempty, components separated, roles unique |
| rig_layout | rigging | one placement per approved part, legal transform and draw ordering, no detached sprite |
| rig_joints | rigging | 14 required pivot names and believable bone lengths, must align with approved layout/source ref |
| rig_profile | rigging | 16 semantic bone roles, 4 valid IK chains, finite matrices, named attachments for approved expressions, optional extra bones explicitly approved |
| rig_manifest | rigging | exact builder lineage/reference IDs and SHA, official runtime render QA, 5 pose visual review, immutable pinning |
| animation_plan | director | same approved actor/shot/rig/version, full allowed DSL, nonoverlap, source performance match, allowed contact events only |
| compiled_film | motion | contiguous frames; complete 16..64 unique approved `rig_profile.runtime_bone_names` each actor every frame; exact snapshots, prop ownership/location consistency |
| frame_sequence_manifest | renderer | exact N nonblank PNGs, size, hashes, local isolated frame path, deterministic random seek replay |
| voice_manifest | voice | one voiced cue per nonempty Shot narration and NO silent cue, verified PCM16 48kHz, precise sample alignment, no dialogue spoof |
| final_timeline | delivery | no cut/truncated speech, only safe hold extension, exact sum frames*2000 samples, immutable render and voice lineage |
| qc_report | QA | all gate statuses based on observed data; no `passed` when real G-Labs, real rig/voice or required manual review are NOT_RUN |

## Core invariants with precise examples

- Silent: shot with `narration_text=""`, `section_start=section_end`, `shot_purpose="visual_reaction"` or `"establishing"`. This is valid even when `story_actions` contains `look` or `react`. `story_action` must have voiced text. Split Script narration only with nonempty contiguous spans; empty windows do not consume text.
- Rig bone count: Spine may have more than 16 bones; `rig_profile.bone_roles` still requires all sixteen canonical names. On each rendered actor snapshot, bone name set equals the **required runtime bone set for that rig**, allowing 16..64. Reject missing or unknown bones. `minItems/maxItems` by themselves are not sufficient validation.
- Visual/performance partition: moving from medium to high motion energy changes `performance_style_hash`, NOT `visual_style_hash`; color change does the reverse. A downstream version's `source_hash` must include appropriate domain hashes.
- Voice-last: per-shot WAV for **voiced** shots only. Silent shots append digital zero samples for their full frame duration; do not invoke TTS for them. Align sample offsets to `start_frame * 2000` and verify exact full-track sample count.
- Expressions: `react(expression)` requires a real approved expression mapping and valid face slot attachment, not a label typed into a JSON file.
- Asset generation: `reference_image_artifact_id` non-null for `character_parts_atlas` and `expression_sheet`, always same pinned character lineage. No paid POST replay after uncertain acceptance.

## Blocking error codes (in addition to Master Spec)

`CHANNEL_DNA_VERSION_UNSUPPORTED`, `CHANNEL_DNA_STYLE_INVALID`, `SHOT_SILENCE_RANGE_INVALID`, `DIRECTOR_PERFORMANCE_SOURCE_MISMATCH`, `RIG_BONE_SET_MISMATCH`, `ASSET_ATLAS_SOURCE_MISMATCH`, `VOICE_CUE_SET_MISMATCH`, `ASSET_KIND_UNSUPPORTED`.

Each failure includes code, JSON field path, expected source ID/hash and recovery action. Validation-only APIs never mutate published artifacts. All errors fail closed; never repair imported creative JSON implicitly.
