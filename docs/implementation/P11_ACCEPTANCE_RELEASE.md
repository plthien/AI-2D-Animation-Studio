# P11 — Two real films, Windows smoke, release decision
**Prerequisite:** P0–P10 approved and merged, no open BLOCKER/HIGH. **Owning skill:** `phase-self-review`. **Fixture authority:** Master Spec Appendix B (Film A) and G (Film B); no story-specific engine code.

## Work orders

**P11.01 Fixture data.** Create `tests/fixtures/acceptance/film_a/` and `film_b/` with authored `script`,`shot_plan`,`animation_plan` and reproducible manifest checks; use required actor/prop/camera identities from Master appendices. Film A Honey Jar Surprise 8 shots 40s planned (960 frames), Film B Lost Hat 7 shots 35s planned (840 frames). The second movie must bind same Actor A's *exact approved* character/rig asset version and same motion template version, while using a new hat and location/background, without changes to `app/modules/animation/**` or `runtime/spine/**` after acceptance rehearsal.

**P11.02 Live media proof.** Under explicit G-Labs cost approval and user credentials run character reference + parts atlas for **two distinct actors**, appropriate background/props, all approvals and native segmentation/joint pose QA. Record original provider task IDs, model, refs, immutable SHA, before/after manually corrected parts and review screenshots. Never commit paid PNGs, credentials or real voice WAV to Git. Without user credentials mark G-Labs acceptance `NOT_RUN` and overall `BLOCKED`, not synthetic-pass.

**P11.03 Animation proof.** Render all shots via approved RigProfiles, MotionTemplate snapshots and compiled film; verify actors visibly walk/reach/grab/carry/place/react, actor holds same jar across cut, `walk_to+look_at` concurrent, no missing attachments, no foot slide >0.01m and contact error <=0.003m, two separate actor instances. Film B must reuse character rigs without new builder code. Review at least first/middle/last image per shot in manual visual checklist.

**P11.04 Voice/MP4 proof.** Produce real Kokoro or ElevenLabs spoken voice, 48k mono PCM16, timing reconciliation (only safe holds), 24 FPS/720p/H.264/AAC MP4; playback with audio, stable captions if included. ffprobe report exact frame counts and voice waveform; preserve per-shot PNG manifests and output hashes. Verify one film production 30–60sec. Repeat same run on Windows 10/11 x64 local machine; Linux CI gives unit tests but cannot replace this gate.

**P11.05 Audit, packaging & release.** Create `docs/FINAL_ACCEPTANCE.md`, `docs/BUILD_STATUS.md`, Windows install/recovery instructions, `docs/qa/PHASE_P11_REVIEW.md`, GitHub workflows for Python, TS frontend/runtime, contract/semantic agents, and Windows smoke when runner available. Verify runtime distribution/licensing (`docs/research/ANIMATION_RUNTIME_EVIDENCE.md`) before packaging, no forbidden imported Genielabs/prototype/YTB still-beat source, no exposed credentials, no unlocked dependencies, no fake real-run report. Physical acceptance statuses `PRODUCTION_ACCEPTED` only when Film A+Film B, G-Labs, rig QA, real speech, frame render, Win smoke, license gate ALL passed.

## Final command set and exit

`python tools/validate_contract_pack.py && python tools/test_animation_contract_semantics.py && python tools/validate_agent_pack.py && python tools/validate_implementation_pack.py`; `python -m pytest tests/platform tests/authoring tests/assets tests/rigging tests/animation tests/director tests/render tests/voice tests/api tests/e2e -q`; `npm ci && npm run build && npm test`; `(cd runtime && npm ci && npm run build && npm test)`; disposable `python -m alembic upgrade head`; inspect ffprobe, runtime/browser screenshots and source review. Record exact exit code + commit + environment, including `NOT_RUN` tests. **Stop and report blocked** rather than lowering quality gate or crafting synthetic acceptance video.

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
