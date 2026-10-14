# P5 — Deterministic Motion / World engine
**Prerequisite:** P4 rig profile/fixture approved technically. **Owning skill:** `motion-engine`. **Contracts:** `rig_profile.v1`, `shot_plan.v1`, `asset_resolution.v1`, `compiled_film.v1` snapshot shape (full publishing completed in P7).

## Motion data ownership and work orders

**P5.01 Create** `app/modules/animation/{action_dsl,motion_library,ik,locomotion,interactions,world_state,retarget,compiler,qa}.py`; `app/repositories/motions.py`, `contracts/motion_templates/v1/{idle,walk,look,reach,point,face_swap,hold_prop}.json`, `tests/animation/*`. Motion templates are versioned JSON parameter sets, no Python code per story or actor ID. Motion code must not import browser, provider or HTTP routes.

**P5.02 Action DSL authority.** Runtime action kinds exact `idle,walk_to,look_at,reach_for,grab,carry_to,place_at,point_at,react` with tracks+params from Master §9.2 / `animation_plan.v1`. Define `validate_action(action,rig_profile,world_state,shot_span)->None` with fail-closed error paths: unknown action `ANIMATION_ACTION_UNSUPPORTED`, missing rig capability `RIG_ACTION_INCOMPATIBLE`, invalid `[start,end)` `MOTION_FRAME_RANGE_INVALID`, one actor two upper-body actions on same arm `MOTION_TRACK_CONFLICT`. `walk_to+look_at` legal concurrent; `walk_to+carry_to` legal if hand already owns prop. No fallback replacement.

**P5.03 IK and transformations.** `solve_two_bone(root:Vec2,target:Vec2,L1:float,L2:float,bend_sign:int)->{joint,tip,angles}`. Inputs meters/y-up; reject negative/NaN lengths or targets; reachability `abs(L1-L2)+0.002 <= r <= L1+L2-0.002`, clamp only within 0.002m numerical boundary else `MOTION_TARGET_UNREACHABLE`. Law-of-cosines with `acos(clamp(x,-1,1))`; elbow/knee bend direction fixed from RigProfile. Inverse rest matrices map IK world targets into local setup pose: never assume limbs point along +X. Tolerances: fingertip <=0.005m, held grip <=0.003m, placed end <=0.005m. No hidden teleport to make contact possible.

**P5.04 Gait.** Root linear segment from current x,y to target at y=0. Use 6-frame max acceleration/deceleration smoothstep from Master §10.4. Initial `stride_length=0.32m`, swing height `0.06m`, torso bob `0.02m`, default cadence 12 frames; contact foot fixed in world during stance, re-solve knee IK each frame. Check requested `speed_mps` vs path distance/duration within 20%, reject mismatch rather than time warp. Arm swing ±12° only for unoccupied arms, modulated by approved ChannelDNA energy. Foot slide <=0.01m during stance. Two feet end on y=0 on final frame.

**P5.05 World FSM.** `WorldState(actor_states,prop_states,location_key)` has actor position, rig version, expression, hand holdings; prop current transform and unique owner. `grab` requires same-hand prior `reach_for`, contact <=0.01m at event frame, free prop, then attaches via bone matrix/grip offset. `carry_to` preserves owner/socket; `place_at` releases on `end_frame-1` retaining identical world transform. Allowed prop states `free→grabbed→held→released→free`; explicit event ledger idempotent per frame. Cut cannot implicitly replace owner. Across locations transfer is unsupported. Concurrent actors own separate state even if same rig.

**P5.06 Deterministic evaluator.** `compile_shot_motion(shot,actions,world_in,rig_map,asset_map,style_snapshot)->{frame_snapshots,world_out}`: precompute all frame snapshots from frozen inputs; `state_at(n)` returns stored immutable state irrespective of seek order. Per-frame order exact Master §10.1. Emit all bone names in RigProfile `runtime_bone_names`, finite local transforms and all actor/prop positions plus camera; enforce exact set before publishing. Avoid conditional code keyed by Film A/B or actor semantic name. Add no-voice no-render engineering proof snapshots with deterministic SHA.

## Tests and gate

Analytic IK: right/left/up targets, 2 differently proportioned rigs, both arms/legs, unreachable & near singular boundary, inverse setup matrix with rotated limb; gait stance foot locks for 2+ strides, no slide >1cm; prop pickup/carry/release across shot cut, double-grab, two hands competing, target off-floor, one held prop other hand pointing, walk+look overlap, repeat seek order `0,20,3,20` stable byte hash. Fake spline or single-arm-only paths fail gate. `python -m pytest tests/animation -q` and contract tools. **Exit:** full-body movement and contact solved in numerical world-space proof (P7 supplies browser rendered proof).

## Mandatory phase protocol

1. Start from the latest approved `main`; never read, merge or copy from `feat/p0-p1-foundation` or PR #1. Freeze upstream `ytb-ai-studio` at `393d0eb5516ac8bb8455f859b79bfc64388b128e`. Record every reused function/file and source SHA in `docs/UPSTREAM_PORT_MANIFEST.md`.
2. Read root `AGENTS.md`, the five `docs/rules/*.md`, `MASTER_SPEC.md` including §19 and Appendix A–H, `docs/contracts/ANIMATION_CONTRACT_SEMANTICS.md`, the relevant `.agents/skills/*/SKILL.md`, and the schema+example named in this phase. **Do not** invent fields, API routes, behaviors or defaults.
3. Before editing execute `python tools/validate_contract_pack.py`, `python tools/test_animation_contract_semantics.py`, `python tools/validate_agent_pack.py`, `python tools/validate_implementation_pack.py`. All must pass. Re-run afterwards. Each `validate` route is read-only: it must not update database artifacts, reservations or files.
4. Implement one phase per feature branch/PR; do not merge or auto-start the next phase. APIs for later phases may respond `{error:{code:"NOT_IMPLEMENTED",...}}` only where this phase's explicit integration shell requires a stub; never return mocked success.
5. Publish only immutable validated artifacts with input provenance and compare-and-set stage heads. All external/paid IO is outside SQLite write transactions. Treat all imported JSON, images, paths and provider payloads as untrusted.
6. Run exact phase tests, perform a manual visual gate when required, and record evidence in `docs/qa/PHASE_Pxx_REVIEW.md`. Status values must distinguish `PASS`, `FAIL`, `NOT_RUN`, `BLOCKED`; mock-only or fixture-only tests cannot be called live-provider or production acceptance.

## Shared implementation invariants

- Windows 10/11 x64 local-first, Python 3.12, Node 22, 24 FPS, 1280x720, 48 kHz mono 16-bit PCM = 2000 samples per frame, 1–2 humanoid actors/shot, up to 3 props, <=30 shots, 24..720 frames/shot, world coordinates (x-right,y-up) in meters.
- ChannelDNA `channel_dna.v2`; `visual_style_hash` controls image/rig reuse; `performance_style_hash` controls Director/Motion; `narration_identity_hash` controls authoring/voice. No implicit conversion of creative prose into runtime actions.
- `rig_manifest.v1` is the final rig artifact; 16 required semantic roles, but approved runtime bones can be 16..64 by `rig_profile.runtime_bone_names` exactly. Any unexpected/missing bone is `RIG_BONE_SET_MISMATCH`.
- Rigged animation must be actual Spine 4.2 + compatible Spine-Pixi v8 / PixiJS 8.16+, using exact lockfile versions; not still-image Ken Burns and not Genielabs code. No hidden LLM APIs.
- IDs are backend-reserved; JSON/DB/OpenAPI/TS contract must stay synchronized. Use the error envelope `{"error":{"code":...,"message":...,"retryable":false,"details":{"path":...,"recovery":...}}}`; do not replace unsupported actions with idle.
