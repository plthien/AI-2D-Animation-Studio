# P4.3 — Fixed-world prop and rotated hand socket: self-review

Date: 2026-10-13. Implemented on the open draft PR #1; **not merged**.

## Scope implemented

- New `studio/world.py`: `WorldProp` contract defines a shared object identity, fixed world-space start/destination coordinates, local grip socket offset, and start/carry/final rotation targets.
- One unchanged `examples/p4_coffee_motion.json` drives the same reach/grab/carry/wait/place sequence for both actual Genielabs Spine rigs; no per-rig action code is authored.
- One unchanged `examples/p4_world_cup.json` defines object center at (270,195) before grab and (286,195) after place, and a local socket (-16,0). The cup rotates 0° → 25° during carry, then 25° → 0° during place.
- `compile_world_motion` uses the actual skeleton and validated `RigProfile`, retaining absolute shared world prop coordinates. It scales only the **initial resting wrist** according to the actor; reach/place endpoints derive from the fixed cup/socket and carry waypoint remains fixed in world coordinates.
- `runtime/spine_contact_scene.mjs` rotates the 2D prop sprite and verifies real Spine hand-bone position + rotated socket on all held frames to 0.001px. World start and end positions are also checked in the browser.
- `scripts/compile_world.py` CLI and `POST /motion/world-retarget` typed API support manual ChatGPT/DeepSeek handoffs, without any LLM API.
- One CI workflow builds two separate five-part rigs using pinned upstream Genielabs, compiles both from identical director/world inputs, checks every-frame constraints, renders two real Spine/PixiJS videos, compares replay hashes and encodes MP4s.

## Verified results

- [P4.3 GitHub Action 38417865054](https://github.com/plthien/AI-2D-Animation-Studio/actions/runs/38417865054): PASS, two genuine Spine/PixiJS renders with 48 unique PNGs per rig and two 2-second MP4s.
- Browser-reported maximum wrist position error: baseline `0.00001465487502633233`px; compact `0.00001462429802530574`px.
- Two rigid arm geometries: baseline upper/lower = 90/80px; compact = 70/65px, both reaching the same cup.
- [Python CI 38418393430](https://github.com/plthien/AI-2D-Animation-Studio/actions/runs/38418393430): 106 tests passed, 457 measured statements and 134 measured branches, 0 missing. This covers only selected first-party Python core modules (not FastAPI entrypoint, JS runtime and vendor).
- Negative/fail-closed tests include unattainable fixed-world targets, invalid reach/grab/place sequence, malformed object identity and a deliberately corrupted placement endpoint.
- Direct visual review on both rigs of frames 0,11,12,19,27,36,47: cup appears stationary through approach, follows the hand and rotates on carry, returns to zero rotation and stays at the shared placement target at frame 47. The arm is rendered from genuine Spine attachments, not an overlaid procedural limb.

## Bugs and corrections

1. Initial trial had the world prop end-point coverage branch untested. Added one targeted simulated bad-release test rather than increasing the test suite broadly; now C0/C1 reaches the configured 100% target.
2. Earlier P4.2 retargeting restaged the cup relative to each rig. The new world mode keeps the cup's initial and final coordinates shared and checks that property numerically and in the browser.
3. Prior static grip offset did not rotate with the prop. P4.3 applies a rotation matrix in the compiler and verifies the same socket transform in the renderer.

## Remaining limits — important

1. Both demos remain synthetic **five-part characters** generated from deterministic sample parts, not complex AI-created full-body multi-limb characters. G-Labs authenticated Windows live generation is still deferred at the user's request.
2. There is **one active actor per video** interacting with the *same world object coordinates*. Two actors do not interact concurrently with one cup; there is no shared ownership/hand-off state machine.
3. The 2D cup rotation is an explicit animation target, not simulated rigid-body dynamics. No collisions, spills, grip hand-sprite changes, tabletop resting physics, occlusion/contact-depth logic, or foot planting.
4. The camera remains fixed at 640×480 and the characters use supported neutral setup arm chains. Scene and camera transformations, full rig retargeting, and arbitrary Spine skeletons are not proven.
5. Render output still looks fairly mechanical, and an exaggerated cup move past the face may be visually awkward. Production-grade acting/timing needs additional creative direction and motion polish.
6. This is not P6's narrated 28-second five-shot film nor P7's new-story asset/motion reuse gate. The application still lacks full automated multi-shot composition and voice/video final assembly.
7. Coverage is 100% **only in the configured Python core measurement scope**; JS/PixiJS, API entrypoint and third-party packages are outside it. Their behavior is checked via real browser/API integration smoke, not universal unit coverage.

## Next gate

P4.4: multiple-actor scene ownership/contact and hand-off, or P5/P6 multi-shot compositor/voice pipeline. Prefer end-to-end production progress rather than expanding synthetic motion demos indefinitely.
