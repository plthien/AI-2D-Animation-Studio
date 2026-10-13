# Implementation status

- Repository initialized; foundation branch implements P0 scaffolding and the P1 G-Labs webhook client with mocks.
- The app deliberately does **not** call LLM APIs. ChatGPT/DeepSeek handoff is file-based.
- P0 runtime gate **not passed yet**: no verified Spine 4.2 / PixiJS PNG sample from a real browser.
- P1 real G-Labs gate **not passed yet**: requires Windows desktop app (MAX), running webhook, and secret API key.
- P2–P7 **not implemented**: Genielabs adapter, rig builder, motion compiler, PixiJS renderer, voice and final-video assembly.
- Unit tests are isolated; do not mistake them for an actual rendering/quality check.
