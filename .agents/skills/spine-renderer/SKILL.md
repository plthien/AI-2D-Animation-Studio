---
name: spine-renderer
description: Implement official matching Spine 4.2/PixiJS 8 deterministic shot rendering, preview and exact frame-sequence export for P7.
---

# Skill — spine-renderer

## References

`MASTER_SPEC.md` §8.5, §10.8, §11.1, Appendix A P7, `frame_sequence_manifest`, `compiled_film` schemas; official https://en.esotericsoftware.com/spine-pixi.

## Procedure

1. Pin official Spine-Pixi v8 4.2.x and supported PixiJS 8 version with lockfile; fail closed if skeleton/runtime editor version differs.
2. Load approved `rig_manifest` and textures from job-specific readonly staging; no shared mutable fixture roots, no internet asset fetching.
3. Seek a **specific** `[shot_id, frame]`; apply compiler-authored root, bones/IK, skins, draw order, props, background and camera. No `requestAnimationFrame`/wall-clock time as frame authority.
4. Render exact 1280x720 RGBA to deterministic frames; stable file names, numeric sequence completeness, frame hash manifest and missing-frame rejection.
5. Verify independent resampling and replay hashes, multi-shot ordering, project isolation, cancellation cleanup and browser version consistency.
6. Preview selected poses and review sprite seams, foot plants, hand gripping, temporal continuity across camera cuts.

## Acceptance

Two independent films with identical engine code hashes, zero stale frames and exact ffprobe FPS/frame counts. Browser screenshots required, not only synthetic serialization tests.


## Mandatory animation-first v1.2 amendment

Use official Spine-Pixi v8 4.2.x and PixiJS >=8.16 with the matching Spine 4.2 skeleton JSON, WebGL preferred. Do not hardcode exactly 16 emitted bones; verify exact approved `rig_profile.runtime_bone_names`, support approved extras and reject unknown bones. Check Spine runtime license before distributing.

## Mandatory phase implementation authority

Read `docs/implementation/INDEX.md` and the matching full `Pxx_*.md` plan before writing code; run `tools/validate_implementation_pack.py` and `tools/test_cross_phase_contracts.py` as part of this skill. Phase plan adds executable work orders but cannot override Master Spec or normative JSON Schema.
