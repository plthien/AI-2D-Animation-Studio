# P6 — External AI Animation Director JSON workflow
**Prerequisite:** approved P5 motion capabilities and P4 rigs. **Owning skills:** `external-authoring`,`motion-engine`. **Schema:** `animation_plan.v1`, source `shot_plan.v1`, `asset_resolution.v1`, `rig_profile.v1`, `channel_dna.v2`.

## Work orders

**P6.01 Source freeze.** Create `app/modules/director/{prompt_builder,import_validator}.py`, `app/api/routes/director.py`, `app/api/schemas/director.py`, `contracts/prompts/animation_director/{system,user,output_contract}.md`, `src/features/animation/AnimationDirectorPanel.tsx`, `tests/director/*`. `DirectorPromptBuilder.build(project,optional_instruction)` freezes exact `{approved_shot_plan_artifact_id,shot_sha,asset_resolution_artifact_id,resolution_sha,rig_ids+sha,motion_library_revision,performance_style_hash,template_sha}` and reserves one artifact ID and source hash. Store pending prompt via P1 reservation engine and restore on refresh.

**P6.02 Prompt input.** Package complete structured ShotPlan actor/prop lists, start world/camera state, approved action catalog and RigProfile capabilities, grip sockets, action timing `[start,end)` and exactly one `shots[].performance` snapshot per shot derived from approved `animation_identity`. No API call to ChatGPT/DeepSeek; user copies prompt externally and imports JSON. Never ask model to supply arbitrary bone transforms or code.

**P6.03 Semantic validation.** `DirectorValidator.validate(result,freeze,rig_catalog,world)->ValidationResult`: schema (required fields/no unknown), unique action IDs globally, exact shot set/duration, action actor exists and rig view compatible, rig `supported_actions` superset, exact kind-track-param union, limits, no track/hand conflict, all referenced props present, `grab` after valid reach with contact possibility, no ownership collisions, camera keyframes sorted/in-range, performance snapshot equal to frozen values. Wrong performance => `DIRECTOR_PERFORMANCE_SOURCE_MISMATCH`; stale any upstream hash => `DIRECTOR_SOURCE_STALE`; unknown action => `ANIMATION_ACTION_UNSUPPORTED`; unknown actor/rig/prop path in `details`. No fallback action substitution.

**P6.04 Publication & UI.** `POST /api/v1/projects/{id}/director/{prompt,validate,import,approve}` and read-only GET pending prompt as same pattern as P1. Validation cannot generate motion/commit changes. Import revalidates and publishes draft `animation_plan`, approval CAS-publishes. Changing DNA performance only invalidates Director/Motion, never physical image/rig unless visual hash changed. UI shows disabled compile before approval and action table with frame ranges/track/targets; select error highlights exact JSON path.

## Tests and DoD

`test_director_schema.py`: unknown enum, unwanted `run` action, absent performance, mismatch source. `test_director_semantics.py`: duplicate action ID, `[9,9)`, out-of-shot, invalid prop, left/right grip mismatch, two same-track overlapping, walk+look allowed, walked actor outside camera, 2 actors same rig allowed, rig lacking `react` blocks. `test_director_reservations.py`: replay/stale/foreign. UI mock no network LLM. **Exit:** imported JSON becomes reviewed executable request, never direct arbitrary JS/Python or unverified auto-play.

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
