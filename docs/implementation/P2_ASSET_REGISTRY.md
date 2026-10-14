# P2 — Global Asset Registry and deterministic resolver
**Prerequisite:** approved P1. **Owning skill:** `asset-resolution`. **Schemas:** `asset_requirements.v1`, `asset_resolution.v1`, `asset_version.v1`, approved `shot_plan.v1`.

## Work orders and code contracts

**P2.01 Physical persistence.** Complete `app/repositories/assets.py`, `app/modules/assets/{registry,requirements,resolver}.py`, `app/api/routes/assets.py`, `app/api/schemas/assets.py`, `src/features/assets/{AssetLibrary,RequirementTable,AssetBindingDialog}.tsx`. Use P0 tables `assets`, `asset_versions`, `project_asset_bindings` and indexed channel filtering; do not create one library per project. `AssetRegistry.create_asset(channel_id,kind,semantic_key,display_name)->Asset` enforces `(channel,kind,semantic_key)` uniqueness and allowed kinds `character|background|prop`; `effect` is rejected `ASSET_KIND_UNSUPPORTED`.

**P2.02 Deterministic requirements.** `RequirementsCompiler.compile(approved_shot_plan,approved_channel_dna)->asset_requirements.v1`; walk shots in order, extract each character `(character,character_key,view)`, background `(background,background_key,base)` and prop `(prop,prop_key,base)`. Deduplicate per `(kind,semantic_key,view)`; `style_hash=visual_style_hash` from DNA; `usage_shot_ids` sorted by shot order, no duplicates. For characters map every attached story action `idle->idle,walk->walk_to,look->look_at,reach->reach_for,grab->grab,carry->carry_to,place->place_at,point->point_at,react->react`, unique and deterministic. For noncharacters `required_actions=[]`. Sort requirements `(kind,semantic_key,view)` lexicographic. `requirement_id = 'req_'+sha256(canonical_json([channel_id,kind,semantic_key,view]).encode()).hexdigest()[:16]`; style hash intentionally NOT part of identity, but must be used for match and invalidation.

**P2.03 Resolver.** `AssetResolver.resolve(project_id,requirements,existing_bindings)->asset_resolution.v1`: (1) verify current approved source revision; (2) load approved candidate versions from same channel; (3) match kind/key/view/visual-style hash byte for byte; (4) for character require approved rig version, exact matching view and `supported_actions` superset of mapped verbs; (5) preserve compatible pinned binding first; otherwise choose newest `approved_at` DESC + `asset_version_id` ASC; (6) label `ready|rig_required|motion_incompatible|generation_required`; (7) emit **one** decision per requirement in canonical order. Do not use embeddings, string-similarity or LLM.

**P2.04 Asset metadata.** `asset_version.v1` binds immutable approved image SHA, dimensions (32..8192), world size meters positive, `grip_socket_px` for props optional until interaction requires it. Backend checks actual file bytes format+dimensions; a null character rig is acceptable before rigging but never status `ready`. New version does not change older project binding. Any manual rebind is a new resolution artifact; do not mutate published bytes.

**P2.05 UI & API.** Implement `POST /projects/{id}/requirements/rebuild`, `GET/POST /projects/{id}/asset-resolution`, `PUT /projects/{id}/bindings/{requirement_id}`, `GET /channels/{id}/assets`, `POST /channels/{id}/assets`, `/channels/{id}/asset-versions/{version_id}/approve` as Master §12 specifies (POST resolution exact suffix `/run`). UI candidate table displays candidate hash, approved date, rig/capabilities and reason codes; no paid generate actions yet.

## Failure and dependency semantics

Visual hash changed -> requirement/reuse decisions stale; performance-only DNA change leaves image/rig approved and unchanged. Wrong channel -> `ASSET_CROSS_CHANNEL_FORBIDDEN`; wrong view -> `ASSET_VIEW_INCOMPATIBLE`; missing rig -> `rig_required`; incompatible actions -> `motion_incompatible`; zero image candidate -> `generation_required`. A previous approved pin gets rejected rather than silently substituted if it becomes incompatible. Resolver MUST NOT call G-Labs.

## Tests and gate

`tests/assets/test_requirement_compiler.py`, `test_resolver.py`, `test_binding_cas.py`, `tests/api/test_assets.py`. Golden fixture with two projects same channel and one rig; verify byte-identical serialized resolution for repeat inputs; changed order of ShotPlan story actions yields same union and hashes; added action alters `required_actions` but stable ID; changing motion energy retains visual compatibility; changing palette invalidates reuse; reject foreign-channel and bogus approved states. Run base tests/UI build and inspect DB FKs. **Exit:** Asset Resolver determines precisely what can be reused, generated or rigged without provider calls.

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
