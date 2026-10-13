# P5/P6 — Manual director to 28-second MP4

This is a **working prototype** with five shots, one real Genielabs Spine 4.2 rig, camera cuts, deterministic frame export, WAV synchronization and FFmpeg assembly. It is **not** yet AI-generated narration or a publishable film-quality pipeline.

## Inputs and outputs

- Director plan: `examples/p6_coffee_film.json` (`FilmPlan` / `film.v1` schema)
- Source motion: existing compiled `P4.3` world-contact sequence of 48 poses, loaded as `runtime/fixtures/baseline/contact_frames.json`
- Character: real synthetic Genielabs `skeleton.json`, `skeleton.atlas`, `skeleton.png`, `rig_profile.json` in `runtime/fixtures/baseline/`
- Five local voice WAVs: `outputs/p6_demo/voices/shot_01.wav` … `shot_05.wav`
- Compiled global timeline: `runtime/fixtures/film_timeline.json`
- Per-sample master audio: `outputs/p6_demo/narration.wav`
- Browser PNGs: `outputs/p6_demo/frames/frame_%06d.png`
- Final container: `outputs/p6_demo/p6_coffee_28s_synthetic_audio.mp4` in the **CI demo**; change the filename for real narration

## P5 manual workflow

In local FastAPI service (`python -m studio`), use `POST /handoff/film/export` with `{"prompt":"...","catalog":{"rigs":["baseline"],"source_frames":48}}`; copy the returned text into ChatGPT or DeepSeek and save its JSON output locally. No LLM API calls are made. Validate it using `POST /film/compile` (body `{"film":{...},"clips":{"baseline":{...compiled P4 clip...}}}`) or use the Python CLI below. Invalid frame spans or missing assets fail closed.

The film JSON specifies `shot_id`, `duration_frames`, `rig_id`, `clip_in`, `clip_out`, camera `zoom/pan_x/pan_y`, and narration `text/wav/start_frame`. All 5 source-clip ranges must consume indices 0–47 exactly once; the current proof supports 24 FPS and 640×480.

## P6 voice without API

Use your **local Kokoro** workflow to produce five WAV clips corresponding to the five narration texts. Convert each file, if necessary, with FFmpeg:

```powershell
ffmpeg -i input_kokoro_shot_01.wav -ac 1 -ar 24000 -c:a pcm_s16le outputs/p6_demo/voices/shot_01.wav
```

Repeat for shots 02–05. The code accepts PCM16 mono WAVs at 24,000 Hz and rejects missing files, incorrect formats, overlaps, and audio that runs past the end of its shot. There is **no automatic TTS generation, time stretching, forced-alignment, word-level timings, or ElevenLabs alignment API** in P6 yet.

## End-to-end rendering once the Genielabs rig and compiled P4 motion exist

From the repository root:

```powershell
python scripts/compile_film.py examples/p6_coffee_film.json runtime/fixtures/baseline/contact_frames.json runtime/fixtures/film_timeline.json
python scripts/assemble_voice.py runtime/fixtures/film_timeline.json outputs/p6_demo/voices outputs/p6_demo/narration.wav outputs/p6_demo/audio_manifest.json
cd runtime
npm install
npx playwright install chromium
npx esbuild film_scene.mjs --bundle --format=esm --outfile=film_scene.bundle.js
cd ..
node runtime/film_render.mjs
ffmpeg -y -framerate 24 -i outputs/p6_demo/frames/frame_%06d.png -i outputs/p6_demo/narration.wav -map 0:v:0 -map 1:a:0 -c:v libx264 -pix_fmt yuv420p -c:a aac outputs/p6_demo/film_with_real_kokoro.mp4
```

The sample rig and motion creation before these commands is automated by [`.github/workflows/p6-five-shot-film.yml`](../.github/workflows/p6-five-shot-film.yml), including exact pinned Genielabs source. For standalone Windows use, follow that workflow to prepare `runtime/fixtures/baseline` before rendering.

**CI demo only:** `python scripts/p6_fixture_voice.py` creates **five two-second sine-wave signals**. These deliberately contain **no spoken words** and are used only to exercise sample-accurate synchronization. Do not mistake the resulting AAC track for Kokoro narration.

## Timing contract

24 FPS, 24,000 audio samples/second → 1,000 samples per frame, exact (no rounding error). The 5 shot ranges are [0,96), [96,240), [240,384), [384,528), [528,672); starts of the 5 WAVs are frames 8, 102, 246, 392 and 536 respectively. The master WAV is exactly 672,000 samples / 28 seconds. FFprobe verifies H.264 + AAC, 640×480, 24 FPS, 672 video frames and 28-second MP4.

Camera shots are deterministic fixed zoom/pan cuts. This is single-actor with one source motion clip stretched to the five shot windows; edit authored FilmPlan values for different demo framing and narration, but do not claim that this is a complete AI directing engine.
