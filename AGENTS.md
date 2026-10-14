# AGENTS.md — AI 2D Animation Studio

> Binding entrypoint for Codex and any coding agent. This repository is the **new** 2D animation project; this pack is **specification only**. Do not mistake a JSON example for executable product code.

## Authority order and contradiction handling

1. Explicit current user instructions (but never silently change a contract).
2. `MASTER_SPEC.md` for product requirements, phase order, algorithms, architecture and expected behaviors.
3. `contracts/schemas/*.schema.json` for precise JSON shape; `contracts/examples/*.json` are illustrative, not semantic proofs.
4. `docs/rules/PROJECT_RULES.md`, `ARCHITECTURE_RULES.md`, `CODING_RULES.md`, `TESTING_RULES.md`, `REVIEW_RULES.md` for development process and guardrails.
5. Relevant `.agents/skills/*/SKILL.md` for implementation procedure, **without overriding** sources 1–4.
6. `README_FOR_CODEX.md` and source-code comments for orientation.

A conflict involving normative layers 2–4 is a **blocker**. Do not choose an interpretation, invent a field, mutate the example to make a test pass, or implement a fallback. Document the exact conflict and submit a targeted specification change with tests before coding that behavior.

## Mandatory pre-implementation protocol

1. Verify target repository is `plthien/AI-2D-Animation-Studio`; baseline must be its `main`. Ignore `feat/p0-p1-foundation` and PR #1 completely: do not inspect, cherry-pick, merge, cite as proof, or copy its files.
2. Read this file, `README_FOR_CODEX.md`, `MASTER_SPEC.md` **including Implementer Appendix A–H**, all five `docs/rules/*.md` files, and relevant schemas/examples.
3. Read the matching skill(s) using `.agents/skills/<name>/SKILL.md`; apply `phase-self-review` on *every* phase.
4. Run `python tools/validate_contract_pack.py` in a Python 3.12 environment with `jsonschema` installed; do not claim PASS without actual output.
5. Confirm pinned YTB source `plthien/ytb-ai-studio@393d0eb5516ac8bb8455f859b79bfc64388b128e`; source files copied only if expressly authorized in §1 of Master Spec. YTB must remain unmodified. Record every transplant in `docs/UPSTREAM_PORT_MANIFEST.md` with original path and SHA.
6. Create a phase-specific feature branch from latest approved base; for P0 use `feat/p0-foundation`. Implement **only the requested phase**, including its specified tests and documentation. Use a distinct PR; never auto-merge.

## Hard project invariants

- Seven-stage order `authoring -> resolver -> generation -> rigging -> director -> motion -> delivery` is fixed.
- External LLM prompt export / JSON import only. **No LLM API/SDK calls** in runtime, backend, CI or hidden services.
- G-Labs is the sole image-generation provider; paid tasks require explicit approval, and uncertain submissions must not be repeated automatically.
- Genielabs is a conceptual reference; never import, vendor, checkout or run its source. No code from the discarded prototype branch.
- Original YTB static-image Scene/Beat asset workflows, Ken Burns render graph, and voice-first scene authoring are excluded.
- Animation engine must compile **general motion from data**, never story-ID branches or fake synthetic fallbacks presented as production output.
- Canonical fixed values: 24 FPS, 1280x720, 48 kHz mono PCM16 (=2000 samples/frame), Spine 4.2 JSON and matching official Spine-Pixi v8 runtime.
- Persist approved immutable assets and hashes; block downstream work when approved upstream authority is invalidated.
- Runtime is loopback-only Windows 10/11 x64 first, with portable Python/JS unit tests.

## Workflow routing (stage / skill)

| Requested scope | Required skill |
|---|---|
| P0 port YTB foundation / UI | `ytb-source-port` |
| P1 external Idea/Script/Shot Plan; P6 Director | `external-authoring` |
| P2 asset registry/resolver | `asset-resolution` |
| P3 G-Labs | `glabs-integration` |
| P4 native auto-rig | `native-auto-rig` |
| P5 motion/world, P7 integration | `motion-engine` |
| P7 Spine rendering | `spine-renderer` |
| P8–P9 voice/final export | `voice-video-assembly` |
| All phases P0–P11 | `phase-self-review` |

When phase crosses boundaries, read *both* owning skills, preserve single-writer ownership of artifacts and avoid circular imports.

## Definition of done per phase

- All phase files/behaviors described in `MASTER_SPEC.md` implement exactly; OpenAPI, persistence, schemas and UI remain consistent.
- New and affected tests run and have recorded commands, versions, pass/fail totals. No masked failures or fabricated CI outcomes.
- Negative/error, cancellation, concurrency and stale-lineage paths are included when the phase introduces them.
- Independent self-review report records traceability (requirement -> file -> test), deviations and unresolved blockers. A phase lacking any mandatory acceptance test is **not complete**.
- Open a PR for review but do **not** merge unless user explicitly requests it. Do not continue to next phase without appropriate approval/branch policy.
