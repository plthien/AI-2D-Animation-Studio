# P3 — G-Labs visual generation and approval
**Prerequisite:** approved P2. **Owning skill:** `glabs-integration`. **Schemas:** `generation_request.v1`, `asset_version.v1`, `parts_manifest.v1` lineage. **No AI chat API**.

## Work orders

**P3.01 Transport transplant.** Adapt only `app/modules/media/{glabs_webhook_client,bounded_http_transport,transport_policy,image_upload_validation,media_secret_safety,media_provider_errors}.py` and neutral `durable_workflow/*` from pinned YTB. Create `app/modules/assets/{glabs_prompt_compiler,generation,qc}.py`, media operation adapter using existing `operations/operation_tasks`, `src/features/assets/GenerationPanel.tsx`; isolated `tests/assets/test_glabs_*.py`.

**P3.02 Request compiler.** `compile_generation_request(channel_dna,requirement,generation_kind,reference_artifact_id,model)->generation_request.v1`. Only allowed kinds `character_reference,character_parts_atlas,background,prop,expression_sheet`; only `nano_banana_2` (default) or `nano_banana_pro`; candidate count exactly one. G-Labs prompt includes exactly current approved visual identity/entity style/negative constraints and explicit output geometry, not animation style or WPM. For derivative `character_parts_atlas` and `expression_sheet`, require non-null approved `character_reference` of same channel/asset lineage; cross-source request => `ASSET_ATLAS_SOURCE_MISMATCH`. For `background` use base 16:9 target 1280x720; `prop` and parts atlas must have true usable alpha after QC.

**P3.03 Paid submission FSM.** `GenerationService.submit(project_id,request,idempotency_key,confirmed_by_user)->Operation`: require `confirm_spend=true`, credential present, explicit live UI click; pre-persist operation state `queued` and unique task `unit_key`, include source hashes and signed request fingerprint, then perform HTTP POST **outside transaction**. Accepted response stores provider task ID; polling is background host-owned, never GET side effect. When POST acceptance unknown, status `ambiguous_submission`, error `MEDIA_SUBMISSION_AMBIGUOUS`, no auto retry and no second paid task until manual provider reconciliation. Add guarded cancellation; network and read/write ownership fencing.

**P3.04 Download verification and QC.** Restrict host to configured loopback webhook and result URL to verified same-origin/local policy; reject redirected private/public cross-host responses, excessive bytes >25MiB, image bombs >32MP, mismatched mime and file decoding, non-image bytes and unsafe filesystem paths. Download to unique attempt path, verify SHA/format/dimensions, emit `asset_version` `needs_review`. RGBA alpha test: image must have meaningful transparent background for `prop`/`character_parts_atlas`; if not, block `IMAGE_ALPHA_REQUIRED`, permit explicit manual matte removal and separate approved derivative artifact (not silent transparency fabrication). User review approval pins exact image/version SHA.

**P3.05 UI/API.** `POST /projects/{id}/assets/{asset_id}/generate`, `GET /operations/{op_id}`, `POST /operations/{op_id}/cancel`, `POST /projects/{id}/assets/import`, `POST /channels/{id}/asset-versions/{version_id}/approve`. Generate UI shows prompt, model, aspect ratio, reference SHA, estimated provider action, confirmation; refresh/restart resumes task projection, no status resets. Provider errors show recoverable instructions.

## Provider/test gate

Fake transport must simulate 202 pending, complete PNG, 4xx, 5xx, redirect, corrupt upload, oversized image, duplicate idempotency click, ambiguous accepted POST then process death, stale worker token, cancel before/after submit and restart. Verify retry only when safe proof of no prior submit. `/health` and `/status` never trigger paid generation. Live Windows G-Labs roundtrip is a **separate user-credential gate**; absent real token mark `NOT_RUN`, never fake PASS. No in-repo paid generated images. **Exit:** approved image assets with stable provenance, alpha review, no duplicate-charge risk.

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
