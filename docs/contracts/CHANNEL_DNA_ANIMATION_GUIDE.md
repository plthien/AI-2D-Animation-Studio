# Channel DNA v2 — animation-first authoring guide

## Why v2 and what is kept from YTB

YTB ChannelDNA v3 had `channel`, `narration_wpm`, `pacing_profiles`, `narration_identity`, 7-field `visual_identity`, `entity_styles` and global constraints. The animation project **does not copy** that contract: keep the useful creative-authority categories and redefine them for full-body cutout motion. `channel_dna.v2` is now the single runtime schema and is intentionally incompatible with YTB v3 and the earlier draft v1.

## Required fields and consumers

| Block | Contract | Owner and consumer |
|---|---|---|
| `channel` | name, language, niche, audience | Channel CRUD + authoring prompt |
| `content_identity` | format enum, promise, story rules, humor rules | external Idea/Script/Shot prompts only |
| `visual_identity` | EXACT keys medium, linework, rendering, palette, shape_language, texture, editorial_language; string minimum one char each | G-Labs prompt compiler + human QC |
| `entity_styles` | arrays for character/location/prop/expression | reference/parts/bgs/props generation and continuity QC |
| `narration` | WPM min/max/style | Script + voice config; semantic validator: `wpm_min < wpm_max` |
| `narration_identity` | voice, delivery, tone boundaries, avoid | external Script prompt + TTS profile advice |
| `animation_identity` | acting_style enum, energy, rhythm, easing, reaction hold 0..24 frames, acting rules, motion constraints | external Director and deterministic motion compiler |
| `editorial_identity` | shot rhythm, camera guidelines, comedy timing, cut rules | Shot Plan and Director prompt, QC |
| `global_negative_constraints` | nonempty unique string list | all visual prompts and QA |
| `render` | width=1280,height=720,fps=24 | export authority fixed MVP |

## Style hash partition

Canonical JSON is UTF-8 with sorted keys, no spaces, no NaN. Hash values are `sha256:` plus lowercase hex. The three **domain** hashes (not necessarily whole ChannelDNA artifact hash):

```text
visual_style_hash     = H({visual_identity, entity_styles, global_negative_constraints})
performance_style_hash= H({animation_identity, editorial_identity})
narration_identity_hash=H({narration, narration_identity})
```

Changing animation energy should recompile Motion/Director only, **not** regenerate character assets. Changing palette should invalidate asset compatibility; it cannot quietly reuse an incompatible rig. Changing narration style reopens Script/Voice only when approved inputs require it; it does not automatically delete approved rigs.

## Deterministic performance mapping for MVP

| Field | Behavior |
|---|---|
| `motion_energy=low/medium/high` | 0.75/1.0/1.25 multiplier on secondary non-contact arm swing, idle breath/head idle only |
| `transition_easing=gentle/standard/snappy` | intended transition frames 6/4/2, capped by floor(action_duration/4); interpolation smoothstep |
| `movement_rhythm` | affects idle phase and style guidance only; does not change world speed, event timing or contact |
| `reaction_hold_frames` | minimum length of an authored expression before legal next reaction; don't synthesize a new reaction |
| `acting_style` | prompt-level authoring identity; no hidden executable `acting_style` runtime branch |
| `editorial_identity` | authoring/camera plan guidance; no secret AI interpretation by runtime |

Runtime SHALL NOT infer new actions from narrative prose, nor change physical root motion/IK reach in response to style modifiers. `animation_plan.shots[].performance` contains exactly the four executable settings copied from approved DNA. Missing or changed settings reject with `DIRECTOR_PERFORMANCE_SOURCE_MISMATCH`; no silent default. Both performance and artistic direction are reviewed, not magic animation synthesis.

## Authoring instructions

All ChannelDNA example strings are meaningful style constraints, not copied neutral placeholders. The sample is deliberately channel-neutral comedy, not a dependency on any existing YouTube channel or a person. Importer must normalize nothing; unexpected fields fail. UI may collect each block with field validation and show hash partition preview. Store new revisions with content SHA.
