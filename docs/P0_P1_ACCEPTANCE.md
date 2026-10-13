# P0 / P1 acceptance record

## P0 — foundation and actual Spine runtime proof
- [x] Source structure and local Python backend
- [x] Manual ChatGPT/DeepSeek JSON export/validate
- [ ] Spine 4.2 sample with atlas loads into an actual browser runtime
- [ ] Real deterministic screenshot `p0_spine_frame.png` uploaded to CI artifact
- [ ] Runtime controls and no broken attachments verified
- [ ] 100% C0 + C1 measured by GitHub Actions (see latest run)

## P1 — live G-Labs image generation
- [x] Asynchronous POST task, polling, cancel; transport isolation tests
- [x] Safe destination file write and result URL validation
- [ ] Windows desktop G-Labs MAX webhook started and reachable
- [ ] `GET /api/health` succeeds
- [ ] Real `POST /api/image/generate` returns 202 with task id
- [ ] Terminal status yields at least one downloadable image
- [ ] Open/check actual PNG/JPEG and store source prompt, model and task id

Never mark a live gate as passed based on mocked HTTP calls. No user's G-Labs secrets should go into GitHub Actions. The P1 live gate requires an authenticated Windows-local environment.
