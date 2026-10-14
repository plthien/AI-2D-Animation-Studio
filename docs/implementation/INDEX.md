# Implementation plan index — frozen v1.3

**Authority:** `AGENTS.md` → `MASTER_SPEC.md` + schemas → Rules → matching phase plan + Skill. A conflict is a blocker, not permission to improvise.

**One phase = one PR; begin P0 from latest main; do not use prototype branch.**

| Phase file | Output |
|---|---|
| [`P0_FOUNDATION.md`](P0_FOUNDATION.md) | Port foundation, fresh 14-table SQLite, React shell; no generation |
| [`P1_EXTERNAL_AUTHORING.md`](P1_EXTERNAL_AUTHORING.md) | Three external authoring prompt/JSON stages, exact Script and silent shot |
| [`P2_ASSET_REGISTRY.md`](P2_ASSET_REGISTRY.md) | Channel-level assets, exact-identity resolver and pinned reuse |
| [`P3_GLABS_INTEGRATION.md`](P3_GLABS_INTEGRATION.md) | Paid G-Labs task lifecycle, generation/review and reference lineage |
| [`P4_NATIVE_AUTO_RIG.md`](P4_NATIVE_AUTO_RIG.md) | Segment/position/joints/Spine atlas, 5 real browser pose tests |
| [`P5_MOTION_ENGINE.md`](P5_MOTION_ENGINE.md) | Full-body IK, foot locks, hand/prop ownership and deterministic frames |
| [`P6_ANIMATION_DIRECTOR.md`](P6_ANIMATION_DIRECTOR.md) | External Director JSON contract and feasibility guards |
| [`P7_SPINE_RENDERER.md`](P7_SPINE_RENDERER.md) | Chromium Spine rendering, isolated shot sequences |
| [`P8_VOICE.md`](P8_VOICE.md) | Kokoro/ElevenLabs real speech and raw cue manifests |
| [`P9_TIMING_FFMPEG.md`](P9_TIMING_FFMPEG.md) | Safe frame holds <=48, final 768 frames, H.264/AAC MP4 |
| [`P10_PRODUCTION_UI_QC.md`](P10_PRODUCTION_UI_QC.md) | Crash-safe durable operations, complete UI and QC |
| [`P11_ACCEPTANCE_RELEASE.md`](P11_ACCEPTANCE_RELEASE.md) | Film A/B real Windows acceptance, licensing/security checks |

Contract verification: `python tools/validate_contract_pack.py`, `python tools/test_animation_contract_semantics.py`, `python tools/validate_agent_pack.py`, `python tools/validate_implementation_pack.py`, `python tools/test_cross_phase_contracts.py`. Do not claim runtime/Windows/G-Labs acceptance from contract tests.
