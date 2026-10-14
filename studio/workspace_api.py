"""Local project workspaces and non-billable render orchestration.

The repository's existing film.v2 compiler is the source of truth.
All resources are project-owned on disk; one render runs at a time because the
existing PixiJS browser loader uses runtime/fixtures as a shared staging area.
"""
from __future__ import annotations

import io
import json
import os
import re
import shutil
import subprocess
import sys
import threading
import uuid
import wave
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field, ValidationError
from PIL import Image

from studio.film_v2 import AssetCatalog, FilmPlanV2, compile_film_v2
from studio.motion import MotionPlan, MotionError, compile_motion
from studio.retarget import RigProfile, validate_spine_profile
from studio.glabs import GlabsClient, ImageRequest

router = APIRouter(prefix="/studio", tags=["Studio Workspace"])
REPO = Path(__file__).resolve().parents[1]
PROJECTS = Path(os.environ.get("STUDIO_PROJECTS_ROOT", str(REPO / "workspace" / "projects"))).resolve()
ID = re.compile(r"^[a-z][a-z0-9_]*$")
FILE = re.compile(r"^[a-z][a-z0-9_.-]*$")
KINDS = {"film", "catalog", "motions"}
RUNNER = ThreadPoolExecutor(max_workers=1, thread_name_prefix="studio-render")
LOCK = threading.Lock()
JOBS: dict[str, dict] = {}
MAX_ASSET_BYTES = 32 * 1024 * 1024


def _project(project_id: str) -> Path:
    if not re.fullmatch(r"[0-9a-f]{32}", project_id):
        raise HTTPException(404, "Project not found")
    path = PROJECTS / project_id
    if not (path / "project.json").is_file():
        raise HTTPException(404, "Project not found")
    return path


def _metadata(path: Path) -> dict:
    return json.loads((path / "project.json").read_text(encoding="utf-8"))


def _atomic_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    tmp.replace(path)


def _documents(path: Path) -> tuple[FilmPlanV2, AssetCatalog, dict]:
    try:
        film = FilmPlanV2.model_validate_json((path / "film.json").read_text(encoding="utf-8"))
        catalog = AssetCatalog.model_validate_json((path / "catalog.json").read_text(encoding="utf-8"))
        motions = json.loads((path / "motions.json").read_text(encoding="utf-8"))
        if not isinstance(motions, dict):
            raise ValueError("Motions must be an object")
        return film, catalog, motions
    except Exception as exc:
        raise HTTPException(422, f"Director documents invalid: {exc}") from exc


def _required_assets(film: FilmPlanV2, catalog: AssetCatalog) -> list[str]:
    required = []
    for rig in catalog.rigs.values():
        for name in ("skeleton.json", "skeleton.atlas", "skeleton.png", "rig_profile.json"):
            required.append(f"rigs/{rig.directory}/{name}")
    for asset in [*catalog.backgrounds.values(), *catalog.props.values()]:
        required.append(asset.image)
    required.extend(f"voices/{s.narration.wav}" for s in film.shots if s.narration)
    return sorted(set(required))


def _preflight(path: Path) -> dict:
    film, catalog, definitions = _documents(path)
    problems = []
    warnings = []
    expected = {a.motion_id: a.rig_id for s in film.shots for a in s.actors}
    if set(expected) != set(definitions):
        problems.append("Motion definitions must match referenced IDs exactly")
    clips = {}
    for name, rig_id in expected.items():
        if name not in definitions:
            continue
        try:
            motion = MotionPlan.model_validate(definitions[name])
            clip = compile_motion(motion)
            clip["rig_id"] = rig_id
            clips[name] = clip
            profile = path / "rigs" / catalog.rigs[rig_id].directory / "rig_profile.json"
            skeleton = profile.parent / "skeleton.json"
            if profile.is_file() and skeleton.is_file():
                p = RigProfile.model_validate_json(profile.read_text(encoding="utf-8"))
                validate_spine_profile(p, json.loads(skeleton.read_text(encoding="utf-8")))
                if (p.rig_id != rig_id or abs(p.upper_arm - motion.upper_arm) > .01
                        or abs(p.forearm - motion.forearm) > .01
                        or abs(p.shoulder.x - motion.shoulder.x) > .01
                        or abs(p.shoulder.y - motion.shoulder.y) > .01):
                    problems.append(f"{name}: arm geometry does not match uploaded Spine rig")
        except Exception as exc:
            problems.append(f"{name}: {exc}")
    try:
        if len(clips) == len(expected):
            compile_film_v2(film, catalog, clips)
    except Exception as exc:
        problems.append(f"Timeline/continuity: {exc}")
    missing = [name for name in _required_assets(film, catalog) if not (path / name).is_file()]
    for item in _required_assets(film, catalog):
        filename = path / item
        if not filename.is_file():
            continue
        if item.endswith(".png"):
            try:
                with Image.open(filename) as im:
                    im.verify()
                if item.startswith("backgrounds/"):
                    with Image.open(filename) as im:
                        if im.size != (film.width, film.height):
                            problems.append(f"{item}: background must be {film.width}x{film.height} pixels")
            except Exception as exc:
                problems.append(f"{item}: invalid PNG ({exc})")
        if item.startswith("voices/"):
            try:
                with wave.open(str(filename), "rb") as wav:
                    if (wav.getnchannels(), wav.getsampwidth(), wav.getframerate()) != (1, 2, 24000):
                        problems.append(f"{item}: must be mono 24kHz PCM16 WAV")
                    shot = next(s for s in film.shots if s.narration and s.narration.wav == filename.name)
                    limit = shot.duration_frames - shot.narration.start_frame
                    if wav.getnframes() > limit * 1000:
                        problems.append(f"{item}: narration exceeds shot duration")
            except Exception as exc:
                problems.append(f"{item}: invalid WAV ({exc})")
    for shot in film.shots:
        for actor in shot.actors:
            clip = clips.get(actor.motion_id)
            if clip and len(clip["frames"]) >= 48:
                hands = [pose["hand"] for pose in clip["frames"]]
                distance = sum(((right["x"]-left["x"])**2+
                                 (right["y"]-left["y"])**2)**0.5
                               for left, right in zip(hands,hands[1:]))
                if distance < 4:
                    warnings.append(
                        f"{shot.shot_id}/{actor.actor_id}: almost static for "
                        f"{shot.duration_frames/24:.1f}s. Review acting/secondary motion."
                    )
                elif distance > 1800:
                    warnings.append(
                        f"{shot.shot_id}/{actor.actor_id}: very large wrist travel; "
                        "review pose speed and physical credibility."
                    )
    if any(s.continuity_break for s in film.shots):
        warnings.append("Intentional jump cut(s): review geographic/visual continuity manually.")
    if film.width * film.height > 1280 * 720:
        warnings.append("High resolution may exhaust headless browser GPU memory.")
    return {"ready": not problems and not missing, "errors": problems, "missing_assets": missing,
            "warnings": warnings, "frames": sum(s.duration_frames for s in film.shots),
            "shots": len(film.shots), "assets_required": len(_required_assets(film, catalog))}


class NewProject(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    template: str = Field(default="coffee", pattern=r"^(coffee|lost_key)$")


@router.get("/projects")
def projects() -> dict:
    PROJECTS.mkdir(parents=True, exist_ok=True)
    values = [_metadata(p) for p in PROJECTS.iterdir()
              if p.is_dir() and (p / "project.json").is_file()]
    return {"projects": sorted(values, key=lambda x: x["created_at"], reverse=True)}


@router.post("/projects", status_code=201)
def create_project(request: NewProject) -> dict:
    project_id = uuid.uuid4().hex
    path = PROJECTS / project_id
    path.mkdir(parents=True, exist_ok=False)
    template = "p6_v2" if request.template == "coffee" else "p7_lost_key"
    for kind, suffix in (("film", "film"), ("catalog", "catalog"), ("motions", "motions")):
        shutil.copyfile(REPO / "examples" / f"{template}_{suffix}.json", path / f"{kind}.json")
    info = {"id": project_id, "name": request.name, "template": request.template,
            "created_at": datetime.now(timezone.utc).isoformat()}
    _atomic_json(path / "project.json", info)
    return info


@router.get("/projects/{project_id}")
def project_details(project_id: str) -> dict:
    path = _project(project_id)
    return {**_metadata(path), "preflight": _preflight(path)}


@router.get("/projects/{project_id}/documents/{kind}")
def get_document(project_id: str, kind: str) -> dict:
    if kind not in KINDS:
        raise HTTPException(404, "Unknown director document")
    return json.loads((_project(project_id) / f"{kind}.json").read_text(encoding="utf-8"))


@router.put("/projects/{project_id}/documents/{kind}")
def save_document(project_id: str, kind: str, payload: dict) -> dict:
    if kind not in KINDS:
        raise HTTPException(404, "Unknown director document")
    try:
        if kind == "film":
            FilmPlanV2.model_validate(payload)
        elif kind == "catalog":
            AssetCatalog.model_validate(payload)
        else:
            if len(payload) > 120:
                raise HTTPException(422, "Too many motions")
            for name, value in payload.items():
                if not ID.fullmatch(name):
                    raise HTTPException(422, "Unsafe motion ID")
                MotionPlan.model_validate(value)
    except ValidationError as exc:
        raise HTTPException(422, detail=exc.errors(include_url=False)) from exc
    _atomic_json(_project(project_id) / f"{kind}.json", payload)
    return {"saved": True, "kind": kind}


@router.get("/projects/{project_id}/assets")
def project_assets(project_id: str) -> dict:
    root = _project(project_id)
    return {"files": [{"path": str(p.relative_to(root)).replace("\\", "/"), "bytes": p.stat().st_size}
                      for folder in ("rigs", "backgrounds", "props", "voices")
                      for p in (root / folder).rglob("*") if p.is_file()]}


@router.post("/projects/{project_id}/assets/{category}/{name}")
async def upload_asset(project_id: str, category: str, name: str, file: UploadFile = File(...)) -> dict:
    root = _project(project_id)
    if category not in {"backgrounds", "props", "voices"} or not FILE.fullmatch(name):
        raise HTTPException(422, "Invalid asset path")
    suffix = Path(name).suffix.lower()
    if suffix != (".wav" if category == "voices" else ".png"):
        raise HTTPException(422, "Unsupported asset file format")
    data = await file.read(MAX_ASSET_BYTES + 1)
    if not data or len(data) > MAX_ASSET_BYTES:
        raise HTTPException(413, "Asset empty or exceeds 32 MB limit")
    if suffix == ".png":
        # Normalize G-Labs PNG/JPEG/WebP outputs to the catalog's PNG contract.
        try:
            with Image.open(io.BytesIO(data)) as image:
                if image.format not in {"PNG", "JPEG", "WEBP"}:
                    raise ValueError("Only PNG, JPEG and WebP images are supported")
                if image.width * image.height > 24_000_000:
                    raise ValueError("Image pixel count exceeds safety limit")
                image.load()
                normalized = image.convert("RGBA") if image.has_transparency_data else image.convert("RGB")
                stream = io.BytesIO()
                normalized.save(stream, format="PNG")
                data = stream.getvalue()
        except Exception as exc:
            raise HTTPException(422, f"Invalid PNG/JPEG/WebP media: {exc}") from exc
    if suffix == ".wav" and not (data.startswith(b"RIFF") and data[8:12] == b"WAVE"):
        raise HTTPException(422, "Not a WAV audio file")
    dest = root / category / name
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(data)
    return {"saved": True, "path": f"{category}/{name}", "bytes": len(data)}


@router.post("/projects/{project_id}/rigs/{rig_id}/{name}")
async def upload_rig_file(project_id: str, rig_id: str, name: str, file: UploadFile = File(...)) -> dict:
    root = _project(project_id)
    if not ID.fullmatch(rig_id) or name not in {"skeleton.json", "skeleton.atlas", "skeleton.png", "rig_profile.json"}:
        raise HTTPException(422, "Invalid rig asset")
    data = await file.read(MAX_ASSET_BYTES + 1)
    if not data or len(data) > MAX_ASSET_BYTES:
        raise HTTPException(413, "Rig asset empty or too large")
    if name.endswith(".json"):
        try:
            json.loads(data.decode("utf-8"))
        except Exception as exc:
            raise HTTPException(422, "Invalid rig JSON") from exc
    if name.endswith(".png") and not data.startswith(b"\x89PNG\r\n\x1a\n"):
        raise HTTPException(422, "Rig texture must be PNG")
    dest = root / "rigs" / rig_id / name
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(data)
    return {"saved": True, "path": f"rigs/{rig_id}/{name}"}


@router.get("/projects/{project_id}/preflight")
def preflight(project_id: str) -> dict:
    return _preflight(_project(project_id))


@router.get("/projects/{project_id}/media/{category}/{name}")
def read_media(project_id: str, category: str, name: str):
    root = _project(project_id)
    if category not in {"backgrounds", "props"} or not FILE.fullmatch(name) or not name.endswith(".png"):
        raise HTTPException(404, "Media not found")
    path = root / category / name
    if not path.is_file():
        raise HTTPException(404, "Media not found")
    return FileResponse(path, media_type="image/png")


def _render_job(job_id: str, project_id: str, root: Path) -> None:
    with LOCK:
        info = JOBS[job_id]
        info["status"] = "running"
        try:
            film, catalog, _ = _documents(root)
            fixtures = REPO / "runtime" / "fixtures"
            for rig in catalog.rigs.values():
                source = root / "rigs" / rig.directory
                target = fixtures / rig.directory
                target.mkdir(parents=True, exist_ok=True)
                for name in ("skeleton.json", "skeleton.atlas", "skeleton.png", "rig_profile.json"):
                    shutil.copyfile(source / name, target / name)
            for asset in [*catalog.backgrounds.values(), *catalog.props.values()]:
                target = fixtures / asset.image
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(root / asset.image, target)
            voice_dir = root / "voices"
            output = root / "render" / "film.mp4"
            temp = root / "render" / "working"
            command = [sys.executable, str(REPO / "scripts" / "run_film_v2.py"),
                       "--plan", str(root / "film.json"),
                       "--catalog", str(root / "catalog.json"),
                       "--motions", str(root / "motions.json"),
                       "--voices", str(voice_dir), "--workspace", str(temp),
                       "--output", str(output)]
            completed = subprocess.run(command, cwd=REPO, text=True,
                                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                       timeout=2700, check=False)
            info["log"] = completed.stdout[-14000:]
            if completed.returncode != 0 or not output.is_file():
                raise RuntimeError(f"Renderer exited {completed.returncode}: {info['log'][-2500:]}")
            info["status"] = "completed"
            info["video_available"] = True
        except Exception as exc:
            info["status"] = "failed"
            info["error"] = str(exc)[-3000:]


@router.post("/projects/{project_id}/render", status_code=202)
def start_render(project_id: str) -> dict:
    root = _project(project_id)
    check = _preflight(root)
    if not check["ready"]:
        raise HTTPException(422, detail=check)
    if any(j["status"] in ("queued", "running") for j in JOBS.values()):
        raise HTTPException(409, "Another render is in progress")
    job_id = uuid.uuid4().hex
    job = {"id": job_id, "project_id": project_id, "status": "queued",
           "video_available": False, "error": None, "log": ""}
    JOBS[job_id] = job
    RUNNER.submit(_render_job, job_id, project_id, root)
    return job


@router.get("/jobs/{job_id}")
def get_job(job_id: str) -> dict:
    if job_id not in JOBS:
        raise HTTPException(404, "Job not found (jobs are in-memory for this local session)")
    job = dict(JOBS[job_id])
    if job["status"] == "running":
        folder = PROJECTS / job["project_id"] / "render" / "working" / "frames"
        job["rendered_frames"] = len(list(folder.glob("frame_*.png"))) if folder.is_dir() else 0
    return job


class GlabsAssetSubmit(BaseModel):
    asset_path: str = Field(pattern=r"^(backgrounds|props)/[a-z][a-z0-9_.-]*\.png$")
    prompt: str = Field(min_length=10, max_length=15000)
    model: str = "nano_banana_2"
    aspect_ratio: str = "16:9"
    allow_replace: bool = False


@router.get("/provider/glabs")
async def glabs_readiness() -> dict:
    if not os.environ.get("GLABS_API_KEY"):
        return {"configured": False, "reachable": False, "message": "GLABS_API_KEY not configured in backend environment"}
    try:
        async with GlabsClient.from_env() as client:
            response = await client.health()
        return {"configured": True, "reachable": True, "health": response}
    except Exception:
        return {"configured": True, "reachable": False, "message": "Local G-Labs webhook is not reachable"}


@router.post("/projects/{project_id}/images/generate", status_code=202)
async def glabs_generate_for_project(project_id: str, request: GlabsAssetSubmit) -> dict:
    """Only an explicit user request may consume G-Labs image generation quota."""
    root = _project(project_id)
    _, catalog, _ = _documents(root)
    allowed = {asset.image for asset in (*catalog.backgrounds.values(), *catalog.props.values())}
    if request.asset_path not in allowed:
        raise HTTPException(422, "Requested image is not declared in this project's catalog")
    destination = root / request.asset_path
    if destination.exists() and not request.allow_replace:
        raise HTTPException(409, "Image already exists. Explicitly allow replacement to regenerate")
    metadata_folder = root / "glabs_tasks"
    for task in metadata_folder.glob("*.json"):
        try:
            prior = json.loads(task.read_text(encoding="utf-8"))
        except (ValueError, OSError):
            continue
        if prior.get("asset_path") == request.asset_path and prior.get("status") in {"pending", "running"}:
            raise HTTPException(409, "An image generation for this asset is already active")
    try:
        image_request = ImageRequest(prompt=request.prompt, model=request.model, aspect_ratio=request.aspect_ratio)
        async with GlabsClient.from_env() as client:
            task_id = await client.submit(image_request)
    except Exception as exc:
        raise HTTPException(503, "G-Labs submission failed. Check local MAX webhook and backend credentials.") from exc
    record = {"task_id": task_id, "asset_path": request.asset_path,
              "status": "pending", "allow_replace": request.allow_replace}
    _atomic_json(metadata_folder / (task_id + ".json"), record)
    return record


@router.get("/projects/{project_id}/images/tasks/{task_id}")
async def glabs_project_task(project_id: str, task_id: str) -> dict:
    root = _project(project_id)
    if not re.fullmatch(r"[0-9a-fA-F]{8}", task_id):
        raise HTTPException(404, "Unknown image task ID")
    task = root / "glabs_tasks" / (task_id.lower() + ".json")
    if not task.is_file():
        raise HTTPException(404, "Task not owned by this project")
    record = json.loads(task.read_text(encoding="utf-8"))
    if record["status"] == "completed":
        return record
    try:
        async with GlabsClient.from_env() as client:
            provider = await client.status(task_id.lower())
            status = provider.get("status")
            if status == "completed":
                results = provider.get("results")
                if not isinstance(results, list) or not results or not isinstance(results[0], str):
                    raise ValueError("Completed G-Labs result missing image URL")
                destination = root / record["asset_path"]
                if destination.exists() and not record.get("allow_replace"):
                    raise ValueError("Destination exists; overwrite not approved")
                tmp = root / "glabs_tasks" / (task_id.lower() + ".result")
                try:
                    await client.download(results[0], tmp)
                    if tmp.stat().st_size > MAX_ASSET_BYTES:
                        raise ValueError("G-Labs image exceeds local upload size limit")
                    with Image.open(tmp) as im:
                        if im.width * im.height > 24_000_000:
                            raise ValueError("G-Labs image exceeds pixel safety limit")
                        normalized = im.convert("RGBA") if im.has_transparency_data else im.convert("RGB")
                        destination.parent.mkdir(parents=True, exist_ok=True)
                        normalized.save(destination, format="PNG")
                finally:
                    tmp.unlink(missing_ok=True)
            record["status"] = status
            if status == "failed":
                record["error"] = "G-Labs reported a failed task"
            _atomic_json(task, record)
            return record
    except Exception as exc:
        raise HTTPException(502, "Unable to retrieve/import G-Labs image; task remains tracked locally") from exc


@router.post("/projects/{project_id}/bootstrap-demo")
def generate_demo_assets(project_id: str) -> dict:
    """Explicit, free, local synthetic integration fixture. NEVER uses G-Labs or Kokoro.

    Requires the pinned Genielabs scripts installed by setup_studio.bat.
    Saves fixtures inside THIS project's asset directory.
    """
    root = _project(project_id)
    vendor = REPO / "vendor" / "genielabs"
    required = [vendor / "scripts" / "build_spine_json.py",
                vendor / "scripts" / "make_atlas.py"]
    if any(not p.is_file() for p in required):
        raise HTTPException(422, "Pinned Genielabs scripts missing. Run setup_studio.bat first.")
    from scripts.p4_spine_fixture import produce
    from scripts.p6_fixture_voice import main as demo_audio
    from scripts.p6_v2_fixture_assets import generate as cafe_images
    from scripts.p7_lost_key_fixture_assets import generate as lost_key_images

    info = _metadata(root)
    source = "coffee" if info["template"] == "coffee" else "lost_key"
    catalog = AssetCatalog.model_validate_json((root / "catalog.json").read_text(encoding="utf-8"))
    if set(catalog.rigs) - {"baseline", "compact"}:
        raise HTTPException(422, "Demo generation only supports baseline/compact synthetic rigs")
    for rig_id, rig in catalog.rigs.items():
        staging = root / "demo_generated" / rig_id
        produce(vendor, staging, rig_id)
        target = root / "rigs" / rig.directory
        target.mkdir(parents=True, exist_ok=True)
        for name in ("skeleton.json", "skeleton.atlas", "skeleton.png", "rig_profile.json"):
            shutil.copyfile(staging / name, target / name)
    if source == "coffee":
        cafe_images(root)
    else:
        lost_key_images(root)
    demo_audio(root / "voices")
    return {"demo": True, "message": "Synthetic fixture only; WAV files contain tones, not speech.",
            "preflight": _preflight(root)}


@router.get("/projects/{project_id}/video")
def download_video(project_id: str):
    video = _project(project_id) / "render" / "film.mp4"
    if not video.is_file():
        raise HTTPException(404, "No rendered MP4")
    return FileResponse(video, media_type="video/mp4", filename="animation.mp4", content_disposition_type="inline")
