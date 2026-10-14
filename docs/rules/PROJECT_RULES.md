# PROJECT RULES — Frozen product boundaries

## Project and source authority

- Target: `plthien/AI-2D-Animation-Studio`, working from its `main` (only startup README at planning freeze). No past prototype code is allowed; explicitly ignore `feat/p0-p1-foundation` and Draft PR #1.
- Upstream neutral modules ONLY from `plthien/ytb-ai-studio` commit `393d0eb5516ac8bb8455f859b79bfc64388b128e`, selectively per `MASTER_SPEC.md` §1. Do not modify the upstream repository.
- Genielabs reference is conceptual and algorithmic only; no vendor checkout, direct source imports, copied builder, image SDK, or runtime dependency.
- This repository is an independent product with fresh database, APIs and animation domain; never copy all YTB schema/migration versions or screenshot-era Scene/Beat model.

## Invariant business flow

1. Idea/Script/Shot Plan via ChatGPT/DeepSeek **outside app**, human copy/import JSON.
2. Asset requirements, global registry and resolver; exact identities and approved revisions only.
3. G-Labs character/parts/locations/props image generation; every paid request confirmed.
4. Native local parts/anatomy/Spine auto-rig with explicit review for low-confidence joints.
5. External AI Animation Director `animation_plan.v1` created **outside app** and imported.
6. Deterministic world/motion/Spine runtime, multi-shot rendering.
7. Voice-last 48kHz, frame reconciliation, FFmpeg MP4 and QC.

## Prohibited shortcuts

- No in-app LLM API, hidden AI web search, or direct Genielabs SDK.
- No fallback to image-per-Beat video, Ken Burns in place of acting, fake/placeholder rig after failure, or fabricated voice labelled narration.
- No hard-coded story names/shot IDs in runtime or production motion templates.
- No silent semantic rewrites of externally-authored JSON, unsupported action substitutions, or arbitrary teleport to satisfy continuity.
- No calling a project successful because JSON validated while actual rig/Spine/frames/voice remain untested.

## MVP scope lock

24 FPS / 1280x720 CFR; 30-shot maximum; one approved rig view per actor; 1–2 humanoid actors per shot, <=3 props; 14 required semantic cutout parts; root locomotion, `idle`, `walk_to`, `look_at`, `reach_for`, `grab`, `carry_to`, `place_at`, `point_at`, `react`; basic expressions; no physics, jumping, 360° turns, combat or phoneme lip sync. See `MASTER_SPEC.md` §0.1/§0.3 for all exact constraints. Do not change caps without an explicit spec revision.

## User-cost and data policy

- Local-first, no provider charges without explicit human action and accurate provider task ownership. Ambiguous provider POST is blocked and reconciled, never blindly retried.
- Secrets only in backend environment, never client, artifact JSON, prompt exports or logs. Do not upload private input assets to unrelated third parties.
- Project data is scoped, auditable and versioned; approval and invalidation are explicit.


## Animation-first scope (v1.2)

`channel_dna.v2` separates visual style, performance identity, narration identity and editorial identity; asset reuse must not invalidate because acting-only settings changed. Rig final artifact is `rig_manifest.v1` (not `rig_package.v1`). Supported asset kinds are character/background/prop only. One silent visual shot uses `narration_text=""` with zero-length script span; all-silent productions and multi-speaker dialogue remain outside narrated MVP. No engine behavior derived from unstructured creative prose; implement only versioned action DSL and bounded performance presets. See Master Spec §19.
