# AI 2D Animation Studio

Local-first AI + skeletal 2D animation production system.

**Status: partial implementation, NOT a complete video generator.** See [implementation gates](docs/STATUS.md). A real Spine sample render and real G-Labs end-to-end run have not been verified.

## Selected flow

ChatGPT/DeepSeek (manual JSON) → G-Labs Webhook (images) → Genielabs (parts/skeleton/presets) → Spine/PixiJS runtime → FFmpeg (final video).

The current branch implements a Python backend foundation, manual handoff, G-Labs webhook adapter, and a Genielabs rig configuration adapter. Spine renderer, motion planner, voice and assembly require later phases.

See [PowerShell setup](docs/RUNNING.md) and [implementation status](docs/STATUS.md).
