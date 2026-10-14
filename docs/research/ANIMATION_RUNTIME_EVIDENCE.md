# Animation runtime research and release constraints (verified 2026-10-14)

This report documents integration-relevant public references; it is not a claim that any rig/video was produced.

## Official renderer and export authority

- https://en.esotericsoftware.com/spine-pixi — maintained official `@esotericsoftware/spine-pixi-v8` is compatible with PixiJS v8 (minimum 8.16). Runtime major.minor must match Spine skeleton export major.minor. The project targets Spine 4.2 JSON with official 4.2.x runtime, pinned exactly in lockfile during P4/P7.
- https://esotericsoftware.com/spine-json-format — JSON skeleton is bones (parents before children), slots (draw order), skins/attachments and optional animation timelines. JSON is human readable but slower/larger than binary; the MVP intentionally selects JSON to make native export/QA inspectable. Runtime must load actual atlas/png and pose the live Spine object.
- https://en.esotericsoftware.com/spine-pixi — WebGL/WebGPU support is complete; Canvas mode does not support some features such as slot objects, tint-black and blend modes. Prefer fixed WebGL Chromium backend and verify actual screenshot pixels, not mocks.
- https://github.com/EsotericSoftware/spine-runtimes — official source and runtime licensing instructions. For distribution ensure appropriate Spine license and include relevant runtime license; do not assume generic permissive open-source rights. Relevant legal text: https://esotericsoftware.com/spine-editor-license. Legal review / user confirmation precedes bundling official runtime into distributed application.

## Local-first native rig and animation design choice

- 14 semantic 2D cutout image regions with 14 reviewed pivot positions and 16 core semantic skeleton roles are project-owned **product constraints**, not a claim of automatic anatomical recovery from arbitrary images. Alpha segmentation/feature matching can fail; require manual workshop resolution.
- Motion is compiled from fixed nine-action DSL and semantic RigProfile. Foot IK contact, world-state transforms and ownership are deterministic and fail closed if infeasible. Additional control bones are allowed when approved and validated.
- Reuse from Genielabs is *conceptual research only* and does not authorize copying, vendoring or running its code. Users must approve paid G-Labs calls; no ChatGPT/DeepSeek API integration.

## Research-to-test traceability

P4 real rig loading tests prove official runtime compatibility and atlas/part placement. P5 contact/foot/slip tests prove procedural motion semantics. P7 independent frame seek/PNG hashes prove deterministic rendering. P11 real 2-film tests, licensed distribution gate and real-provider provenance are the production definition of done.
