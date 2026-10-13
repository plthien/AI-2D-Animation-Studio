# AI 2D Animation Studio

Local-first prototype: **manual ChatGPT/DeepSeek director → G-Labs webhook image generation → Genielabs auto-rig → Spine/PixiJS motion engine → FFmpeg video assembly**.

**Updated technical proof:** The motion planner now drives **actual upper/lower-arm bones in a Genielabs-generated five-part Spine 4.2 rig**. The coffee cup has an independent grip socket on its handle. The browser checks real wrist bone position and contact for each frame and exports a repeatable **48-frame / 2-second MP4**.

See [P4 full self-review](docs/P4_SPINE_BONE_REVIEW.md), [current status](docs/STATUS.md), and [GitHub Actions P4 real Spine run](https://github.com/plthien/AI-2D-Animation-Studio/actions/runs/38405396665).

## Phase summary

- P0: real Spine 4.2 browser nonblank render — PASS.
- P1: G-Labs Webhook adapter implemented; real Windows test deferred by user.
- P2: Genielabs technical rig pipeline with synthetic images — PASS for prototype only.
- P3: fixed-step Spine/PixiJS frame exporter — PASS for single rig.
- P4: actual Spine-bone contact and grip socket — PASS for *specific five-part prototype*. General-purpose re-targeting and animation quality remain.
- P5: manual ChatGPT/DeepSeek director handoff and motion compiler API — partial.
- P6/P7: narrated 28s video, fully reusable motion on second character — not implemented.

**Do not mistake this for a complete idea-to-video production system.**

This is still [Draft PR #1](https://github.com/plthien/AI-2D-Animation-Studio/pull/1), not merged into main.
