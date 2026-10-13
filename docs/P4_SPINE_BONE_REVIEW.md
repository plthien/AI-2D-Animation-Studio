# P4 real Spine bone + grip socket integration — self review (2026-10-13)

## What is genuinely working

1. P4 motion JSON is compiled by `studio.motion.compile_motion` without a model API.
2. Synthetic **five-part** rig is generated through the exact pinned upstream Genielabs `build_spine_json.py` and `make_atlas.py`; output is a real Spine 4.2 `skeleton.json`, atlas and PNG (6 bones including root).
3. Chromium loads the rig in official `@esotericsoftware/spine-pixi-v8@4.2.120`, and for every frame it changes the **real** `left-upper-arm` / `left-lower-arm` local bone rotations. It does not render a procedural placeholder arm or override visibility with fake geometry.
4. It reads `left-hand` wrist bone **world coordinates** after the Spine skeleton update; fails if shoulder, elbow or wrist differs from P4 solver target by more than 0.1px.
5. Grip socket is explicit: prop center = actual wrist + `grip_offset`, currently (-16,0) for the coffee cup's handle. Contact is verified while held to 0.001px.
6. Browser exports 48 frames, replay-checks frames 0/11/14/27/47 with SHA-256, and FFmpeg produces the 2-second 640x480 MP4.

## Verified links

| Check | GitHub Actions |
|---|---|
| Actual Genielabs Spine bone contact, 48-frame MP4 | [run 38405396665](https://github.com/plthien/AI-2D-Animation-Studio/actions/runs/38405396665) |
| Older procedural PixiJS diagnostic stays compatible | [run 38405396706](https://github.com/plthien/AI-2D-Animation-Studio/actions/runs/38405396706) |
| P2 fresh synthetic rig from upstream Genielabs | [run 38405396660](https://github.com/plthien/AI-2D-Animation-Studio/actions/runs/38405396660) |
| P3 deterministic single-rig renderer | [run 38405396668](https://github.com/plthien/AI-2D-Animation-Studio/actions/runs/38405396668) |
| Python statement+branch CI | [run 38405396650](https://github.com/plthien/AI-2D-Animation-Studio/actions/runs/38405396650): 85 passed, 331 statements / 106 branches, no misses |

Generated artifact named `p4-actual-spine-bone-contact` contains `spine_bone_contact.mp4`, 48 frame PNGs, rig files and manifest. The manifest recorded `maxWristError = 0.00001465487502633233` px, 48 unique images, and stable replay.

## Real bugs discovered and fixed

- Original Spine-Pixi v8 bone `worldY` conversion inverted the coordinate sign, producing a 630px apparent shoulder error. Corrected it without relaxing 0.1px threshold.
- Prop originally placed at wrist center, not handle. Added independent `grip_offset`, P4 code and schema handoff support.
- Shifting grip changed wrist destination to an unreachable position (>170px two-link reach). Compiler failed closed; moved the final target to reachable wrist coordinate (302,195), while cup center is (286,195).
- Re-ran P0, P2, P3, P4 browser and Python checks on the final code. All pass.

## Visual review

Opened browser-rendered frames 0/7/11/12/15/25/35/47. Verified:
- actual rig upper and lower arm images rotate with spine bones;
- cup stays in place through reach and transition to grab;
- wrist contacts the handle at grab;
- cup moves with wrist under `carry`, including selected replay frames;
- cup is released at the table edge without a positional jump;
- rendered pose is still stylistically simple and fairly stiff; there are no anticipation/follow-through or hand grasp sprites.

## Missing — not production complete

- Source art is synthetic five-part, with *manual semantic mapping/joints*; this is **not** Genielabs fully automatic 14-part rig validation, AI image generation, multi-angle identities or skinning proof.
- Spine retarget config is **hardcoded** to this bone naming/hierarchy, stage origin (320,480) and a single left arm; generalized animation across different character sizes/pivots requires a rig metadata contract and transform solver.
- `grip_offset` is a constant screen-space translation. Rotated props and grip/socket orientation are unsupported.
- No character root animation, grounded footsteps, collisions, multiple characters/props, scene camera, final script/voice syncing or 28-second production.
- P1 real Windows G-Labs/MAX webhook remains deferred at user request.
- Measured 100% C0/C1 only applies to selected Python core modules. JS renderer, CLI entrypoints and API app routes are not included in the coverage metric; separate browser integration tests validate them.

## Next actual gate

P4.2: parameterized `RigProfile` (bone roles, scale, actor origin, hand socket), retarget a **second separately generated rig** with different body proportions and assert unchanged action JSON produces valid collision-free contact. Only then claim reusable motion beyond the fixed fixture.
