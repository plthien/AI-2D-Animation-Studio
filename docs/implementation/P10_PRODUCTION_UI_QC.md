# P10 — Durable production operations, full workflow UX, QC
**Prerequisite:** approved P9 video pipeline. **Owning skills:** `phase-self-review`, `spine-renderer`, `voice-video-assembly`. **Schema:** `qc_report.v1`.

## Work orders

**P10.01 Durable workers.** Implement `app/modules/production/{durable_render,qc}.py`, `app/repositories/operations.py`, `app/durable_render_runner.py`, and use P0 `operations`/`operation_tasks` tables. A worker claims queued operation by conditional `lease_owner`, randomly generated token, expiry, attempt and input hash; persists token before IO. Renew while running, re-check token immediately before progress, artifact write and final publication. Dead/stale owner result cannot publish. GET endpoints must be read-only and never drive work. Restart detects expired lease and safely reschedules only idempotent local rendering; *never* replay uncertain paid G-Labs submissions.

**P10.02 Process ownership & cancel.** Stable process handle for Chromium/FFmpeg job, OS-safe interruption, child cleanup, bounded retries for local deterministic stages; bounded logs strip secrets and user-provided prompt fragments. Paths always scoped project/operation/attempt. Cancellation atomically records intent before attempting signal; late exit cannot convert cancelled operation to success.

**P10.03 QC.** `QualityGate.evaluate(context)->qc_report.v1` records output SHA/path, frame count and nonblank coverage, full approved Spine asset identity, named runtime bones, foot/contact thresholds, prop ownership continuity, 48k audio/count, ffprobe codecs/rate/dimensions, licensed runtime packaging gate, user review/signoff. Distinguish `technical_only`, `passed`, `failed`, `review_required`; `passed` impossible with required real visual/live voice/manual gates NOT_RUN. Failing gate includes actual observed metric/value/unit/allowed max; never hardcode success.

**P10.04 UI.** Build `src/features/render/{RenderJobStatus,QCReviewPanel}.tsx`, ensure all seven stages navigable/ready/blocked from backend projection; show exact progress, failures, correction flow, previews, waveform, downloadable MP4 and not-run gates. `src/features/studio/StudioPipeline.tsx` or page shell must persist selected project and pending frozen prompts after browser reload. React Query polls only active operations at bounded cadence; no full workspace reload in polling loop. Browser tests cover keyboard, disabled paid call, ambiguous operation, stale draft, cancel/retry.

**P10.05 Endpoint completeness.** `GET /operations/{id}`, `POST /operations/{id}/cancel`, `GET /projects/{id}/render/status`, `/render/download`, `/qc` all project/channel scoped. Human approval is explicit CAS update with evidence SHA; status badge must not claim accepted based on fake provider/task. Update static OpenAPI and TS client from actual current routes.

## Tests and gates

Kill Chromium during second shot then restart worker, inject SQLite write crash before output publication, contest same lease with stale tokens, two projects rendering concurrently, cancel after compile and after render, corrupt PNG in final mux, cross-project traversal, injected missing audio, stale source SHA after a successful preview, render once vs repeated render output identity on deterministic environment. Browser end-to-end seven-step navigation must run in real Chromium, not just React unit tests. `tests/e2e/*`, `tests/render/test_durable_*.py`, UI tests and full contract tool suite. **Exit:** crash-safe work ownership and honest UI readiness, NOT production-accepted until P11 evidence.

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
