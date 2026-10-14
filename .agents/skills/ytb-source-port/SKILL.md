---
name: ytb-source-port
description: Port neutral YTB foundation for P0 and selected shared platform changes. Use for source provenance, database/UI skeleton and contract-first adaptations.
---

# Skill — ytb-source-port

## Required source and target

Read `MASTER_SPEC.md` §1, §2, §3, §14 and Appendix A P0; `docs/rules/ARCHITECTURE_RULES.md` and `CODING_RULES.md`. Source snapshot: `plthien/ytb-ai-studio@393d0eb5516ac8bb8455f859b79bfc64388b128e`. Target: `plthien/AI-2D-Animation-Studio/main` only.

## Steps

1. Enumerate allowed YTB source files in Master Spec §1 and confirm their exact existence at pinned commit. Record candidate path and SHA in `docs/UPSTREAM_PORT_MANIFEST.md`; do not add from old target prototype.
2. Copy allowed neutral utility/errors/hashing/DB/session/service/UI-shell components; adapt imports and naming with minimal changes. Keep source license/provenance metadata.
3. Design new SQLite Alembic revision 0001 from Master Spec §3.2, no old YTB migrations. Implement explicit artifact role schema and Channel DNA identity.
4. Build new FastAPI app entrypoint and React shell with the fixed seven stages, but only P0 pages/operations actionable. Incomplete later stages display `Not implemented` and are not marked Ready.
5. Pin and verify Python 3.12, Node 22, React/Vite dependencies, Windows `.venv`, `setup.bat`, `start.bat` and CI.
6. Test app health, CRUD, new DB migration, startup restart, artifact versioning/CAS and frontend build. Record precise test outputs.

## STOP / acceptance

P0 ends without imported Scene Asset, voice-first, Ken Burns or YTB old routes. Do not implement future stage logic or report their status as complete. Complete phase audit per `phase-self-review`.
