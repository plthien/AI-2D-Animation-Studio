# P7 — Deterministic multi-shot Spine/PixiJS renderer
**Prerequisite:** P4 real rig loader and P5 numerical motion plus P6 approved action plan. **Owning skills:** `spine-renderer`,`motion-engine`. **Contracts:** `compiled_film.v1`,`frame_sequence_manifest.v1`,`rig_profile.v1`.

## Work orders

**P7.01 Node runtime.** Create `runtime/package.json`, lockfile, `runtime/spine/{index.html,app.ts,load_assets.ts,frame_evaluator.ts,scene_renderer.ts,coordinate.ts}`. Pin exact compatible `pixi.js@8.x` (>=8.16), `@esotericsoftware/spine-pixi-v8@4.2.x`, Playwright/Chromium version; do not use `latest`. Spine 4.2 JSON and runtime major/minor must match. `load_assets` loads approved files by SHA/manifest through project-scoped signed local URLs; no direct disk path supplied by LLM.

**P7.02 Render bridge.** `app/modules/production/{spine_render_driver,frame_export}.py`, `app/api/routes/render.py` P7 preview routes, `src/features/animation/MotionPreview.tsx`, `tests/render/*`. Python P5 compiles **all** per-frame bones/camera/prop snapshots into `compiled_film`; JS does not solve IK or incrementally simulate actions. Renderer provides `renderFrame(shotId,localFrameIndex)` by setting setup state/reset all bones/slots/attachments and applying exact source snapshot. No wall-clock `deltaTime` or accumulated Pixi ticker.

**P7.03 Coordinate conversion.** World (meters x-right/y-up); `screen_x=640+(world_x-camera.x)*100*zoom`, `screen_y=360-(world_y-camera.y)*100*zoom`. Rig rest pixels are local, converted to meters via approved RigProfile size; apply actor world root once, then snapshot local bones, then camera once. Background fills frame at catalog version, prop independent sprite follows actual world transform. Verify rotated hand socket result against compiled prop center within 0.003m.

**P7.04 Per-shot output.** Each render attempt has uniquely generated `{artifact_root}/{project}/attempts/{operation_id}/shot_{id}/` and no shared `runtime/fixtures`; isolated loopback port assigned atomically/OS free bind per operation. `FrameExporter.render_shot(compiled_shot,context)->frame_sequence_manifest.v1`: for frames `0..N-1` save `frame_%06d.png`, 1280x720 RGBA PNG, SHA256 per file, exact count, first/middle/last nonblank check. Re-seek in arbitrary order must regenerate equal bytes/shader snapshots on same pinned runtime; where GPU raster nondeterminism prevents byte equality, run determinism on actor/world transforms and repeat browser with controlled software renderer and report platform-specific image differences (never claim identical hash falsely).

**P7.05 Continuity and preview.** `src/features/animation/MotionPreview.tsx`: real play/pause, seek to any frame, camera view, skeleton overlay and owned prop label. Compile P5 across shots with explicit WorldState carried, including actor offscreen state; ordinary cut can change camera, not ownership/position without declared legal change. No story ID branches. `POST /projects/{id}/motion/compile`, `GET /projects/{id}/motion/preview/{shot_id}`, `POST /projects/{id}/render/previews` return operation IDs and validated output, no fake MP4 yet.

## Tests and gate

Actual Chromium test not optional: two actors sharing same rig use distinct instances; different rigs; 3 props; 7 consecutive shots; atlas missing region fails; wrong runtime bone name fails; 1st/mid/last nonblank; isolated simultaneous projects do not cross-contaminate, camera moves affect screen only; `frame_at(20)` identical after seeking 0→20→3→20; screenshots inspect joints/hand sockets and seams. ffprobe not required until P9. Pure backend unit PASS is **not** sufficient for P7 approval. **Exit:** real frame sequence of full-body animated actors and props for multi-shot preview.

## Mandatory phase protocol

1. Start from the latest approved `main`; never read, merge or copy from `feat/p0-p1-foundation` or PR #1. Freeze upstream `ytb-ai-studio` at `393d0eb5516ac8bb8455f859b79bfc64388b128e`. Record every reused function/file and source SHA in `docs/UPSTREAM_PORT_MANIFEST.md`.
2. Read root `AGENTS.md`, the five `docs/rules/*.md`, `MASTER_SPEC.md` including §19 and Appendix A–H, `docs/contracts/ANIMATION_CONTRACT_SEMANTICS.md`, the relevant `.agents/skills/*/SKILL.md`, and the schema+example named in this phase. **Do not** invent fields, API routes, behaviors or defaults.
3. Before editing execute `python tools/validate_contract_pack.py`, `python tools/test_animation_contract_semantics.py`, `python tools/validate_agent_pack.py`, `python tools/validate_implementation_pack.py`. All must pass. Re-run afterwards. Each `validate` route is read-only: it must not update database artifacts, reservations or files.
4. Implement one phase per feature branch/PR; do not merge or auto-start the next phase. APIs for later phases may respond `{error:{code:"NOT_IMPLEMENTED",...}}` only where this phase's explicit integration shell requires a stub; never return mocked success.
5. Publish only immutable validated artifacts with input provenance and compare-and-set stage heads. All external/paid IO is outside SQLite write transactions. Treat all imported JSON, images, paths and provider payloads as untrusted.
6. Run exact phase tests, perform a manual visual gate when required, and record evidence in `docs/qa/PHASE_Pxx_REVIEW.md`. Status values must distinguish `PASS`, `FAIL`, `NOT_RUN`, `BLOCKED`; mock-only or fixture-only tests cannot be called live-provider or production acceptance.

## Shared implementation invariants

- Windows 10/11 x64 local-first, Python 3.12, Node 22, 24 FPS, 1280x720, 48 kHz mono 16-bit PCM = 2000 samples per frame, 1–2 humanoid actors/shot, up to 3 props, <=30 shots, 24..720 frames/shot, world coordinates (x-right,y-up) in meters.
- ChannelDNA `channel_dna.v2`; `visual_style_hash` controls image/rig reuse; `performance_style_hash` controls Director/Motion; `narration_identity_hash` controls authoring/voice. No implicit conversion of creative prose into runtime actions.
- `rig_manifest.v1` is the final rig artifact; 16 required semantic roles, but approved runtime bones can be 16..64 by `rig_profile.runtime_bone_names` exactly. Any unexpected/missing bone is `RIG_BONE_SET_MISMATCH`.
- Rigged animation must be actual Spine 4.2 + compatible Spine-Pixi v8 / PixiJS 8.16+, using exact lockfile versions; not still-image Ken Burns and not Genielabs code. No hidden LLM APIs.
- IDs are backend-reserved; JSON/DB/OpenAPI/TS contract must stay synchronized. Use the error envelope `{"error":{"code":...,"message":...,"retryable":false,"details":{"path":...,"recovery":...}}}`; do not replace unsupported actions with idle.
