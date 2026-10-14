from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

from alembic import command
from alembic.config import Config
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.responses import FileResponse

from app.api.errors import ApiError, api_error_handler, unexpected_error_handler
from app.api.routes import artifacts, channels, jobs, projects, system
from app.core.config import get_settings
from app.db.session import engine


@asynccontextmanager
async def lifespan(_app: FastAPI):
    from app.infrastructure.sqlite import ensure_sqlite_parent_dir
    ensure_sqlite_parent_dir(engine)
    config_path = Path(__file__).resolve().parents[1] / "alembic.ini"
    cfg = Config(str(config_path))
    cfg.set_main_option("sqlalchemy.url", get_settings().database_url)
    command.upgrade(cfg, "head")
    yield


app = FastAPI(title="AI 2D Animation Studio", version="0.1.0", lifespan=lifespan)
app.add_exception_handler(ApiError, api_error_handler)
app.add_exception_handler(Exception, unexpected_error_handler)
app.add_middleware(CORSMiddleware, allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"], allow_credentials=False, allow_methods=["GET", "POST", "PUT", "OPTIONS"], allow_headers=["Content-Type"])


@app.exception_handler(RequestValidationError)
async def validation_error_handler(_request: Request, exc: RequestValidationError) -> JSONResponse:
    first = exc.errors()[0] if exc.errors() else {"loc": (), "msg": "Invalid request"}
    location = first.get("loc", ())
    path = "$" + "".join(f"[{part}]" if isinstance(part, int) else f".{part}" for part in location if part not in ("body", "query", "path"))
    return JSONResponse(status_code=422, content={"error": {"code": "REQUEST_INVALID", "message": first.get("msg", "Invalid request"), "retryable": False, "details": {"path": path, "recovery": "Correct the request and try again."}}})


app.include_router(system.router)
app.include_router(channels.router, prefix="/api/v1")
app.include_router(projects.router, prefix="/api/v1")
app.include_router(jobs.router, prefix="/api/v1")
app.include_router(artifacts.router, prefix="/api/v1")


@app.get("/{full_path:path}", include_in_schema=False)
def serve_frontend(full_path: str) -> FileResponse:
    if full_path == "api" or full_path.startswith("api/"):
        raise ApiError(404, "RESOURCE_NOT_FOUND", "Resource was not found.")
    dist = Path(__file__).resolve().parents[1] / "dist"
    requested = (dist / full_path).resolve()
    if not requested.is_relative_to(dist):
        raise ApiError(404, "RESOURCE_NOT_FOUND", "Resource was not found.")
    if requested.is_file():
        return FileResponse(requested)
    index = dist / "index.html"
    if index.is_file():
        return FileResponse(index)
    raise ApiError(503, "FRONTEND_NOT_BUILT", "Run npm run build to create the local UI.")
