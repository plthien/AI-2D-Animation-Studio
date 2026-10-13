# P5/P6 v2 — final engineering self-review (2026-10-14)

## Scope deliberately fixed by user

Complete P5 manual Director JSON + independent per-shot asset/motion compilation and P6 reusable renderer/video assembly. **Do not call G-Labs live or integrate Kokoro yet.** Accept existing WAV files and use artificial sine signals only to verify timestamp/mux correctness in CI.

## Delivered: actual implementation

- `studio/film_v2.py` introduces `film.v2` and an explicit `AssetCatalog`. Every shot identifies background, camera, actor IDs/rigs/motion clips, prop visuals and owning actor, duration in integer frames and optional narration WAV. It checks IDs, references, frame counts, FPS, rig/clip identity and continuity of wrist/prop centers across normal shot boundaries.
- `examples/p6_v2_motions.json` contains six distinct motion definitions; P4 IK compiles each independently, with **no remapping of one 48-pose source clip over the whole film**. Each shot's local frame selects the exact corresponding pose.
- `scripts/prepare_film_v2.py` verifies the real Spine rig profile/bone hierarchy and source shoulder/arm lengths, then builds exact timeline+motion assets. Incorrect proportion, unknown assets or discontinuities reject early.
- `runtime/film_v2_scene.mjs` loads rig JSON/atlas, background and prop PNG using catalog references, instantiates real Spine actors by **actor identity** (including two actors visible simultaneously, even if they share a rig asset), applies IK bone rotations and validates actual hand-bone/prop contact.
- `runtime/film_v2_render.mjs` uses a frame-index API, outputs exact PNGs, and compares SHA-256 hashes when replaying shot-boundary frames. It supports arbitrary film lengths and resolutions within the current schema; strict 5-shot acceptance is opt-in.
- `studio/voice.py` (reused) places PCM16 mono 24-kHz WAVs on integer frame boundaries at 1000 samples per 24-FPS frame; missing files, overlap and shot overflow cause errors.
- `scripts/run_film_v2.py` is an end-to-end local command for validated real asset files and supplied WAVs. It compiles, builds the browser runtime, renders frames, muxes FFmpeg H.264/AAC and verifies MP4 frame count with ffprobe. `POST /film/v2/compile` and `POST /handoff/film/v2/export` support manual AI director copy/paste import.
- Legacy `film.v1` and P0–P4 modules stay working and are covered by regression CI.

## Technical acceptance film: The Coffee Cup Save v2

- 5 shots, 672 total frames at 24 FPS = 28.000 seconds.
- Shot lengths 96/144/144/144/144 frames.
- Six independent motion IDs: `hero_wait`, `hero_reach`, `hero_rescue`, `friend_watch`, `friend_fix`, `spectator_wait`. At least one unique action sequence per shot.
- Two independent Genielabs-generated synthetic five-part Spine rigs (`baseline`, `compact`), two actual PNG backgrounds (`cafe_morning`, `cafe_evening`), one reusable red mug PNG.
- Shot 4 and 5 render both `friend` and `spectator` concurrently; only `friend` owns the mug. Each actor uses a separate skeleton instance, and the wrist/prop contact remains verified.
- Visual milestone review of all five first/last shot frames: no missing characters/backgrounds, prop stays continuous through normal shot boundaries, fixed-camera cuts operate, the second rig enters and two actors are visible in shots 4/5.
- FFprobe checks H.264 video + AAC audio, 640×480 resolution, exactly 672 read video frames and 28.000-second file duration. Playback has an **artificial signal WAV soundtrack**, NOT Kokoro reading the narration text.
- Shot-level audio start frames remain 8/102/246/392/536 with the supplied WAV track; master PCM duration 672,000 samples at 24 kHz.
- Python core C0/C1 regression target: 173 focused parameterized tests pass, 749 measured statements and 234 branches at 100%. FastAPI entrypoints, JavaScript renderer and upstream packages are outside that Python metric; Playwright and FFprobe are separate integration gates.

## Defects found during implementation and fixes

1. `film.v1` stretched one 48-frame P4 movement into 672 frames with only camera changes. **Replaced** with new per-shot motion clips and exact frame indexes in v2; kept v1 for compatibility.
2. Initial renderer shared one character instance per rig ID, which would fail when two actors shared the same rig. **Fixed** by independently instantiating skeletons keyed by actor identity.
3. The general-purpose local CLI failed an absolute import (`ModuleNotFoundError: scripts`). **Fixed** sibling module import and retested end-to-end command in GitHub CI.
4. A CI assertion still expected exactly five unique motions after adding the `spectator_wait` clip. The exported movie was valid; **corrected** acceptance expectation to six and reran CI.
5. Tightened authoring boundaries: compare source shoulder/pivots and lengths to the actual Spine rig before starting the browser; reject invalid manual plans.
6. All assets in the acceptance demo are deterministic generated test fixtures and NOT representations of G-Labs' image generation performance.

## Remaining quality gaps — separate from P5/P6 *technical* scope

- Artificial CI audio is **not speech**. No Kokoro TTS, no alignment at word/phoneme level, no vocal-expression QA; expressly deferred by the user.
- The 640×480 five-part cartoon fixtures have basic IK, static/wait actions and simplistic blocking/acting. This proves independent shot control, **not professional character animation quality**.
- No G-Labs authenticated Windows live image task or test on G-Labs-generated character art; deferred.
- P5 web UI project manager is not built: prompt export, typed JSON import, CLI orchestration and file outputs exist, but the full graphical editor/asset-library views remain separate UI work.
- Current per-shot P4 `MotionPlan` contract requires a grabbed prop to be placed before the end of its clip. Seamless carrying a single held prop *across cuts* would require an explicit clip initial/final hold-state extension; the sample composes independent actions instead.
- No collision solver, lip-sync, multi-character shared-object hand-off, audio mix/music or full production render QC. P7 independent second-story benchmark is still pending.

## Conclusion

**P5 (manual Director JSON + shot-specific asset/motion compilation): technically DONE.**
**P6 (multi-shot frame/camera render + WAV sync + FFmpeg MP4): technically DONE using supplied WAV audio.**
Authentic narration, full-body AI rigs and GUI work remain open and must not be inferred from this technical acceptance. PR remains Draft while the broader studio is incomplete.

The runnable setup and exact commands are in [P5/P6 V2 Runbook](P5_P6_V2_RUNBOOK.md). The source of truth for all phase gates is [STATUS.md](STATUS.md).
