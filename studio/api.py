"""Small local API. External AI remains manual; G-Labs remains user-controlled."""
from __future__ import annotations
import os
from pathlib import Path
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from studio.glabs import GlabsClient, ImageRequest
from studio.handoff import AnimationPlan, export_task, export_motion_task
from studio.motion import MotionPlan, MotionError, compile_motion
from studio.retarget import RigProfile, compile_retargeted
from studio.world import WorldProp, compile_world_motion

app = FastAPI(title="AI 2D Animation Studio", version="0.1.0")


class HandoffRequest(BaseModel):
    prompt: str
    catalog: dict = Field(default_factory=dict)


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


@app.post("/handoff/motion/export")
async def motion_export(request: HandoffRequest) -> dict:
    try:
        path = export_motion_task(
            request.prompt, request.catalog,
            Path(os.getenv("STUDIO_OUTPUT_ROOT", "outputs")) / "motion_task.txt",
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return {"path": str(path), "mode": "manual"}


@app.post("/motion/compile")
async def motion_compile(plan: MotionPlan) -> dict:
    try:
        return compile_motion(plan)
    except MotionError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


class RetargetRequest(BaseModel):
    plan: MotionPlan
    profile: RigProfile
    skeleton: dict


@app.post("/motion/retarget")
async def motion_retarget(request: RetargetRequest) -> dict:
    """Retarget one manually authored plan to a verified rig profile."""
    try:
        return compile_retargeted(request.plan, request.profile, request.skeleton)
    except MotionError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


class WorldRetargetRequest(RetargetRequest):
    world_prop: WorldProp


@app.post("/motion/world-retarget")
async def motion_world_retarget(request: WorldRetargetRequest) -> dict:
    """One stationary world prop target shared across different rig profiles."""
    try:
        return compile_world_motion(request.plan, request.profile, request.skeleton, request.world_prop)
    except MotionError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
