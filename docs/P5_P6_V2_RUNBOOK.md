# Finished P5/P6 v2 technical workflow — no Kokoro/G-Labs live calls

The second-generation production interface is **data-driven per shot**. One film JSON references 5 independently authored motion clips, 2 Spine rigs, 2 background images and one reusable prop asset in the sample. The renderer does not convert a 48-frame animation into 672 frames: each shot uses all frames of its own exact-length motion.

## Director workflow

1. Use `POST /handoff/film/v2/export` with a brief and asset catalog; copy the returned prompt into ChatGPT or DeepSeek, and save a well-formed `film.v2` plan.
2. Supply one `MotionPlan` JSON for every unique `motion_id` used in the plan (see `examples/p6_v2_motions.json`). All referenced rig IDs, backgrounds and prop visuals must exist in `AssetCatalog`.
3. Use `POST /film/v2/compile` for in-app validation, or `python scripts/prepare_film_v2.py PLAN CATALOG MOTIONS runtime/fixtures`. Validation rejects absent resources, wrong pose counts/FPS, wrist jumps and prop jumps between neighboring shots; intentional discontinuities need `continuity_break=true`.
4. Place Spine 4.2 JSON/atlas/PNG and `rig_profile.json` in `runtime/fixtures/<rig_directory>`; backgrounds and prop images under `runtime/fixtures/` using catalog-relative image paths. Image creation with G-Labs is a separate pipeline, not required to test P5/P6.
5. Provide local per-shot **mono 24 kHz PCM16 WAVs** in a voice directory. For now WAVs may come from any external process: **do not install or call Kokoro yet**. Silence or synthetic signal fixtures are only valid for CI smoke.
6. Run `python scripts/run_film_v2.py --plan examples/p6_v2_film.json --catalog examples/p6_v2_catalog.json --motions examples/p6_v2_motions.json --voices outputs/p6_demo/voices --output outputs/film.mp4`. Node/PixiJS + Playwright and FFmpeg must be installed. The command revalidates assets, renders exact frames and checks final MP4 frame count. Camera zoom/pan, props and multiple rig assets come from the plan, not hardcoded code.

## CI acceptance fixture

`.github/workflows/p6-v2-independent-shots.yml` generates **synthetic** reference art, five independent motion clips, two Genielabs-backed rigs, two PNG backgrounds and a cup PNG. Narration uses five **non-speech** synthetic sine-wave WAVs, not real TTS. It renders 672 frames at 24 FPS and muxes H.264 + AAC into a 28-second file. The frame manifest records each shot ID, motion IDs, rig IDs, background IDs and SHA-256 replay checkpoints. This distinguishes real per-shot authoring from the original stretched 48-pose P6 demo.

## Remaining production gates (not part of P5/P6 compiler contract)

Real AI-generated full-body characters, verified voice acting and Kokoro, face/mouth/lip-sync, expressive secondary animation, multi-camera depth/layer polish, UI project/file management and P7 second-story reuse are separate tasks. The current sample's five-part Spine actors and basic IK do not demonstrate production-quality human performance. The v2 contracts explicitly support independent per-shot assets and motion even though this sample is synthetic and small-resolution.
