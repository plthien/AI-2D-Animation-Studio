---
name: asset-resolution
description: Build canonical global Asset Registry and deterministic reuse-or-generate resolver for P2.
---

# Skill — asset-resolution

## References

`MASTER_SPEC.md` §3, §6, Appendix A P2; contracts `asset_requirements`, `asset_resolution`, `asset_version`, `shot_plan`.

## Procedure

1. Derive required character/location/prop/rig identities exactly from current approved ShotPlan. Use explicit `asset_key`, visual/style/view, rig capability and immutable versions; do not fuzzy-match names.
2. Resolve each requirement into allowed statuses as specified in §6.3 (reuse, image needed, rig needed, review, blocked). Check image hash/version/approval and rig/motion capability; never select stale or incompatible art.
3. De-dupe repeat keys across shots/projects under approved global scope; block conflicting semantic identity rather than guessing reuse.
4. Persist complete ordered `asset_requirements.v1` and `asset_resolution.v1`; implement manual relink/approval and lineage invalidation, not silent reassignments.
5. Test exact-match reuse, unknown variant, mismatched view, stale image/rig, duplicate demand and concurrent reservation for single asset.

## Acceptance

No paid G-Labs call triggered by resolver. Every demanded asset has an actionable decision and a traceable immutable input.


## Mandatory animation-first v1.2 amendment

Resolve only `character`, `background`, `prop` asset kinds. Hash visual identity/entity styles/negative constraints, excluding animation/editorial performance; changes to acting do not force image regeneration. Detect rig capability independently.

## Mandatory phase implementation authority

Read `docs/implementation/INDEX.md` and the matching full `Pxx_*.md` plan before writing code; run `tools/validate_implementation_pack.py` and `tools/test_cross_phase_contracts.py` as part of this skill. Phase plan adds executable work orders but cannot override Master Spec or normative JSON Schema.
