# CODING RULES — Agent-implementable engineering standards

## Base conventions

- Python **3.12**; type all public functions, use `from __future__ import annotations`, Pydantic v2 DTOs, explicit return values and bounded I/O. React **18** + TypeScript strict and functional components; Node **22**; respect pinned, lockfile-resolved versions in Master Spec.
- No wildcard imports, undocumented dynamic attribute access, `eval`, untrusted pickle, shell-interpolated subprocess commands, global mutable project state or unbounded concurrency. No placeholder `pass`/TODO silently treated as supported capabilities.
- No new dependencies unless approved by phase scope, pinned with lockfiles, explained and CI tested. Local tests must run offline with fake provider interfaces.

## API/contracts/persistence

- One schema version per product domain in MVP. JSON Schema Draft 2020-12 and strict Pydantic (`extra='forbid'`) must agree on fields, ranges, enums and nullability.
- Validation order: syntactic parse (duplicate keys fail), JSON Schema, semantic check, upstream lineage/hash, capability feasibility, explicit approval, then publication.
- API errors use `{code,message,details,retryable}` with stable machine-readable error codes, proper HTTP 4xx for invalid client state and 5xx for internal faults; never leak paths, tokens, prompts or provider credentials.
- Financial/provider requests: durable attempt and ownership fencing before network call; submission/poll/download external I/O outside SQLite write transaction; ambiguous POST status is preserved, never automatically resubmitted.
- Database is new SQLite schema, WAL and Alembic from revision 0001; no legacy YTB or prototype migrations/backfills. Use compare-and-set publication and immutable artifact byte hashes. Do not use object mutation in place to fake immutable versions.
- Accept filenames/media only after path-traversal guards, MIME/content sniff, length/pixel limits and asset SHA validation.

## Temporal/geometry engineering

- Frame indices are **0-based integers**; action intervals half-open `[start_frame,end_frame)`, exact 24 FPS. End frame is excluded. Never accumulate floats to count frames.
- Local/world Cartesian x right/y up; render conversion from `MASTER_SPEC.md` §10.2; do not mix screen y-down with rig y-up without an explicit named conversion function.
- Deterministic evaluator `pose(shot_id, frame)` must be idempotent and independent of earlier render calls. No runtime `Date.now`, `Math.random`, wall-clock tweens or mutable previous-frame dependencies.
- Bone setup/camera/sockets/IK use finite numbers only. Clamp or reject only when spec authorizes it, never silently guess. Avoid disabling QC to pass demo.
- All contact constraints verify true Spine world-space grip position, not merely the requested IK target, and fail/flag explicitly on deviation.

## Software safety

- Run local processes with argument arrays and bounded timeouts; redact secrets; implement cancellation and process cleanup. Keep backend on `127.0.0.1`. No broad CORS `*` for authenticated origin/cookie flows.
- Strict path separation for project IDs, approved asset versions and staging outputs. Provider/network failures and interrupted renders must leave previous approved artifacts untouched.
- Keep portability between Windows batch launcher and Linux tests; no shell assumptions in Python application code.

## Review traceability

Every changed behavior requires a test; report exact reproducible commands and outcomes; do not declare the phase complete on lint-only or schema-only success.


## Animation schema contract refinements (v1.2)

- Only `channel_dna.v2` is supported; do not resurrect `channel_dna.v1` adapters. Follow 7-field visual identity, entity styles and bounded acting metadata.
- `animation_plan.shots[].performance` is required, typed, versioned, and must exactly match current ChannelDNA defaults in MVP; no free-form motion/gesture inference.
- Preserve approved metadata and SHA for both generated character reference and parts atlas. `parts_manifest` references both original image artifact IDs.
- `compiled_film` core semantic bone roles number 16; serialized bones are between 16 and 64 distinct approved rig bones. Validate all names against actual skeleton.
- For silent visual shots: zero-length script range, explicit shot purpose, no VoiceCue, exact silence injected only in final audio assembly.
- `rig_manifest.v1` is sole rig publication name; effect asset is unsupported until explicitly versioned.
