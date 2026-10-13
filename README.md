# AI 2D Animation Studio

Local-first prototype: **manual ChatGPT/DeepSeek planning → G-Labs Webhook image generation → Genielabs auto-rig → Spine/PixiJS frame rendering → later FFmpeg assembly**.

## Current status

- **P0**: real Spine 4.2 sample browser smoke with nonblank pixel QC — PASS.
- **P1**: G-Labs webhook client implemented; real Windows-local live test deferred at user's request.
- **P2**: Genielabs atlas-to-rig pipeline runs on synthetic parts, with new skeleton loading in Spine — technical smoke PASS; full-body character QC pending.
- **P3**: fixed-step Spine/PixiJS runtime exports verified 24-frame PNG sequence — small-scale smoke PASS; full multi-layer renderer pending.
- **P4–P7**: not implemented, except basic manual AI JSON handoff.

**This repo does not yet produce a complete narrated animation video.**

## Docs

- [Implementation evidence and self-review](docs/STATUS.md)
- [Genielabs rig setup](docs/P2_RIGGING.md)
- [Frame renderer](docs/P3_RENDERER.md)
- [Local setup](docs/RUNNING.md)
- [Draft implementation PR #1](https://github.com/plthien/AI-2D-Animation-Studio/pull/1)
