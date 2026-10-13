# AI 2D Animation Studio

Local-first 2D production prototype:
**ChatGPT/DeepSeek manual director → G-Labs image webhook → Genielabs Spine rig → motion compiler → Spine/PixiJS shot renderer → FFmpeg**.

## Verified milestone state

- P0: browser Spine 4.2 nonblank runtime — PASS.
- P1: G-Labs Webhook adapter implemented; real Windows MAX live test **deferred** by user.
- P2: Genielabs segmentation / rig / atlas integration — PASS on synthetic source art, not production AI characters.
- P3: fixed-step Spine/PixiJS frame exporter — PASS at 640×480.
- P4/P4.2/P4.3: real Spine arm IK, rotating prop grip socket, actor-local motion reuse and fixed-world cup targets across two synthetic rigs — PASS technical integration.
- **P5**: typed five-shot manual director JSON, copy/paste prompt export, strict 24fps timeline compiler and local FastAPI import/validation — **functional prototype PASS**.
- **P6**: Spine/PixiJS renders **672 frames (5 shots × 28 seconds at 24 FPS)** with camera cuts; sample-accurate WAV synchronization and FFmpeg create a verified **28-second H.264/AAC MP4** — **technical export PASS**. Demo soundtrack is **synthetic non-speech tone**, NOT Kokoro narration.
- P7 second distinct story and production-grade motion reuse: not implemented.

The repo is **not yet a production-ready idea-to-video service**: authentic Kokoro generation, multi-shot acting, full AI characters, automated image QC and end-to-end scene orchestration are still open.

See [P5/P6 runbook](docs/P5_P6_RUNBOOK.md), [evidence-based self-review](docs/P5_P6_SELF_REVIEW.md), [overall status](docs/STATUS.md), and [Draft PR #1](https://github.com/plthien/AI-2D-Animation-Studio/pull/1).
