# P3 fixed-step 2D runtime (technical proof)

The project now has an actual **Spine 4.2.120 / PixiJS 8.21.0** bundle, not just the legacy Spine Player preview.

```bash
cd runtime
npm install
npx playwright install chromium
npm run build
cd ..
# Place sombrero.json/.atlas/.png from upstream Genielabs under runtime/fixtures/
node runtime/fixed_smoke.mjs
node runtime/render_sequence.mjs 24 outputs/p3/sequence
ffmpeg -framerate 24 -i outputs/p3/sequence/frame_%06d.png -c:v libx264 -pix_fmt yuv420p outputs/p3/idle.mp4
```

- No ticker progression: `autoUpdate=false`.
- Scene pose advances in exact `1/24` steps, with zeroed state when seeking backwards.
- Sequential export advances incrementally; does not replay from the beginning for every adjacent frame.
- Frames 0, middle and final re-seek and hash-match screenshot output after the whole export.
- This is a **single-actor P3 technical proof at 640x480**, not the full 1920x1080 multi-layer camera/prop scene renderer.
- If the artifact/quality gate fails in a browser/GPU combination, investigate WebGL fallback rather than masking pixel differences.

See `.github/workflows/p3-frame-smoke.yml` for CI smoke evidence.
