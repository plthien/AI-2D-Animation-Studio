# Full animation-first audit — 2026-10-14

**Target baseline:** `plthien/AI-2D-Animation-Studio` at repository commit `2fca1e1c6835a707a718608a5f09602aef865069`. **Authorized YTB baseline:** `plthien/ytb-ai-studio@393d0eb5516ac8bb8455f859b79bfc64388b128e`. This is a spec-only audit; none of these output artifacts are live generated yet.

## Every normative schema (19/19 inspected)

| Schema | Disposition | Justification / action |
|---|---|---|
| `channel_dna` | REPLACE_DOMAIN | YTB style/narration categories preserved conceptually; new v2 explicit acting/editorial/entity rules, separate hashes |
| `topic_ideas` | KEEP_ADAPTED | Keep external prompt/import/reservation and novelty; output compact and film feasibility guided in prompts |
| `script` | KEEP_ADAPTED | Narration-only Script with story intent; multi-speaker dialogue deferred, visual-only shots in ShotPlan |
| `shot_plan` | UPDATE | Required purpose, exact silent range and actor/prop continuity, no image-per-beat contract |
| `asset_requirements` | UPDATE | Only three producible asset kinds; derive required actions and visual style hash |
| `asset_resolution` | KEEP | Deterministic same-channel asset/rig binding; semantic capability checks in runtime |
| `asset_version` | UPDATE | Only character/background/prop; approved reference distinct from generated derivatives |
| `generation_request` | UPDATE | Reference ID required for character parts atlas/expression sheet; confirmed paid job |
| `parts_manifest` | UPDATE | Explicit immutable artifact IDs of reference and source atlas, in addition to SHA |
| `rig_layout` | KEEP | Per-part placement, reviewed draw order; semantic confidence rules enforced |
| `rig_joints` | KEEP | 14 required joint anchors and human review, verified against rest pose |
| `rig_profile` | KEEP_ADAPTED | 16 semantic roles mandatory; supporting additional native Spine control bones |
| `rig_manifest` | CLARIFY | Sole rig terminal artifact name, remove phantom rig_package name |
| `animation_plan` | UPDATE | Typed bounded executable performance per shot from ChannelDNA, 9 action DSL |
| `compiled_film` | UPDATE | Actual approved bone set not hard-coded count 16; 16..64 permitted |
| `frame_sequence_manifest` | KEEP | Deterministic PNG frames and hashes, no Ken Burns |
| `voice_manifest` | CLARIFY | Cues only for voiced shots; exact silence injected for visual-only shots |
| `final_timeline` | KEEP_ADAPTED | Voice-last exact 48k frame samples, not voice-first beat timing |
| `qc_report` | KEEP_ADAPTED | Real provider/manual visual gates not optional for production status |

## YTB source reuse boundary

- **Transplant neutral infrastructure only:** strict JSON parser and schema bundling; immutable artifact IDs/versioning and CAS publication; SQLite jobs/leases; G-Labs provider transport; Kokoro/ElevenLabs provider controls and audio validation; FFmpeg processes/probe; React Cockpit shell and prompt import workspace. Adapt API imports to the new project DB and schema.
- **Retain concepts, not schema payloads:** ChannelDNA (YTB v3 is string-array identity with pacing sections; animation v2 is typed acting identity), project metadata, narrator pacing; external prompt/import mechanics.
- **Reject static production semantics:** image-per-Beat visual plan, BeatTimingMap, Scene Asset Manifest, Ken Burns crop graph, legacy V3 DB migrations and Voice-first Scene Breakdown. Reusing those payloads would create invalid animation authority.
- **New animation-only domain:** actor identity across shots, semantic action DSL, rig/profile/manifests, asset capability resolver, world state, IK/gait, shot-scope render frame snapshots, voice-last shot windows, QC.

## High-risk holes resolved in this revision

1. `channel_dna.v1` did not include content/acting/editorial/EntityStyle identities → replace with `channel_dna.v2` and meaningful channel-neutral example.
2. All seven visual style fields contained a repeated placeholder string → replace with precise cutout-art direction.
3. `effect` asset in enum/DB despite absent media or render workflow → exclude entirely from MVP.
4. Source reference + parts atlas linked only by SHA → add both artifact IDs with immutable lineage.
5. AnimationPlan lacked executable channel acting profile → require shot performance, enforce approved DNA match.
6. CompiledFilm exactly 16 bones excluded auxiliary control bones → allow 16..64, semantic match to approved rig.
7. Master Spec named nonexistent `rig_package.v1` → corrected to `rig_manifest.v1`.
8. Silent visual beats were prohibited by ShotPlan minLength=1 and Voice wording → exact empty narration range, no TTS cue, digital silence insertion.
9. Architecture rules claimed modules `motion/` owned IK and `animation/` owned Director, contrary to actual file tree → aligned to `animation/` and `director/` respectively.
10. Previous first Codex prompt checked out an obsolete initial blank main SHA → changed to latest approved main.

## Deferred capabilities (not silently enabled)

Character dialogue, phoneme lip sync, rig view changes mid-action, airborne jumps/combat, procedural secondary physics, standalone visual `effect` assets, unbounded arbitrary LLM-generated actions, and scene-specific special-case animation. Request explicit versioned change and new real rendered tests before adding any of these.

## Research anchors

- Official Spine-Pixi v8 https://en.esotericsoftware.com/spine-pixi (PixiJS >=8.16, Spine runtime major.minor data match, WebGL/WebGPU).
- Official Spine JSON export format https://esotericsoftware.com/spine-json-format (bone hierarchy, slots, skins, attachments).
- Spine Runtime integration/license https://github.com/EsotericSoftware/spine-runtimes and https://esotericsoftware.com/spine-editor-license (verify rights and distribution terms for product; license gate P4/P11).

## Verification gates

Structural: `python tools/validate_contract_pack.py`; positive+negative boundary fixtures: `python tools/test_animation_contract_semantics.py`; agent/rule references: `python tools/validate_agent_pack.py`; manifest: `python tools/verify_package_manifest.py`. These never claim a real 2D motion render has already been tested.
