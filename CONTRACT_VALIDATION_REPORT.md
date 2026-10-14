# Animation-first Codex Specification validation — v1.2

Date: 2026-10-14. The following commands were run locally against the updated files. These are **specification checks only** and not proof of actual G-Labs, Spine, Kokoro, FFmpeg or Windows production behavior.

- `python tools/validate_contract_pack.py` — exit 0: `PASS 19 schema/example pairs + animation-specific cross-artifact assertions`
- `python tools/test_animation_contract_semantics.py` — exit 0: `PASS 30 animation-first positive/negative and cross-domain contract assertions`
- `python tools/validate_agent_pack.py` — exit 0: `PASS 1 AGENTS + 9 skills + 5 rules + authoritative references`

Changes audited: 19 schema/example pairs; Channel DNA v2; bounded per-shot acting; actor bone set; silent visual shots; atlas/reference source lineage; no unsupported effect; official Spine runtime/license references.

No application source was implemented as part of this contract revision. Real provider/rig/animation/video acceptance remains NOT_RUN.
