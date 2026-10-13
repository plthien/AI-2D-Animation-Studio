"""Small local API. External AI remains manual; G-Labs remains user-controlled."""
from __future__ import annotations
import os
from pathlib import Path
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from studio.glabs import GlabsClient, ImageRequest
from studio.handoff import AnimationPlan, export_task, export_motion_task, export_film_task, export_film_v2_task
from studio.motion import MotionPlan, MotionError, compile_motion
from studio.retarget import RigProfile, compile_retargeted
from studio.world import WorldProp, compile_world_motion
from studio.film import FilmPlan, FilmError, compile_film
from studio.film_v2 import FilmPlanV2, AssetCatalog, compile_film_v2

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


class FilmCompileRequest(BaseModel):
    film: FilmPlan
    clips: dict[str, dict]


@app.post("/film/compile")
async def film_compile(request: FilmCompileRequest) -> dict:
    try:
        return compile_film(request.film, request.clips)
    except FilmError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.post("/handoff/film/export")
async def film_export(request: HandoffRequest) -> dict:
    import json
    example = json.loads((Path(__file__).parents[1] / "examples/p6_coffee_film.json").read_text(encoding="utf-8"))
    try:
        path=export_film_task(request.prompt,request.catalog,example,
            Path(os.getenv("STUDIO_OUTPUT_ROOT","outputs"))/"film_task.txt")
        return {"mode":"manual","path":str(path)}
    except ValueError as exc:
        raise HTTPException(status_code=422,detail=str(exc)) from exc


class FilmV2CompileRequest(BaseModel):
    film: FilmPlanV2
    catalog: AssetCatalog
    motions: dict[str, dict]


@app.post("/film/v2/compile")
async def film_v2_compile(request: FilmV2CompileRequest) -> dict:
    try:
        return compile_film_v2(request.film, request.catalog, request.motions)
    except FilmError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.post("/handoff/film/v2/export")
async def film_v2_export(request: HandoffRequest) -> dict:
    import json
    example=json.loads((Path(__file__).parents[1]/"examples/p6_v2_film.json").read_text(encoding="utf-8"))
    try:
        path=export_film_v2_task(
            request.prompt, request.catalog, example,
            Path(os.getenv("STUDIO_OUTPUT_ROOT","outputs"))/"film_v2_task.txt")
        return {"mode":"manual","schema_version":"film.v2","path":str(path)}
    except ValueError as exc:
        raise HTTPException(status_code=422,detail=str(exc)) from exc
