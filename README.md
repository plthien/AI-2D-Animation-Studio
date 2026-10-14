# AI 2D Animation Studio

P0 provides the local platform foundation: persistent channels and projects, ChannelDNA v2 validation, immutable artifact storage primitives, job projections, and the seven-stage Studio shell. Generation, rigging, motion, rendering, and voice controls are not implemented in P0.

## Requirements

- Windows 10/11 x64
- Python 3.12
- Node.js 22 and npm
- FFmpeg is optional in P0; it is required by later export phases.

Run `setup.bat` once, then `start.bat`. Setup installs pinned Python and npm dependencies and builds the UI. The app binds to loopback at `http://127.0.0.1:8000`; the SQLite database defaults to `ai_2d_animation_studio.db` and artifacts to `local_artifacts/`.

For development, activate `.venv`, run `python -m uvicorn app.main:app --host 127.0.0.1 --port 8000`, and rebuild the UI with `npm run build`. The UI is served from the generated `dist/` directory by FastAPI. API documentation is available at `/docs`.

The five frozen contract checks are run with Python 3.12:

```powershell
python tools/validate_contract_pack.py
python tools/test_animation_contract_semantics.py
python tools/test_cross_phase_contracts.py
python tools/validate_agent_pack.py
python tools/validate_implementation_pack.py
```
