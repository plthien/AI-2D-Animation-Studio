# AI 2D Animation Studio

Local-first project: **ChatGPT/DeepSeek manual director → G-Labs webhook images → Genielabs Auto-Rig → Spine/PixiJS animation → FFmpeg**.

## Current technical proof

- P0: browser Spine 4.2 sample renders.
- P1: G-Labs webhook client implemented, live Windows/MAX test deferred.
- P2: Genielabs atlas, rig, position technical smoke on synthetic sample.
- P3: reproducible Spine fixed-frame rendering.
- P4: actual Spine bone two-link IK, grip socket, MP4 proof with synthetic five-part character.
- P4.2: one director action JSON retargets to two different limb geometries.
- **P4.3:** both separately rigged synthetic actors reach the **same world-space coffee cup positions**, rotate it with an orientation-aware hand socket and return it to an identical final location; verified in two 2-second Spine MP4s. No per-character action script.
- P5: partial manual ChatGPT/DeepSeek prompt/JSON local API, including `POST /motion/world-retarget`; no LLM API calls.
- P6/P7: full narrated 28-second production and independent second story remain open.

**Not a finished automated idea-to-video application.** See [P4.3 evidence/self-review](docs/P4_3_SELF_REVIEW.md), [overall status](docs/STATUS.md), and [Draft PR #1](https://github.com/plthien/AI-2D-Animation-Studio/pull/1).
