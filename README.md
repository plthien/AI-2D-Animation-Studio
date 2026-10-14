# AI 2D Animation Studio

A **local-first 2D animation cockpit** with a React/TypeScript UI and a Python Spine/PixiJS motion/render engine.

## Getting started on Windows

1. Install Python 3.12, Node.js 22, and FFmpeg + ffprobe.
2. Clone the **`feat/p0-p1-foundation` branch** of `plthien/AI-2D-Animation-Studio`.
3. Run **`setup_studio.bat`** one time; installs pinned JS/Python dependencies, Playwright Chromium and the pinned open-source Genielabs scripts.
4. Run **`start_studio.bat`**; open **http://127.0.0.1:8000**.
5. Create a project, open Assets, click **Prepare demo assets (offline)**, then Render & Review → Preflight → Start render. The result is a real multi-shot Spine/PixiJS H.264/AAC MP4, but with **synthetic five-part art and non-speech tone WAVs**.

For your own project art, import PNG/JPEG/WebP assets and local PCM16 WAVs. The new **Rig Workshop** offers separate atlas/ref input, segmentation, positioning and manually approved semantic/pivot rig building. G-Labs tasks can be submitted explicitly and imported into a catalog background or prop, with provider credentials kept in backend environment. G-Labs MAX authenticated live access **still must be tested on Windows**.

### UI design source

Interface layout borrows the dark cockpit/sidebar/pipeline-stage presentation patterns from your [ytb-ai-studio](https://github.com/plthien/ytb-ai-studio) frontend; the 2D Studio code is its own UI rather than a copy of the YouTube app.

### Verified technical baseline

P5: independent `film.v2` per-shot JSON with validated catalogs, motion clips, camera and continuity. P6: Spine/PixiJS fixed-step frames and WAV/FFmpeg MP4 assembly. P7: same engine produces Coffee Cup 28s and Lost Key 21s with different story/art/motion data.

The UI and local workspace endpoints have separate Python API tests and actual Chromium screenshot + rendered-video workflow, located at [UI cockpit CI](https://github.com/plthien/AI-2D-Animation-Studio/actions/workflows/ui-cockpit.yml). See [UI self-review](docs/UI_PHASE_SELF_REVIEW.md), [Windows guide](docs/STUDIO_UI_USER_GUIDE.md), and [project status](docs/STATUS.md).

**Still not production-quality:** authentic G-Labs/Genielabs full-body character acceptance, real Kokoro TTS, expressive acting/lip-sync/physics, fully interactive keyframe editor, robust persistent job queue. The full repo remains [Draft PR #1](https://github.com/plthien/AI-2D-Animation-Studio/pull/1), unmerged.
