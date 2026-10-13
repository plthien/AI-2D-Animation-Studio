# P4.2 — Retarget one motion file onto two Genielabs Spine rigs

P4.2 introduces `RigProfile` and a `compile_retarget.py` CLI. Profiles are validated against the **actual** Spine JSON bone roles, hierarchy and nonzero arm lengths.

A baseline synthetic rig uses 90px upper / 80px lower arm, shoulder (140,165). A second independently built synthetic **compact rig** uses 70px upper / 65px lower arm, shoulder (175,185). Both are created by the same pinned upstream Genielabs builder and atlas packer. Each loads its own JSON, atlas and textures in the official Spine/PixiJS 8 runtime.

The original file `examples/p4_coffee_motion.json` is **unchanged**, and both compiled outputs come from it with two different `rig_profile.json` files. Nobody writes variant-specific animation code.

### Algorithm (explicit limitation)

Retargeting is **actor-local, proportional path remapping**:

```
scale = (target_upper + target_forearm) / (source_upper + source_forearm)
target_hand = target_shoulder + scale * (source_hand - source_shoulder)
target_prop_initial = transform(source_prop_initial - source_grip_offset) + target_grip_offset
```

This retains relative movement and exact prop contact for **a prop restaged along with the actor**; it does not preserve a fixed world-location cup if the actor moves. A second rig with pathological upper/lower arm ratios is rejected by IK instead of silently stretching bones.

Both rigs are validated by Chromium (every frame checks actual Spine shoulder, elbow, wrist and wrist-plus-socket contact). All 48 PNG frames are replay-checked at selected milestones and FFmpeg emits a 2-second MP4 for each rig.

### Remaining hard gates

No 14-part AI character or arbitrary right-arm bone layouts yet. P4.2 currently assumes a straight setup arm chain (lower bone x = upper arm length, wrist bone x = forearm length, local y=0). Shoulder positions and scene origins are explicitly authored in `RigProfile` and verified by the browser rather than auto-discovered. No motion from camera, body turn, walk/foot planting, multiple objects or rotated contact socket. G-Labs live image test remains intentionally deferred.
