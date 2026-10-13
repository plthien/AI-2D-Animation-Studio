# Local quickstart (PowerShell)

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[test]"
Copy-Item .env.example .env
# Set GLABS_API_KEY and enable the MAX webhook server inside G-Labs Automation.
python -m studio
```

The API is available at http://127.0.0.1:8000/docs.

```powershell
python -m pytest --cov=studio --cov-branch --cov-report=term-missing --cov-fail-under=100
```

The current unit-test suite uses HTTP mocks; real image generation is **not** invoked during tests. Results from /images/generate return a task ID for subsequent status polling. No images are created automatically until the user submits a request.

Do not put secrets into Git commits. This foundation is intentionally incomplete: see docs/STATUS.md.
