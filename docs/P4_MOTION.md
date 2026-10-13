# P4 — Two-bone IK and object-contact proof

The command below compiles a **standalone** manual-director JSON file into deterministic per-frame poses. No LLM/Gemini APIs are involved.

```powershell
python scripts/compile_motion.py examples/p4_coffee_motion.json runtime/fixtures/contact_frames.json
cd runtime
npm install
npx playwright install chromium
npx esbuild contact_scene.mjs --bundle --format=esm --outfile=contact_scene.bundle.js
cd ..
node runtime/contact_render.mjs
ffmpeg -framerate 24 -i outputs/p4/frames/frame_%06d.png -c:v libx264 -pix_fmt yuv420p outputs/p4/p4_coffee_contact.mp4
```

## Contract

- Motion JSON: `MotionPlan` in `studio/motion.py`; action types: `reach`, `grab`, `carry`, `wait`, `place`.
- Coordinates are absolute screen pixels with y positive downward; one fixed shoulder, one wrist, one target prop.
- 2-link analytic IK: a target outside reachable workspace fails; there is no silent clipping.
- Grab must start with the free prop already at wrist (tolerance 1 px).
- Carry and place require held prop; no reach while holding; cannot finish shot with prop held.
- During held frames the prop center is **exactly** the hand center, not an independently interpolated path.
- JSON timeline must cover every frame once, with no gaps/overlaps.

## Evidence and limitations

GitHub workflow `P4 IK prop-contact video smoke` compiles the example, checks bone lengths/contact on every frame, replays selected frames to verify pixel hashes and creates a **2-second 640x480 MP4**.

**This is a diagnostic procedural puppet, not yet a Genielabs/Spine bone-retargeted rig.** Spine bone adaptation, actor movement/rotation, second actor, inverse contact offsets (grip point vs prop center), grounding/foot planting and collision avoidance remain P4 backlog. The clip is a functional test, not publishable video.
