# TESTING RULES — Verification hierarchy and mandatory gates

## Before any implementation

Run `python tools/validate_contract_pack.py` with Python 3.12 + `jsonschema`; check that all 19 schema/examples and cross-artifact assertions pass. A passing contract script says nothing about runtime behavior.

## Every PR

- Test positive, negative, boundary and stale-lineage cases for each changed API. For imports: duplicates, extra keys, wrong schema, wrong upstream revision, approval/rebuild race, replay of consumed reservation.
- For G-Labs: mocked safe roundtrip, backend-only secrets, network timeout, ambiguous paid POST, retry fence, invalid image/URL, dedupe and explicit approval.
- For assets/rig: deterministic alpha segmentation fixtures (disconnected/dangling/overlap), insufficient feature matches, pivot out of bounds, corrupt atlas, missing semantic role, mismatched Spine 4.2, actual browser load and visual pose samples.
- For motion: two actors, all 9 action names, half-open frame scheduling, unreachable IK, foot slip, prop continuity, double-grab, unsupported action, world/camera invariance and exact deterministic replay.
- For render: project isolation, no stale frames, full frame count, repeatable frame hashes, kill/cancel/restart safety, FFmpeg/ffprobe structural truth.
- For voice: canonical 48kHz mono PCM16, 2000 samples per 24 FPS frame, duration overflow, alignment authority, bounded retime, preservation of contact events, no fake tone accepted as narration.

## CI environments

- Linux Python/JS unit and integration CI on every PR. Run lint, type checks, `pytest`, `npm ci && npm run build`, contracts check and static code/domain checks.
- Browser-backed Spine/Pixi test must actually render changed frames; frozen mock screenshots do not prove Spine compatibility.
- Windows 10/11 user-run setup+live-provider acceptance cannot be replaced by Linux CI. Record explicit pending gates when actual paid-provider access is unavailable.

## P11 full acceptance

- Two fixed films from Master Spec Appendix B and G: Film A and independent Film B using the same engine, rig, character identity and motion library. Both must run with real character G-Labs assets; synthetic sample passes are only technology smoke tests.
- Verify 24 FPS/1280x720 H.264/AAC and 48kHz timeline, audio peak/clipping metrics, actual narration and continuity. Capture sampled video frames and compare to approved visual checklist.
- NO green quality gate by suppressing missing actions, missing voice, wrong asset versions, contact errors or failed real-provider test.

## Evidence

`docs/qa/PHASE_Pxx_REVIEW.md` must include environment, commands, stdout/pass/fail totals, CI run links, screenshots/artifact paths, limitation list and phase verdict PASS/BLOCKED/NOT_RUN. Never invent run evidence.


## v1.2 contract regression gates

Before implementation and every PR run `python tools/test_animation_contract_semantics.py` in addition to the existing schema checker. Tests must reject old ChannelDNA v1, missing performance, corrupt reference/atlas lineage, invalid silent quote windows, effect asset kind, >64 bone arrays and invalid generation references. Tests must also accept a valid zero-length silent visual shot, an approved extra bone, and distinctly hashed visual/performance identities. Structural PASS does not prove image or motion quality.

## Implementation-plan authority (v1.3)

Every PR P0–P11 must implement the corresponding `docs/implementation/Pxx_*.md`, report task-by-task proofs in phase QA, and execute `tools/validate_implementation_pack.py` plus `tools/test_cross_phase_contracts.py`. Master Spec §20 controls canonical voice final-extension limits (768 final frames/shot, 23040 final frames maximum); raw voice length in P8 is not the final scheduling authority. Contract collisions are blockers, not choices left to agents.
