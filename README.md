# AI 2D Animation Studio

Local-first proof-of-concept: **ChatGPT/DeepSeek manual director → G-Labs Webhook images → Genielabs Auto-Rig → Spine/PixiJS animation → FFmpeg video**.

## Verified milestones

- **P0** browser Spine runtime: PASS.
- **P1** G-Labs Webhook client: implemented, live Windows/MAX test deferred by user.
- **P2** real Genielabs auto-rig scripts: synthetic asset generation and Spine browser checks PASS (not yet full AI character).
- **P3** fixed-step Spine/PixiJS frame renderer: PASS (single rig/short sequence).
- **P4** IK/reach/grab/prop contact on actual Genielabs-generated Spine bone chain: PASS five-part prototype.
- **P4.2** same 48-frame action JSON retargeted to **two distinct Genielabs Spine rigs (90/80px vs 70/65px arm segments)**: PASS for actor-local world restaging, with two independently generated MP4 outputs and wrist/contact validation.
- **P5** manual director + local `/motion/retarget` endpoint: partial.
- **P6–P7** full narrated 28s story and second-story reuse: not implemented.

**Current video demos are 2 seconds and use five-part synthetic characters. They are not finished publishable animation.**

Read [P4.2 self review](docs/P4_2_SELF_REVIEW.md), [rig retarget technical contract](docs/P4_RETARGETING.md), [overall status](docs/STATUS.md) and [PR #1](https://github.com/plthien/AI-2D-Animation-Studio/pull/1).
