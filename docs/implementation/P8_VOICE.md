# P8 — Real narration voice providers, post-animation
**Prerequisite:** P7 real compiled/preview frames; narration Script/ShotPlan approved. **Owning skill:** `voice-video-assembly`. **Contract:** `voice_manifest.v1`; 48kHz sample authority.

## Work orders

**P8.01 Cohesive voice port.** Create `app/modules/voice/` by selectively adapting YTB `voice_*`, `elevenlabs_*` and provider execution modules plus canonical `kokoro/` wrapper, `app/api/routes/voice.py`, `app/api/schemas/voice.py`, `src/features/voice/VoicePanel.tsx`, `tests/voice/*`. Retain exact Kokoro model `kokoro-v1.0.onnx`, voices `voices-v1.0.bin`, pinned hashes/calibration identity, immutable wrapper command; ElevenLabs optional and only with user key. Eliminate voice-first Script/Scene dependency and render graph assumptions. No synthetic tone saved as real narration.

**P8.02 Cue derivation.** `VoiceCueCompiler.from_approved_shots(script,shot_plan)->list[VoiceCue]`: one cue per shot with nonempty `narration_text`; omit silent visual reaction/establishing shots. Cue `shot_id`, exact UTF-8 narration, **absolute** original-film `start_frame` (sum prior shot durations), `start_sample=start_frame*2000`, expected original window `duration_frames*2000`. One voice/provider per narration track in MVP; spoken two-character dialogue is unsupported. `voice_manifest.cues` lists exactly all voiced shots in order; at least one voiced shot per film.

**P8.03 TTS normalization & alignment.** `SpeechGenerator.generate(cue,provider_profile)->CanonicalWav`: exact 48_000 Hz, mono PCM16 (`s16le`), no clipping, no zero-sample WAV. Convert provider formats without changing spoken text. Kokoro speed control may be calibrated, but reject stale identity with `VOICE_PACING_CALIBRATION_IDENTITY_INVALID`; no silent fallback to different model or pace. ElevenLabs forced word alignment only if configured; absence sets `alignment_status=unavailable`, no invented word offsets. Imported WAV follows exact same byte validator.

**P8.04 Distinguish raw overrun from final schedule.** P8 may publish a valid WAV longer than originally planned shot; record actual `duration_samples` and readiness flag `needs_reconciliation`. **Do not truncate TTS or reject only because it overran original frames**: P9 decides if max +48 safe hold-only extension exists, otherwise `VOICE_WINDOW_OVERFLOW`. A voiced cue `start_sample` remains pinned to the **original compiled-film shot start** in P8; P9 recalculates final cue starts for extended shots in final timeline. This rule supersedes the premature overrun assertion in old Master §4.2.

**P8.05 API & UI.** `POST /api/v1/projects/{id}/voice/generate`, `POST /api/v1/projects/{id}/voice/import`, `GET /api/v1/projects/{id}/voice/status`, `GET /api/v1/projects/{id}/voice/manifest`; UI choose provider+voice, read readiness, generate only via explicit action, review per-shot waveform/text and alignment. Voice regeneration publishes new voice manifest revision, invalidates final timeline/MP4 only, not rigs/motion.

## Negative tests and gate

`test_kokoro_readiness.py` invalid asset hash, process interruption; `test_provider_identity.py` calibration mismatch; `test_wav_format.py` stereo/44.1k/24k/truncated, missing alignment, text mismatch; `test_silent_cue_subset.py` silent shot excludes cue; `test_raw_overrun.py` valid +10frame speech stored and marked for P9. Also manual test real TTS if configured; otherwise explicitly NOT_RUN, fixture bytes only. **Exit:** verified speech WAV artifacts attached to voiced shots with precise provenance, not yet final timing.

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
