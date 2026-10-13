# AI 2D Animation Studio

Local-first 2D animation engine: manual ChatGPT/DeepSeek Director JSON → (eventually G-Labs image assets) → Genielabs Spine rig → reusable P4 IK/motion primitives → per-shot PixiJS/Spine film → FFmpeg H.264/AAC.

## P7: second-story engine reuse proof — PASS

The first film (**The Coffee Cup Save**, 28 seconds, 672 frames, six motion clips) and second film (**The Lost Key**, 21 seconds, 504 frames, five motion clips) now render through the **same unchanged P5/P6 source engine**. The second film uses the existing two Spine rig variants, new workshop day/twilight PNGs, a new brass key prop PNG and completely separate Director/Motion JSON. Both are verified 24fps 640×480 MP4s with two separate clean frame workspaces.

- [P7 two-story GitHub Actions proof and MP4 artifacts](https://github.com/plthien/AI-2D-Animation-Studio/actions/runs/38486839154)
- [P7 self-review, bugs and acceptance scope](docs/P7_SELF_REVIEW.md)
- [Run both films locally](docs/P7_RUNBOOK.md)
- [Overall phase status](docs/STATUS.md)
- [Draft PR #1](https://github.com/plthien/AI-2D-Animation-Studio/pull/1)

## Project status

P5 per-shot Director and asset/motion compiler, P6 WAV-based multi-shot render/FFmpeg and P7 bounded second-story reuse are **technically validated**. P0–P4 support these demos with actual Genielabs Spine bones. The first G-Labs authenticated generation test and local Kokoro TTS were deferred by the user. CI uses **synthetic five-part characters and non-speech tone WAVs**, not finished human-like animation and not Kokoro narration.

The Studio still lacks a complete GUI editor, full-body production rigs, polished acting/lip-sync, sound direction, and verification on real AI-generated assets. Never interpret two successful demos as proof of universal story generalization or a production-ready film system. The PR stays Draft, not merged into `main`.
