# P9 — Voice-last timing reconciliation and H.264/AAC assembly
**Prerequisite:** P7 frame sequences and P8 verified voice manifest. **Owning skill:** `voice-video-assembly`. **Contracts:** `voice_manifest.v1`,`final_timeline.v1`,`frame_sequence_manifest.v1`.

## Work orders

**P9.01 Timing algorithm.** Create `app/modules/voice/timing_reconciliation.py` and `app/modules/production/{ffmpeg_runner,probe}.py`, `src/features/render/FinalReviewPanel.tsx`, `tests/voice/test_reconciliation.py`, `tests/render/test_ffprobe.py`. Let canonical `samples_per_frame=48000//24=2000`. For each shot in order, `orig_frames=duration_frames`, `wav_samples=verified WAV sample count` if voiced, else zero; `needed_frames=max(0,ceil_div(wav_samples,2000)-orig_frames)`. If needed>0, extend only legal terminal `idle/hold` window explicitly approved in compiled motion; cap extension at 48 frames; disallow extension overlapping grab/release/contact/action boundary; otherwise fail `VOICE_WINDOW_OVERFLOW` or `VOICE_HOLD_UNSAFE`. Never speed/stretch spoken audio or truncate. `final_frames=orig_frames+needed_frames` and `absolute_start_frame` cumulative prior **final** frames.

**P9.02 Audio construction.** For each shot allocate exactly `final_frames*2000` samples; copy verified PCM from cue to start of its own shot buffer; pad end with zero samples, silent shots entirely zero; concatenate in final shot order. Verify full assembled mono WAV sample_count = `final_timeline.total_frames*2000`, all sample positions integer, no overlap, no clipping. `voice_manifest.start_sample` refers to original compiled start and remains immutable; reconstructed final offsets derive from `final_timeline` instead of mutating voice manifest. Relative per-shot narration always starts frame zero of that shot in MVP; future offset requires new schema.

**P9.03 Selective rerender.** Reuse P7 frame sequence for unextended shots; for extended shots re-evaluate approved terminal hold pose and camera/prop state per new frames **without changing event timestamps**. New sequence manifest hash recorded; never modify previously approved PNGs in place. An extended shot final length <=768 can exceed `compiled_film` shot 720 frame cap (it is a **final timeline** duration only); ensure `final_timeline.v1.shots[].final_frames` accepts up to 768 and `total_frames` up to 23040, or strictly cap ShotPlan planned duration to <=672 whenever extension may be needed. **Final timeline schema is already widened in this documentation pack to 768 frames/shot and 23040 total; compiled film stays <=720 planned frames per shot.**

**P9.04 FFmpeg.** Extract process supervision/cancel/progress and ffprobe portions of pinned YTB FFmpeg code into `ffmpeg_runner.py`, not Ken Burns/crop filters. Input shot PNG streams at 24 FPS; concat exact per-shot sequences, mux canonical narration to AAC 192 kbps, output H.264 `yuv420p` 1280x720 24 FPS CFR MP4. Use argument-list subprocess, bounded error stderr, short path aliases on Windows, cancel process group safely; no shell interpolation of user-supplied names. Probe video expected frame count/fps/dimensions and audio duration within AAC encoder packet delay tolerance. `FinalTimeline` published CAS only after probe and SHA verification.

**P9.05 API/UX.** `POST /api/v1/projects/{id}/voice/reconcile`, `POST /api/v1/projects/{id}/render/final`, `GET /api/v1/projects/{id}/render/download`. Show per-shot needed extension and blocking unsafe holds. Download serves verified current artifact only with path ownership checks.

## Gate tests

`wav_samples=orig_frames*2000`: 0 extension; `wav_samples=orig+1`: needs 1 frame; exactly orig+48 frames legal: 48 extension; 49th frame blocked; a 720-frame shot +48 fits final schema 768; 30×768 total fits 23040; one silent shot between narrated shots inserts proper zero duration; an action ending last frame forbids hold if not safe; ffprobe H.264/AAC CFR 24fps 720p; encoder AAC delay accounted without silently truncating WAV. **Exit:** real MP4 with actual frame-level 2D animation and speech (or imported real spoken WAV), not still-image video.

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
