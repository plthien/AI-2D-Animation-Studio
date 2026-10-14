# UI / Connected Local Pipeline — Implementation and Self Review

Branch: `feat/p0-p1-foundation`, PR #1. Prototype is designed for a single-user Windows desktop browser connected to FastAPI at `127.0.0.1:8000`.

## Design reference and implementation

Reviewed the user's `plthien/ytb-ai-studio` repository, specifically `src/layout/CockpitShell.tsx`, `src/layout/GlobalSidebar.tsx`, `src/layout/PipelineStepper.tsx`, `src/pages/StudioPage.tsx`, and `src/index.css`. Reused the **navigation/stage-based dark cockpit design principles** but not YouTube-specific app code or database models. The new standalone `frontend/` uses React/TypeScript + Vite, with project navigation, storyboard cards, shot inspector, editable FilmPlan/Catalog/Motion JSON, file-library review, preflight, render job status, inline MP4 preview and settings/readiness.

## Backend additions

- `studio/workspace_api.py`: project-local disk storage (`workspace/projects/<uuid>`), starter film templates, typed JSON save, asset/rig upload, required-asset and P4 motion validation, shot continuity, correct background resolution, 24 kHz mono WAV length and format checks, warnings for overly static/fast shots.
- Project job management uses a single-flight `ThreadPoolExecutor`, project-owned output directory and shared Spine staging guarded by a process-level lock. Not safe for multi-user internet deployment; jobs are **in-memory** on restart.
- Optional one-click **synthetic demo assets**: pinned Genielabs five-part fixtures, two sets/props and non-speech WAVs. User-controlled, no AI API, enables testing UI → preflight → browser render → FFmpeg MP4 before G-Labs/Kokoro are available.
- Optional **G-Labs Webhook** UI + backend task ownership: explicit quota confirmation, one POST without auto retry, poll, verify same-origin download, convert to project PNG. Credentials remain in backend env. Only **mocked test** exists: real authenticated Windows/MAX integration must be tested by user.
- Optional **Rig Workshop**: stage 1 segment a supplied separated-parts atlas, stage 2 position against reference, stage 3 require explicit human semantic labels/anchors and build the accepted +X neutral two-link Spine rig. P2/P4 synthetic Genielabs integration was previously verified; the new UI flow for diverse AI-made characters is **not yet production certified**.
- Image import accepts PNG, JPEG and WebP and normalizes to PNG with decode/pixel/size guards. Invalid FilmPlan/MotionPlan inputs now return typed HTTP 422 instead of unhandled HTTP 500.

## Actual test evidence and self-review fixes

- The existing Python core CI remains configured to 100% C0/C1 for `studio/film*.py`, glabs, motion, rigging, handoff, voice, retarget, world. The new FastAPI/UI service is deliberately excluded from this figure, and exercised separately through `tests/test_workspace_api.py` and real Chromium.
- `.github/workflows/ui-cockpit.yml` installs frontend dependencies, typechecks/builds TypeScript, uses a real TestClient to create/update projects, import media, verify errors/guards, then opens the built cockpit in Playwright and drives create → storyboard → missing-asset render block → one-click synthetic assets → preflight → actual 28-second MP4; validates the file response and screenshot. This is a **synthetic integration smoke**, not a guarantee about actual images/voices.
- Caught a validation exception that returned HTTP 500 for malformed manual JSON; changed to HTTP 422 with field-specific details.
- Caught an erroneous screenshot assertion using a too-high bright-pixel threshold on the intentionally dark UI; corrected it to check meaningful nonblack content and verify actual DOM/render output separately.
- Caught the original image import incompatibility for JPEG/WebP provider outputs; added explicit server-side decode and PNG normalization.
- Added deterministic lightweight head secondary motion to the sample Spine renderer and quality warnings about excessive wrist stillness or travel without breaking hand/prop contact. This is **not** realistic full-body motion generation or art-direction QA.

## Remaining hard requirements before production readiness

1. **Real G-Labs roundtrip** (paid, local Windows): authenticity, API key, task ownership/download and reference consistency; intentionally not executed from CI.
2. **Real character rig QC** from actual AI atlas/reference with user-approved semantics and pivots, beyond synthetic 5-part sample. Current P4 motion path handles only a neutral single two-link arm/one prop per character.
3. **Kokoro/TTS + expressive narration/lip synchronization**: not integrated here; WAVs in automated tests are non-speech signals.
4. **Motion/art quality**: no advanced body physics, hand posing, footsteps, facial emotion, deform mesh, collision or animated camera path; static shots can still look mechanical despite warnings.
5. **Production reliability**: no durable restart-safe render worker, cancellable tasks, project-scoped Chromium staging for concurrent renders, versioned asset history or automated recovery; one process and one job at a time only.
6. **UI editing**: no true interactive timeline drag handles or keyframe IK editor; film and motion JSON remain editable text and shot-inspector fields.

This implementation is intended as a **local user-testable cockpit**, not a claim that a no-touch, studio-quality idea-to-video factory is finished. [Windows testing guide](STUDIO_UI_USER_GUIDE.md), [project phase status](STATUS.md), [PR #1](https://github.com/plthien/AI-2D-Animation-Studio/pull/1).


## 2026-10-14 user-test hardening

- Read the actual `plthien/ytb-ai-studio` `CockpitShell`, `GlobalSidebar`, `StudioPipeline` and dark theme and reviewed the already implemented local React/Vite cockpit. Kept the standalone animation-specific app; no copy of YouTube workflow logic.
- Director stage stepper now routes to relevant sections and reflects whether core project documents, rigs, background images, motion definitions, voice WAVs and preflight are available. This is a **readiness indicator**, not a substitute for complete preflight.
- The manual JSON editor now guards unsaved drafts when switching JSON documents or reloading. It no longer resets the text after unrelated film/camera state updates. Raw JSON save remains explicitly validated by backend.
- The local setup now installs an **isolated Python 3.12 `.venv`** and checks Node major version 22; startup uses that exact virtual environment rather than whichever global Python happens to be on PATH. This is Windows-specific and must be checked on an actual Windows machine; Linux CI cannot prove batch behavior.
- Added persistent MP4 availability check (project-local `/studio/projects/{id}/video/status`) so a successfully rendered file remains visible/downloadable after backend restart, even if in-memory job IDs are gone. Includes a focused API test.
- Existing built cockpit CI runs React TypeScript build, API TestClient smoke, and a real Playwright browser run through project creation / offline asset creation / render / MP4 response. It does **not** assert that G-Labs authenticated provider tasks work on the user's Windows installation.
- No Kokoro/TTS is added here; existing WAV import/sample-rate checks remain required. Synthetic waveform demo audio must never be represented as real generated speech.

**Release interpretation:** local user-testable prototype with real UI and offline end-to-end technical render. The user-facing intent of a fully automatic, professional-quality original-character studio is NOT yet met: verified G-Labs image-to-rig quality, high-quality multi-limb acting, local Kokoro, durable job queue and GUI keyframe motion editor are open.
