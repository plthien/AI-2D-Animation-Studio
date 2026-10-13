"""Small local API. External AI remains manual; G-Labs remains user-controlled."""
from __future__ import annotations
import os
from pathlib import Path
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from studio.glabs import GlabsClient, ImageRequest
from studio.handoff import AnimationPlan, export_task

app = FastAPI(title="AI 2D Animation Studio", version="0.1.0")


class HandoffRequest(BaseModel):
    prompt: str
    catalog: dict = {}


@app.get("/health")
async def health() -> dict:
    return {"ok": True, "llm_mode": "manual", "glabs": "not_checked"}


@app.post("/handoff/export")
async def handoff_export(request: HandoffRequest) -> dict:
    path = export_task(request.prompt, request.catalog, Path(os.getenv("STUDIO_OUTPUT_ROOT", "outputs")) / "ai_task.txt")
    return {"path": str(path)}


@app.post("/handoff/validate")
async def handoff_validate(plan: AnimationPlan) -> dict:
    return {"valid": True, "shots": len(plan.shots), "frames": sum(s.duration_frames for s in plan.shots)}


@app.post("/images/generate")
async def image_generate(request: ImageRequest) -> dict:
    try:
        async with GlabsClient.from_env() as client:
            task_id = await client.submit(request)
        return {"task_id": task_id, "status": "pending"}
    except (ValueError, OSError, RuntimeError) as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@app.get("/images/{task_id}")
async def image_status(task_id: str) -> dict:
    async with GlabsClient.from_env() as client:
        return await client.status(task_id)
