---
name: native-auto-rig
description: Implement native local parts segmentation, positioning, anatomy, pivots, Spine 4.2 skeleton/atlas builder, RigProfile and human review for P4.
---

# Skill — native-auto-rig

## References

Read `MASTER_SPEC.md` §8.1–8.6, §10.2, Appendix A P4; schemas `parts_manifest`, `rig_layout`, `rig_joints`, `rig_manifest`, `rig_profile`. Follow all actual algorithm parameters in §8; do not invent replacements.

## Procedure

1. Input approved reference pose, separated parts atlas + immutable hashes. Reject merged/incomplete parts when semantic proof is absent. No Genielabs source, Gemini calls or synthetic success fallback.
2. Implement alpha/crop-component segmentation with byte/dimension/alpha guards; emit `parts_manifest.v1`, overlays and per-part confidence. Stable order and file naming.
3. Position parts with geometry and locally available matching methods from spec; on ambiguity produce `REVIEW_REQUIRED`, never assume a joint location without review.
4. Resolve exactly 14 required humanoid semantic parts and explicit parent hierarchy; verify finite in-canvas anchors, positive segment lengths, corrected x-right/y-up conversion, draw/z ordering.
5. Build native 4.2 Spine bones/slots/attachments, packed RGBA atlas with padding and texture bleed tests; validate load against official runtime. Build RigProfile from **actual** bone hierarchy and geometry.
6. Rig Workshop must support part-role assignment, anchor/pivot adjustment, before/after overlay, pose matrix test and immutable approval.
7. Test inconsistent atlas, undersegmentation, duplicate anatomy, zero-length joints, negative coords, mismatched 4.2 runtime, real browser sampling and per-bone world transforms.

## Acceptance

A valid JSON skeleton without convincing poses is only structural proof; real G-Labs character pose screenshots and reviewer acceptance are required to pass final product gate.


## Mandatory animation-first v1.2 amendment

Stage 4 output is `rig_manifest.v1`, never `rig_package.v1`. `parts_manifest.v1` stores both source reference and parts atlas artifact IDs+SHA. Skeleton may have extra approved bones; core 16 semantic roles required, runtime must verify all named bones.

## Mandatory phase implementation authority

Read `docs/implementation/INDEX.md` and the matching full `Pxx_*.md` plan before writing code; run `tools/validate_implementation_pack.py` and `tools/test_cross_phase_contracts.py` as part of this skill. Phase plan adds executable work orders but cannot override Master Spec or normative JSON Schema.
