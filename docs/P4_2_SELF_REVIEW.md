# P4.2 — Two-rig motion retargeting: evidence-based self-review

Date: 2026-10-13. All checks below were run against commit `f032bdb95f24a99958643e7668f68d17f8ce92be` before this documentation commit.

## Acceptance results

| Gate | Result | Evidence |
|---|---|---|
| Same authored action JSON reused unchanged on both rigs | PASS | `examples/p4_coffee_motion.json` → `compile_retarget.py` per RigProfile |
| Real Genielabs skeleton/atlas created separately for two variants | PASS | [GitHub CI P4.2 38407752108](https://github.com/plthien/AI-2D-Animation-Studio/actions/runs/38407752108) |
| Distinct arm geometry | PASS | baseline upper/lower = 90/80px, compact = 70/65px; shoulders at (140,165) vs (175,185) |
| Same normalized hand path after rescale | PASS | per-frame CI position assertion tolerance 1e-8 |
| Spine rendered 48 frames for each rig, real wrist contact verified | PASS | baseline max wrist error ~0.000014655px; compact max wrist error ~0.000012947px |
| Scene replay stable for both variants | PASS | 48 unique frame images each; SHA-256 checks on milestones |
| MP4 for each variant | PASS | two independent 2s, 640×480 H.264 MP4 artifacts |
| Python UT C0 / C1 | PASS (measured core scope) | [38407752259](https://github.com/plthien/AI-2D-Animation-Studio/actions/runs/38407752259): 99 tests; 394 statements / 118 branches, 0 missing |
| Existing P0/P2/P3/P4 regression workflows | PASS | all seven workflows green at the tested commit |

## Code implementation

- `studio/retarget.py` defines a strict `RigProfile` (Spine bone roles, rest pose, actual segment lengths, stage origin and grip socket).
- `validate_spine_profile` verifies bones exist, hierarchy, joint offsets, length match and neutral setup rotations/scales. Unsupported geometry fails closed.
- `retarget_motion` scales trajectories **about the character shoulder** by total arm reach and preserves the original prop's physical grip offset in screen pixels.
- `compile_retargeted` preserves the input chronology/action names and delegates per-frame pose/contact and reach limits to the existing motion compiler.
- `scripts/compile_retarget.py` creates a compiled timeline from original action JSON, a rig profile and the actual Spine skeleton.
- The runtime reads its named bone roles and stage origin from the profile rather than hardcoding character-specific code.
- `POST /motion/retarget` accepts the typed plan, validated rig profile and skeleton JSON. The user can still use manual ChatGPT/DeepSeek handoff without invoking an AI API.
- Pinned upstream Genielabs tools build two separate five-part rig/atlas files via `scripts/p4_spine_fixture.py --variant baseline|compact`. The browser loads each and measures actual wrist, elbow and shoulder per frame, rather than showing a fake arm.

## Self-review findings

### Confirmed positive

Both actual browser videos have been opened and visually compared at frames 0,11,14,25,47. The shorter rig has a visibly shorter forearm/upper arm; both perform reach → grab → carry → place with no prop discontinuity at grab/release. At frame 47 the cup sits against the same table, at a restaged position appropriate to the second rig.

### Limitations and next gates

1. **Actor-local reuse, not fixed-world contacts.** The cup's start and placement target are transformed along with the rig. Two differently sized actors have not been proven to grab a single stationary world-space cup.
2. **Only two synthetic 5-part rigs.** No real G-Labs character / 14-part automatically detected body, left/right multiple arms, arbitrary bone naming, deform/mesh, or multi-angle reference.
3. Bone profiles currently require a straight neutral setup chain, local lower/hand joint offsets on +X, stage scale = 1 and a fixed upper-body pose; runtime must not claim universal Spine support.
4. The `RigProfile` field `actor_origin` is parameterized but both current CI rigs use origin (320,480); retarget with transformed camera / origin is not independently demonstrated yet.
5. Grip socket is a fixed 2D screen translation; if prop/hand rotates, socket should use rotated local coordinates.
6. No event-driven director timeline compiler covering multiple shots, no voice synchronization, full-humanoid foot planting or collision avoidance.
7. 100% Python C0/C1 measured scope excludes FastAPI entrypoint, JS renderer and third-party modules. Browser checks and API smoke are independent of that figure.
8. G-Labs Webhook real MAX/Windows image-generation test remains explicitly deferred by user.

## Next recommended gate

P4.3 world-space prop contact + a portable hand-contact socket that follows prop rotation. For broader character animation, next prepare a full-body multi-limb rig and validate both-hand reach without manually reauthoring motion code.
