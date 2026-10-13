# P7 — Repeatable two-story benchmark

## Requirements

- Python 3.12+ and project dependencies installed: `pip install -e ".[test]"`
- Node 22, `cd runtime && npm install && npx playwright install chromium`
- FFmpeg and ffprobe available on PATH.
- Genielabs scripts `build_spine_json.py` and `make_atlas.py` pinned to upstream SHA `702b71689cac826efee942ee4564fef9560d6ef8` at `vendor/genielabs/scripts/`.

## Shared rig/fixture setup

From the repository root:

```powershell
python scripts/p4_spine_fixture.py --genielabs vendor/genielabs --out outputs/p7/shared_rigs/baseline --variant baseline
python scripts/p4_spine_fixture.py --genielabs vendor/genielabs --out outputs/p7/shared_rigs/compact --variant compact
```

Copy each output rig's `skeleton.json`, `skeleton.atlas`, `skeleton.png`, `rig_profile.json` to matching `runtime/fixtures/baseline` and `runtime/fixtures/compact` directories respectively. To prepare the two fixture story worlds:

```powershell
python scripts/p6_v2_fixture_assets.py
python scripts/p7_lost_key_fixture_assets.py
python -c "from pathlib import Path; from scripts.p6_fixture_voice import main; main(Path('outputs/p7/coffee/voices')); main(Path('outputs/p7/lost_key/voices'))"
```

Those audio signals are not words or Kokoro; replace with your **own existing** mono 24kHz PCM16 WAV files to test real spoken audio. No TTS is invoked.

## One identical renderer command for both movies

```powershell
python scripts/run_film_v2.py --plan examples/p6_v2_film.json --catalog examples/p6_v2_catalog.json --motions examples/p6_v2_motions.json --voices outputs/p7/coffee/voices --workspace outputs/p7/coffee/workspace --output outputs/p7/coffee/coffee_28s.mp4
python scripts/run_film_v2.py --plan examples/p7_lost_key_film.json --catalog examples/p7_lost_key_catalog.json --motions examples/p7_lost_key_motions.json --voices outputs/p7/lost_key/voices --workspace outputs/p7/lost_key/workspace --output outputs/p7/lost_key/lost_key_21s.mp4
```

All code executed in `studio/`, `runtime/`, `scripts/run_film_v2.py` is the same for both movies. Only `--plan`, `--catalog`, `--motions`, `--voices`, `--workspace` and `--output` input paths change. The output folders are isolated; the CLI discards stale frame/preview PNGs before each run.

For a fully reproducible automation of installation, upstream pinning, both videos and the detailed ffprobe/hash/asset-count checks, use [P7 GitHub Actions workflow](../.github/workflows/p7-two-stories-reuse.yml).

## Scope

This benchmark uses deterministic synthetic artwork and supported 2-link left-arm motions, no G-Labs live assets and no Kokoro. Passing P7 means story/package reusability within this engine subset, not arbitrary cinematography or production-quality character acting.
