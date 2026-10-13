# P7 — Two-story engine reuse: technical acceptance and self-review

Reviewed: 2026-10-14. Branch: `feat/p0-p1-foundation`. This is an evidence-based **bounded reusability proof**, not a claim that arbitrary film scripts or fully automatic character acting are solved.

## P7 goal and exact result

Use a SECOND, genuinely different fictional story with new background art and prop, retaining the SAME P5/P6 compiler, Spine PixiJS renderer, reusable rigs and P4 motion primitives. No shot-specific JavaScript/TypeScript and no new AI LLM/TTS/G-Labs API calls.

| | Story A: The Coffee Cup Save | Story B: The Lost Key |
|---|---|---|
| Source FilmPlan | `examples/p6_v2_film.json` | `examples/p7_lost_key_film.json` |
| Source motion definitions | `examples/p6_v2_motions.json` | `examples/p7_lost_key_motions.json` |
| Background assets | cafe_morning / cafe_evening | workshop_sunrise / workshop_twilight |
| Visual prop | red_mug PNG | brass_key PNG (new geometry) |
| Reused character rigs | baseline + compact | SAME baseline + compact |
| Shot count | 5 | 5 |
| Independent motion clips | 6 | 5 |
| Duration | 672 frames / 28s | 504 frames / 21s |
| Outputs | H.264 + AAC MP4 | H.264 + AAC MP4 |

The second story is a fictional miniature comedy. An apparently lost key is visible on a workshop bench; a character finds and hangs it on a hook; later a second character takes it down and puts it on another shelf. All actions are authored via existing `wait`, `reach`, `grab`, `carry`, `place` primitives. The feature implementation uses story-specific JSON and **PNG fixture-generation script only**, never story-specific animation engine code.

## Verifiable acceptance

- **Final P7 real integration CI [38486839154](https://github.com/plthien/AI-2D-Animation-Studio/actions/runs/38486839154)**: PASS. Artifact: [p7-two-stories-spine-reuse-proof](https://github.com/plthien/AI-2D-Animation-Studio/actions/runs/38486839154/artifacts/11859353882). Contains both MP4s, 10 beginning/end shot preview PNGs per story, SHA-256 engine fingerprint and acceptance manifests.
- GitHub action runs the SAME public `scripts/run_film_v2.py` **twice**, with unchanged `studio/film_v2.py`, `studio/motion.py`, `studio/voice.py`, `runtime/film_v2_scene.mjs`, `runtime/film_v2_render.mjs`, `scripts/run_film_v2.py`. The action checks these source hashes with `sha256sum -c` after both movies and `git diff --exit-code` for all tracked studio/runtime/scripts files.
- The **same two upstream Genielabs synthetic Spine rigs** are built only once, copied into `runtime/fixtures` and used by both stories. Both movies rendered in actual Chromium with Spine/PixiJS bone transforms, not procedural overdraw.
- `ffprobe` verifies Story A = **672 read frames, 24 FPS, 28s**, Story B = **504 read frames, 24 FPS, 21s**, both 640×480 H.264 video + AAC audio. Videos have distinct SHA-256 hashes.
- P7 acceptance checks separate `--workspace` locations, exactly 672 and 504 emitted PNGs, 10 replay-stable screenshot checkpoints per film, five shot records, correct motion/rig/background IDs and separate audio manifests.
- Final Python CI [38486841669](https://github.com/plthien/AI-2D-Animation-Studio/actions/runs/38486841669): **176 tests passed, C0/C1 100%** for configured first-party Python modules: 749/749 statements, 234/234 branches. Only three compact P7 unit tests were added to prove both plans, exact per-shot source lengths, two-person retrieval continuity, and a bad-prop transition that must be rejected. API/JS/vendor are not part of the 100% metric.

## Bugs caught and fixed during self-review

1. **Cross-film frame residue risk:** The previous local runner wrote into a single fixed `outputs/p6_v2` directory. If a subsequent film had fewer frames, obsolete PNGs could survive and contaminate encoding. The generic CLI now allows **`--workspace` per film** and removes old `frames/` and `previews/` before rendering. Acceptance explicitly audits frame counts for a longer Story A followed by shorter Story B.
2. **Semantic scene teleport not caught by coordinate assertions:** First Story B draft hung the key inside a workshop then cut to an unrelated hallway while keeping the same pixel coordinates; numerical continuity was green despite incorrect storytelling geography. Fixed both backgrounds to represent the **same workshop with consistent hook, desk, windows and pegboard**, at sunrise and twilight. The visual storyboard was inspected again after re-render.
3. **Acceptance versus production:** The second story was deliberately generated solely with new JSON, images and existing primitives. It proves parameterization and asset swapping for supported one-arm/one-prop behaviors, **not** automatic animation direction for every possible script.
4. **Visual limits:** Five-part synthetic actors lack legs, realistic gestures and expressive faces. Some holding/waiting phases look static and object positioning remains cartoon-simple. These are quality/open scope, not incorrectly represented as finished video-production animation.
5. **Audio limits:** Each story has five **synthetic non-speech** 2-second sine WAVs for exact sample alignment and FFmpeg mux checks, not actual Kokoro narration. This is intentional as requested.
6. **Execution scope:** The renderer currently uses a global `runtime/fixtures` source folder and is sequential; concurrent multi-project executions would require project-scoped fixture roots/port and resource isolation. One actor/prop contact per motion clip and simple one-arm IK are current contracts.
7. **World semantics:** `film.v2` validates wrist/prop coordinates across ordinary cuts but does not infer that two differently illustrated backgrounds refer to a consistent physical room. Human/visual review remains necessary.

## Final interpretation

**P7 technical gate: PASS** for the agreed two-story reuse benchmark. The engine successfully produces a second distinct film with a new prop, new backgrounds, new motion JSON and the same Spine rigs without per-shot runtime changes. **It is not a universal animation system**, nor is the overall Studio production-ready. P1 G-Labs live/AI-asset quality, real Kokoro, full-body animation/art direction and the project GUI still need separate acceptance.

See [P7 local runbook](P7_RUNBOOK.md), [status](STATUS.md), [PR #1](https://github.com/plthien/AI-2D-Animation-Studio/pull/1).
