# Contract ↔ Phase cross-audit — v1.3

**Scope:** all 19 normative schema/example pairs, the Master Spec, ChannelDNA v2, 12 phase plans, nine agent Skills and five Rules. This is a **documentation/contract audit**; no app/Spine/G-Labs/Windows code or real media was run.

## Resolved blocking inconsistencies

| Contract boundary | Previously ambiguous/conflicting | Normative decision (schema or prose change) | Test |
|---|---|---|---|
| P8 VoiceManifest → P9 Timeline | Raw WAV overrun rejected in §4.2 even when P9 could extend | P8 stores exact measured WAV; P9 can extend legal terminal hold <=48 frames; otherwise typed blocker | `test_cross_phase_contracts.py::test_overrun_policy` |
| CompiledFilm vs FinalTimeline | ShotPlan 720 max frames but final also max720 despite +48 hold | Compiled <=720; Final shot <=768, film <=23040; no changes to action event frames | `test_cross_phase_contracts.py::test_final_extension_bounds` |
| Voice `start_frame` coordinate | Original per-shot and absolute descriptions mixed | Manifest uses original-film **absolute** shot start; no delayed intra-shot offset in MVP | `test_cross_phase_contracts.py::test_voice_cue_absolute_offsets` |
| DB table count | Former summaries spoke of 12 or 13 tables | §3.2 enumerates exactly 14 physical tables | `validate_implementation_pack.py` |
| Asset requirement identity | "canonical three tuple plus channel" not serialistically precise | `req_+sha256(canonical_json([channel_id,kind,semantic_key,view]))[:16]`, visual hash is an eligibility input | P2 golden fixture once app implemented |
| API health | P0 example returned unwrapped shape | `GET /health → {data:{status:"ok",schema_version:"1"}}` per §12 | P0 API test once app implemented |
| Stage 4 rig identity | Previous nonexistent `rig_package.v1` | Only `rig_manifest.v1` exists; Runtime bones exactly match approved 16..64 list | Existing `test_animation_contract_semantics.py` |
| Narrated vs silent visual shots | Silence needed without fake voice | `shot_purpose` + zero-length span, voice cue subset voiced only | Existing semantic validator |
| Channel DNA vs asset reuse | Moving motion energy accidentally invalidated images | Independent visual/performance/narration SHA partitions | Existing semantic validator |
| Asset kind effect | Effect available in Registry but no generate path | Only `character/background/prop`; `effect` unsupported MVP | Schema negative case |

## Source-of-truth matrix

| Artifact | Producer | Consumer phase | Normative schema |
|---|---|---|---|
| ChannelDNA v2 | P0 platform | P1/P2/P3/P6/P8 | `channel_dna.schema.json` |
| Topic/Script/ShotPlan | P1 authoring | P2/P6/P8 | `topic_ideas`, `script`, `shot_plan` |
| AssetRequirements/Resolution | P2 asset | P3/P4/P6 | `asset_requirements`, `asset_resolution` |
| AssetVersion/GenerationRequest | P2/P3 | P4, P7 | `asset_version`, `generation_request` |
| Parts/Layout/Joints/RigProfile/RigManifest | P4 | P5/P6/P7 | `parts_manifest`, `rig_layout`, `rig_joints`, `rig_profile`, `rig_manifest` |
| AnimationPlan | P6 | P5 compiler invoked at P7 | `animation_plan` |
| CompiledFilm/FrameSequence | P7 | P8/P9 | `compiled_film`, `frame_sequence_manifest` |
| VoiceManifest | P8 | P9 | `voice_manifest` |
| FinalTimeline/QCReport | P9/P10 | P11 | `final_timeline`, `qc_report` |

## Remaining risks (explicitly NOT tested)

1. Runtime interop with official Spine 4.2 JSON + PixiJS 8: must test in real Chromium at P4/P7. JSON Schema cannot validate actual atlas pose/reconstruction or animation appeal.
2. Real G-Labs provider task acceptance/ambiguous submissions on Windows: P3 live gate is `NOT_RUN` until user credentials and cost approval.
3. Kinematics/constraint reachability and multi-actor physical contact: P5 numeric tests and P7 pixel review are mandatory.
4. Voice pacing/forced alignment and real WAV sample counts: P8 live voice test and P9 ffprobe must run.
5. Runtime license/distribution: P11 compliance gate; this audit is not a license opinion.
6. User-facing 12 plans specify engineering intent and test contracts, not a guarantee that future libraries or provider behavior will match the planned assumptions. Implementation must block and report mismatches.

**Exit:** contract bundle can be used to **begin P0** after all document validation scripts pass. No final app acceptance is claimed.
