# AI 2D Animation Studio

Local-first AI-assisted 2D animation pipeline: **manual ChatGPT/DeepSeek director JSON → G-Labs Webhook images → Genielabs Spine rig → per-shot IK motion → Spine/PixiJS render → FFmpeg final video**.

## P5/P6: v2 technical milestones complete

The previous P6 prototype stretched a single 48-pose motion to a 28-second film. The new **`film.v2`** works differently: **each shot references its own exact-length motion clip, character rig, background and camera** via an explicit catalog, and props are checked for continuity across normal cuts.

The CI acceptance builds **five shots, six independent motion assets, two different Genielabs Spine rigs, two PNG backgrounds, one cup prop and two actors together in the final shots**, rendering 672 PNG frames at 24fps. The local CLI muxes supplied 24kHz mono PCM16 WAVs into a verified 28-second H.264/AAC MP4. The CI audio is deliberately **synthetic non-speech tones**, not Kokoro narration.

### Working interfaces

- Director handoff: `POST /handoff/film/v2/export` for copy/paste ChatGPT/DeepSeek prompt.
- Validate/compile imported JSON: `POST /film/v2/compile`.
- End-to-end CLI: `python scripts/run_film_v2.py --plan examples/p6_v2_film.json --catalog examples/p6_v2_catalog.json --motions examples/p6_v2_motions.json --voices outputs/p6_demo/voices --output outputs/film.mp4` after preparing the referenced rig/images/WAVs.
- See [full v2 runbook](docs/P5_P6_V2_RUNBOOK.md), [self-review](docs/P5_P6_V2_SELF_REVIEW.md), and [phase status](docs/STATUS.md).

## Not yet production complete

- P1 live Windows G-Labs/MAX webhook testing deferred by user.
- Actual Kokoro speech not connected; existing WAVs can be supplied without TTS.
- Full-body AI character rigging, expressive animation, lip-sync, physics and complete GUI editor not implemented.
- P7 separate story/motion reuse gate not done.

The code remains on [Draft PR #1](https://github.com/plthien/AI-2D-Animation-Studio/pull/1) and is not yet merged to `main`.
