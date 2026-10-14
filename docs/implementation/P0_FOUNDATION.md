# P0 — Standalone platform foundation
**Prerequisites:** specification-only main at the current approved revision. **Owning skill:** `.agents/skills/ytb-source-port/SKILL.md`. **Outcome:** independent startup, real local DB, channels/projects/jobs/artifacts, 7-stage UI shell, no old storyboard engine.

## Task execution order and file ownership

**P0.01 Dependency lock & bootstrap.** Create `requirements.txt`, `package.json`, `package-lock.json`, `tsconfig.json`, `vite.config.ts`, `index.html`, `.env.example`, `setup.bat`, `start.bat`, `app/__init__.py`, `src/main.tsx`. Start from pinned YTB dependency versions, with the security-reviewed Vite 6.4.3 exception recorded in the upstream port manifest. Default `DATABASE_URL=sqlite:///./ai_2d_animation_studio.db`, `ARTIFACT_ROOT=./local_artifacts`, host `127.0.0.1`, backend port `8000`, Vite port `5173`. Make batch files quote paths containing spaces; check Python 3.12, Node 22, npm, FFmpeg readiness; do not download G-Labs/Spine or generate video. `.env` and local data excluded via `.gitignore`.

**P0.02 Core transplant.** Port `app/api/errors.py`, `app/core/{config,ids,hashing,time,version}.py`, `app/db/{__init__,base,session,dependencies,types,sqlite_pragmas}.py`, `app/infrastructure/sqlite.py` and neutral artifact/job functions allowed by Master §1. Create `app/repositories/{artifacts,projects}.py`, `app/services/{artifacts,jobs}.py`. Preserve source-provenance manifest at `docs/UPSTREAM_PORT_MANIFEST.md`: `{source_path,source_sha256,target_path,mode:COPIED|REWRITTEN,removed_dependencies,tests}`. Where a YTB file imports banned Scene/Beat modules rewrite the needed neutral function, never transitively port banned files.

**P0.03 New schema.** Create `app/db/models.py`, `migrations/env.py`, `migrations/versions/0001_initial.py` for the **14 tables** listed in Master §3.2: channels, projects, project_stage_heads, artifacts, authoring_reservations, assets, asset_versions, project_asset_bindings, rigs, rig_versions, motion_templates, operations, operation_tasks, jobs (all fourteen tables are required). Empty but real tables for later phases are allowed. `channels.dna_json` must validate `channel_dna.v2`, never YTB v3. UUID-hex prefixed IDs are generated server-side. Timestamps UTC ISO8601. SQLite FK ON and WAL in connections; CAS pointer replacement performed transactionally. Do not copy upstream Alembic revisions.

**P0.04 Platform application.** Create `app/main.py` with lifespan/migration startup, `app/api/routes/{system,channels,projects,jobs,artifacts}.py`, `app/api/schemas/base.py`, `app/modules/platform/{channels,projects}.py`. Route `/health` returns `{data:{status:"ok",schema_version:"1"}}`; add `/api/v1/channels` GET/POST, `/api/v1/projects` GET/POST, `/api/v1/projects/{id}`, `/api/v1/projects/{id}/artifacts` GET, `/api/v1/jobs` GET, `/api/v1/jobs/{id}` GET, keeping exact §12 projection fields. ChannelDNA create/update validates against bundled schema and computes identity hashes. `PUT /api/v1/channels/{id}/dna` requires `expected_current_artifact_id`: explicit `null` creates the first revision and an exact current `art_<32hex>` replaces it; stale/null mismatch returns 409 `CHANNEL_DNA_STALE_REVISION` with the current artifact ID. Invalid schema returns 422 and missing channel returns 404. Current phase must not silently invent downstream stage-ready artifacts.

**P0.05 Frontend.** Port YTB `src/layout/*`, `src/components/*`, `src/features/{channels,projects}/*` and page shells after dependency cleansing. Create `src/api/client.ts`, `src/pages/{ChannelsPage,ProjectsPage,StudioPage,JobsPage,SettingsPage}.tsx`. `StudioPage` displays seven stage labels in §0.2 in exact order with statuses from backend; P1+ controls disabled and explain blocked status. Client generated/static typing must match FastAPI OpenAPI. No fake successful generate/preview UI.

**P0.06 Isolation.** Add a static-source dependency scanner in `tests/platform/test_no_legacy_imports.py`, scanning active `.py`, `.ts`, `.tsx` imports (not docs) for `scene_asset`, `scene_breakdown`, `beat_timing`, `prompt_composer`, `genielabs`, `feat/p0-p1-foundation`; fail if runtime module imports forbidden code. No imported `app/modules/v4` domain.

## Required API/DB behavior

- Two projects may reference one channel, but artifact heads are project-scoped; foreign project/channel access is 404 or 409, not a leak.
- `ArtifactRepository.publish(staged, expected_head_id)` must: verify same-channel/project; validate full SHA+size; CAS current stage head; commit record and rename owned temp; rollback and delete only attempt-owned temp on conflict. A file that was already published is immutable.
- `ProjectService.create(channel_id,name,description)` initializes all seven visible statuses; `authoring` ready only with approved valid ChannelDNA, rest blocked. `Job` is projection, not execution lease authority.

## Deterministic test matrix and gate

`python -m alembic upgrade head` on a clean **disposable** SQLite path, then inspect names and foreign keys; `python -m pytest tests/platform tests/api -q`; `npm ci && npm run build && npm test`; OpenAPI generation. Tests include: one channel/two projects, rejecting `channel_dna.v1`, distinct style hashes, invalid WPM min>=max, artifact immutable bytes, two concurrent publisher CAS losers, foreign-channel ID denial, bad path traversal, restart persistence, banned imports, UI seven-stage order. `start.bat` smoke test Windows must be reported `NOT_RUN` if no Windows host. **Exit gate:** independent app boots and persists real data; ZERO stage-specific animation success claimed.

## Environment and bootstrap gate

The initial `jsonschema` import error is an **environment prerequisite failure**, not a schema failure: provision `tools/requirements-validation.txt` before running JSON Schema gates. If PyPI or GitHub is unreachable in the Codex sandbox, arrange network access or pre-provision the exact approved upstream source snapshot and Python/npm dependencies. Do not bypass the full phase gates or claim P0 accepted.

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
