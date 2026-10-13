# P0/P1 acceptance

## P0 — initial foundation/runtime sample: PASS
- [x] Python package and local API
- [x] 100% C0/C1 **for measured first-party modules** in [Python checks](https://github.com/plthien/AI-2D-Animation-Studio/actions/runs/38395974624): 57 tests, 226 statements/72 branches fully covered
- [x] Real Spine 4.2 sample loads into Chromium and renders screenshot artifact in [runtime smoke](https://github.com/plthien/AI-2D-Animation-Studio/actions/runs/38395980638)
- [ ] Browser screenshot manually visually reviewed, and new custom rig validated (belongs with P2)
- [ ] Frame-number deterministic PNG exporter (P3)

## P1 — webhook: LIVE GATE PENDING
- [x] Submit (202), status polling, cancel, download with HTTP mock tests
- [x] Opt-in command `python scripts/glabs_live_smoke.py --run-live --output outputs/glabs-smoke.png`
- [ ] Start Windows G-Labs Automation MAX Webhook and set `GLABS_API_KEY` locally
- [ ] Confirm live `/api/health`, submit image, get completed status, download and inspect a valid result

P1 cannot be honestly completed from a cloud runner: user's Windows localhost G-Labs service is unreachable here. Do not publish the key or open the local service to the Internet solely for this test.
