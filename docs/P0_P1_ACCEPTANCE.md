# P0/P1 gate ledger

- [x] Python scaffold and tests implemented
- [x] Browser Spine 4.2 sample smoke runner and GitHub Actions workflow implemented
- [ ] **P0** browser workflow succeeded and screenshot artifact independently inspected
- [ ] **P0** Python C0 and C1 both 100% on current code
- [x] **P1** asynchronous G-Labs webhook client and mock contract tests implemented
- [x] **P1** explicit opt-in local smoke command available
- [ ] **P1** REAL Windows-local MAX webhook health check, create, status, download completed

Run locally: `python scripts/glabs_live_smoke.py --run-live --output outputs/glabs-smoke.png` with `GLABS_API_KEY` in environment and running G-Labs. Do NOT submit secrets to GitHub. No unit tests are substitutes for real browser/render/webhook integration.
