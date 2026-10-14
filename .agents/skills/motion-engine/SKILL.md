---
name: motion-engine
description: Implement deterministic full-body 2D world-state motion planner, action DSL, root/gait/IK, contact and cross-shot continuity for P5–P7.
---

# Skill — motion-engine

## References

`MASTER_SPEC.md` §9.2–§10.8, Appendix C, Appendix A P5/P7; `animation_plan`, `rig_profile`, `compiled_film` schemas. No old one-arm `studio/motion.py` from discarded prototype.

## Procedure

1. Author one action registry and semantic-to-executable mapping from §9.2. Validate declared required rig capability, action intervals, channel conflicts, binding ownership and shot boundaries.
2. Implement deterministic pure evaluation `evaluate(shot, frame, frozen_state)`: no accumulating previous rendered frame; fixed 24 FPS and exact half-open action/event intervals.
3. Implement world transform, 2-bone IK for left/right hands and legs; unreachable target error instead of fake pose. Use exact foot-lock/gait parameters from Appendix C; test support-leg planting.
4. Implement independently blendable lanes for locomotion, upper-body, head/look and expression; highest precedence for contact constraints and explicit events.
5. Implement `grab`, `carry_to`, `place_at` with 1 prop per hand, single ownership, exact socket, release frame world handoff. Preserve world prop coordinates over normal shot cuts, reject teleportation.
6. Render pose data to `compiled_film.v1` with reproducible frame hashes and exact source IDs. Ensure same engine handles Appendix B/G acceptance films without story-specific code.
7. Test each action, simultaneous walk/look, attachment while walking, retarget to different limb lengths, IK endpoint errors, lossless handoff and 2-actor ownership conflicts.

## Acceptance

No false green on structurally valid but unreachable/foot-sliding animation; browser true-bone world transforms must confirm contact.


## Mandatory animation-first v1.2 amendment

Respect bounded `animation_plan.shots[].performance` derived from ChannelDNA v2. Energy scales non-contact idle/arm-swing only; easing affects transition frames but never grip or IK targets. Accept 16..64 approved actual rig bones and preserve determinism.

## Mandatory phase implementation authority

Read `docs/implementation/INDEX.md` and the matching full `Pxx_*.md` plan before writing code; run `tools/validate_implementation_pack.py` and `tools/test_cross_phase_contracts.py` as part of this skill. Phase plan adds executable work orders but cannot override Master Spec or normative JSON Schema.
