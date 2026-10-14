# P1 — External Idea / Script / Shot Plan authoring
**Prerequisite:** approved P0. **Owning skill:** `external-authoring`. **Canonical shapes:** `topic_ideas.v1`, `script.v1`, `shot_plan.v1`, `channel_dna.v2`.

## Work orders and exact files

**P1.01 Port safe authoring primitives.** Copy/adapt `app/core/external_authoring.py`, `app/services/external_authoring_reservations.py`, `app/modules/platform/contracts.py`, relevant `app/api/external_authoring_schemas.py` from pinned YTB. Implement `app/modules/authoring/{prompts,external_import,invalidation,shot_plan}.py`, `app/modules/platform/{topic_ideas,script}.py`, `app/repositories/authoring.py`, `app/api/routes/authoring.py`, `app/api/schemas/authoring.py`. Any YTB voice-first scene dependency is forbidden.

**P1.02 Prompt files.** Create `contracts/prompts/{topic_ideas,script,shot_plan}/{system,user,output_contract}.md`. `PromptService.build(project_id,stage,user_instruction)->PromptPackage` snapshots approved ChannelDNA, current selected Topic/Script as applicable, schema bundled without remote `$ref`, creates exact reserved `art_<uuidhex>`, `source_hash=sha256(canonical_json({stage,project_id,stage_inputs,visual_hash,performance_hash,narration_hash,prompt_template_hash}))`. Persist immutable prompt text and single pending reservation; returning existing pending prompt does NOT allocate another ID. Rebuild explicitly consumes/invalidates prior reservation.

**P1.03 Strict import.** `validate_import(project_id,stage,result_json)->ValidationResult` applies max 10 MiB, UTF8, duplicate-key rejection, Draft2020-12 schema, reserved artifact/project/source hash match and semantic cross-checks, WITHOUT write. `import_result` reruns same validation inside its own publication transaction and publishes a draft artifact; consume reservation once, CAS guarded. Same source snapshot changing after prompt build returns `EXTERNAL_SOURCE_STALE`, not auto-rewritten. Approval is a separate request with expected prior head ID.

**P1.04 Script rules.** Section IDs unique and stable; `full_narration` equals `"\n\n".join(section.narration_text for section in sections)` byte-for-byte after JSON decoding. Never auto-normalize/punctuate spoken text. Script is narrated MVP, no character dialogue as distinct timed speakers. Story intent informs Shot Plan prompt but never executes as code.

**P1.05 Shot plan rules.** Each `shot_id` and `order` unique, contiguous one-based order; each actor ID sticks to one character key across film; each prop ID sticks to one semantic prop key; 1..2 actors per shot, 0..3 props. All voiced shots `shot_purpose=story_action`, `section_end>section_start`, exact substring of referenced Script section; silent `visual_reaction|establishing` with `section_start=section_end` and `narration_text=""`. Voiced spans consume Script text in sequence with no gaps/overlaps; silent spans do not advance cursor. Every story action actor/target exists in shot; classify target field required/null rules from Master §5.2. Duration integer 24..720; no floating seconds accepted. Explicit camera zoom finite and positive; continuity does not teleport ownership.

**P1.06 UI.** `src/features/studio/{TopicPanel,ScriptPanel,ShotPlanPanel,ExternalPromptWorkspace}.tsx`; reuse YTB `PromptImportWorkspace` only after removing static video assumptions. Buttons Build/Rebuild/Copy/Upload/Validate/Import/Approve; `Rebuild` warns old reserved ID invalidated; inline JSON paths with error codes. Refresh restores pending prompt. No LLM API settings or calls.

## API routes and responses

All routes under `/api/v1`: `GET/POST /projects/{id}/authoring/{stage}/prompt`, `POST /projects/{id}/authoring/{stage}/validate`, `POST /projects/{id}/authoring/{stage}/import`, `POST /projects/{id}/artifacts/{artifact_id}/approve`, `GET /projects/{id}/shot-plan`; `{stage}` is one of `topic_ideas|script|shot_plan`, anything else 404. Package fields `{artifact_id,source_hash,prompt_text,stage}`; validate response `{valid,errors:[{path,code,message}],source_hash}`. HTTP 413 oversized, 422 schema/semantic, 409 stale/reservation conflict, 404 foreign artifact.

## Tests and acceptance

`tests/authoring/test_reservations.py`, `test_script_integrity.py`, `test_shot_plan_semantics.py`, `test_prompt_bundle.py`, `tests/api/test_authoring.py`, UI tests. Include duplicate JSON key; missing/additional field; stale hash; replay after import; two simultaneous imports; cross-project reserved ID; script exact-text changed by one apostrophe; silent shot valid, silent but nonzero span rejected, voiced but empty text rejected; duplicate actor ID binding; camera zoom 0; invalid actor target; order 1,3 gap. **Exit:** run full topic→script→shot JSON copy/import/approval offline with app network disallowing all LLM calls; no voice and no images generated.

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
