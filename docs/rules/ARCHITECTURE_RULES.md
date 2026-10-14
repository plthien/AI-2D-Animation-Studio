# ARCHITECTURE RULES — Module authority and dependency boundaries

## Source of truth

`MASTER_SPEC.md` §1–§3 and §8–§11 define physical ownership and logic. This ruleset narrows agent execution, not the product schema.

## Layering

1. `app/core`: IDs, hashing, clock, errors, provider-neutral authoring parsing; must not import stage-specific service modules.
2. `app/db`/`app/repositories`: persistence, immutable artifact versions, CAS publication; must not execute G-Labs, Spine or FFmpeg I/O.
3. `app/modules/platform`: Channel/Project, external Idea and Script; may call core and repositories but cannot bind Spine render internals.
4. `app/modules/media`: only G-Labs transport, explicit paid operation lifecycle and asset materialization. Do not mix rig anatomy with transport.
5. `app/modules/assets`: global asset metadata, resolver, version, approvals; consumes published media results, not provider SDK types.
6. `app/modules/rigging`: segmentation, matching, pivots, bones, atlas, rigor and Spine 4.2 export; local, no AI remote calls.
7. `app/modules/animation`: deterministic Action DSL interpretation, gait, IK, grip, world and contact; consumes approved `RigProfile`, ShotPlan, and current performance-style hashes. Compiler owns immutable frame snapshots.
8. `app/modules/director`: external Director authoring, strict JSON validation and capability checks; no direct media generation. `app/modules/voice` owns TTS/alignment independently of Spine.
9. `runtime/spine`: browser rendering using official matching Spine 4.2/PixiJS 8 runtime; one shot renderer, no story conditional logic.
10. `app/modules/production`: shot frames, final timing/voice, FFmpeg and QC, requiring frozen upstream hashes.
11. `app/api`: validation and orchestration edges only. UI is a client, never the source of business state.

## Ownership and immutable contracts

- Each published artifact has exactly one owning module/phase and one approval authority. Consumers take immutable IDs + content hashes, not mutable paths or loose filenames.
- UI may hold local drafts; only successful backend publication advances a stage. Re-author invalidates descendants (do not silently accept stale `animation_plan` or stale frames).
- Motion Library versions and RigProfile capability snapshots are linked by exact source identity. `animation_plan.v1` only expresses executable actions in capability snapshot; compiler rechecks.
- Scene graph and 2D world states are independent of camera projection. Camera operations never move actual world props.
- Render workers and browser asset staging are project-scoped, cleanup-safe; never share a writable fixture folder across concurrent jobs.

## Explicitly not ported

YTB's Scene Breakdown, BeatTimingMap, Scene Assets, image-per-Beat Prompt Bundle, Ken Burns video render graph, voice-first Scene Breakdown, old DB migrations and `/api/v4` routes. Do not transplant their tests or feature flags as runtime architecture.

## PR/module boundaries

Use Master Spec §14 and Appendix A for file-level phase deliverables. If work spans more than one authority, design interface + test in owning phase and defer implementation of dependent phase; no placeholder “complete” state. Avoid circular imports via typed DTOs.


## Animation-style/hash authority

ChannelDNA v2 owns textual and bounded style defaults. Assets consume the `visual_style_hash`; Director/Motion consume `performance_style_hash` and explicit per-shot performance snapshot; Voice consumes `narration_identity_hash`. Never invalidate approved G-Labs images solely for movement style changes, nor allow a new visual asset to bypass rig QA. Renderer consumes compiled frame snapshots and Spine 4.2 assets, not arbitrary ChannelDNA prose. Rig actual bone list must be checked against approved RigProfile before rendering.
