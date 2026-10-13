# P4/P5 Self Review — 2026-10-13

## Actual evidence

- Motion compiler: `studio/motion.py`, `examples/p4_coffee_motion.json`, `scripts/compile_motion.py`.
- Diagnostic PixiJS scene: `runtime/contact_scene.mjs`, frame exporter `runtime/contact_render.mjs`.
- CI: [P4 action run 38402761203](https://github.com/plthien/AI-2D-Animation-Studio/actions/runs/38402761203). Artifact `p4-ik-contact-demo` includes 48 PNG frames, manifest, and MP4.
- Compiled values checked on all frames: upper 90px, forearm 80px; while `prop_state=held`, hand and prop centers coincide exactly; end frame releases object. Five milestones independently replayed with same PNG SHA-256.
- Manual AI bridge: `/handoff/motion/export` and `/motion/compile` via FastAPI; no model APIs invoked.
- CI source coverage: 330/330 measured statements and 106/106 branches, with compact parameterized Python tests.

## Findings

**Fixed in this iteration**
1. C0/C1 missing branch for reversed action interval; added one targeted invalid case.
2. FFmpeg missing on GitHub runner; installed via workflow before MP4 encoding.
3. Final place target initially outside the table footprint; moved to (300,199) for coherent staging.
4. Connected manual director JSON prompt generation to compiled motion API (without paid LLM endpoint).

**Remaining — blocking production claims**
1. **Critical:** P4 currently draws a PixiJS diagnostic puppet. It does **not** drive Genielabs-generated Spine upper/lower arm bones. Motion adapter to actual Spine skeleton must be designed and verified on a 4+/14-part rig.
2. **High:** Only one fixed shoulder/root and one prop are modeled; cannot yet walk, move root, handle multiple actors/props or solve collisions.
3. **High:** Hand and prop share center; a realistic grip requires an explicit contact socket/offset and correct prop z-order.
4. **High:** Procedural motion is mechanically correct but visually stiff. Ease curves, anticipation, reactions and secondary animation require artistic/motion polish.
5. **Medium:** 640×480 stage lacks adjustable camera, foreground/background compositing and per-shot asset loading.
6. **Medium:** No authenticated G-Labs image creation test (deferred); no end-to-end film with voice/music.
7. **Medium:** The manual task JSON uses a P4.1 schema separate from legacy `AnimationPlan`; migration or schema unification should occur before P6.
8. **Test scope:** Current 100% C0/C1 is for measured Python core only, not the JS canvas code, API entrypoint or third-party packages. P4 browser integration smoke supplements UT but is not itself 100%-covered.

## Recommended next phase

First build a **Spine Bone Motion Adapter** on a real multi-limb Genielabs rig, confirming hand–prop transform and full-frame contact; then add stage/camera and multi-actor support. Keep G-Labs live test deferred until local access is available.
