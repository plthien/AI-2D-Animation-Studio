# CODEX EXECUTION PACK v1.1 — Read this first

This repository root contains **specifications and implementation policy only**, not finished 2D production code. Root `AGENTS.md` is the coding-agent entrypoint.

## Mandatory order

1. Read `AGENTS.md` entirely.
2. Read `MASTER_SPEC.md` **entirely** (including Implementer Appendices A–H).
3. Read all five `docs/rules/*.md` documents.
4. Read `contracts/schemas/*.schema.json` and `contracts/examples/*.json` (19 shape contracts + 19 structurally valid examples).
5. Read phase-relevant `.agents/skills/<skill-name>/SKILL.md`; always apply `.agents/skills/phase-self-review/SKILL.md`.
6. Run `python tools/validate_contract_pack.py`; interpreter must have `jsonschema` available. Do not infer PASS from report of previous run.
7. Follow `MASTER_SPEC.md` Appendix F for execution prompt, starting **P0 ONLY** unless user explicitly changes the phase.

## Frozen repositories

- Target: `plthien/AI-2D-Animation-Studio`, branch `main` at freeze `d45528635442512e21dd276baf3a3b721150811e` (then only README). **Never use `feat/p0-p1-foundation`, PR #1 or contents of that discarded implementation.**
- Source for authorized neutral transplant: `plthien/ytb-ai-studio` at `393d0eb5516ac8bb8455f859b79bfc64388b128e`.
- Genielabs source is prohibited; techniques may be studied conceptually; the target implements its own native rig engine.

## Interpretation

The schemas determine exact shape; Master Spec supplies semantics; rules govern agent process and quality; skills provide phase-specific procedure. Do not silently resolve contradictions. JSON schema checks prove only structure, not real motion, Windows provider integration or visual quality.

## Contents

`AGENTS.md`, `MASTER_SPEC.md`, `README_FOR_CODEX.md`, `docs/rules/` (5 documents), `.agents/skills/` (9 skills), `contracts/schemas/` (19 documents), `contracts/examples/` (19 examples), `tools/validate_contract_pack.py`, generated `PACKAGE_MANIFEST.json` and `CONTRACT_VALIDATION_REPORT.md`.
