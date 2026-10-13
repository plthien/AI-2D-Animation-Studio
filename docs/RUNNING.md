# Local Windows setup

```powershell
git clone https://github.com/plthien/AI-2D-Animation-Studio.git
cd AI-2D-Animation-Studio
git checkout feat/p0-p1-foundation
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[test]"
Copy-Item .env.example .env
# Set GLABS_API_KEY inside your environment (the app does not auto-load .env yet):
$env:GLABS_API_KEY = "COPY_FROM_GLABS_WEBHOOK_TAB"
python -m studio
```

Go to http://127.0.0.1:8000/docs for the FastAPI interface.

To run mock-only unit tests:

```powershell
pip install pytest-asyncio
python -m pytest --cov=studio --cov-branch --cov-report=term-missing --cov-fail-under=100
```

For direct Genielabs builder use, acquire the upstream repository separately, pin a reviewed commit, then call `studio.rigging.run_genielabs_builder`. No upstream source is committed to this branch.

**Important:** This is an incomplete foundation, not an operational end-to-end generator. Real G-Labs/Spine integration and passing coverage must be verified separately.
