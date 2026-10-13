# AI 2D Animation Studio

Local-first prototype: **ChatGPT/DeepSeek manual planning → G-Labs Webhook images → Genielabs Auto-Rig → Spine/PixiJS animation → FFmpeg video**.

## Verified technical milestones

- **P0:** Spine 4.2 browser runtime can render a nonblank character.
- **P1:** G-Labs Webhook adapter implemented; live Windows/MAX request deferred at user's direction.
- **P2:** Genielabs atlas segmentation/positioning/skeleton/atlas can produce and render a new synthetic 2-part rig.
- **P3:** fixed-step PixiJS + Spine renderer exports reproducible 24-frame sequences.
- **P4 (partial):** analytic two-bone IK and prop-contact state compiler produces 48 PNG frames and a short 2-second MP4 from a PixiJS *diagnostic puppet*, **not yet a Spine-rigged actor**.
- **P5 (partial):** manually export ChatGPT/DeepSeek motion brief, then validate/compile the JSON locally with FastAPI; no LLM API.

**Not yet a full idea-to-animation production system:** Spine bone retargeting, full character visuals, multi-actor scenes, voice assembly and reuse test are outstanding.

See [CI evidence and status](docs/STATUS.md), [P4 self-review](docs/P4_SELF_REVIEW.md), [P4 local demo commands](docs/P4_MOTION.md), and [Draft PR #1](https://github.com/plthien/AI-2D-Animation-Studio/pull/1).
