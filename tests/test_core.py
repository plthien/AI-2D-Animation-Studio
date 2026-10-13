"""Small, parameterized suites: branch coverage matters, not test count."""
import json
from pathlib import Path

import httpx
import pytest
from pydantic import ValidationError
from studio.glabs import GlabsClient, ImageRequest, WebhookError
from studio.handoff import Action, Shot, AnimationPlan, export_task, import_plan


@pytest.mark.parametrize("field,value", [
    ("model", "invalid"), ("aspect_ratio", "2:5"),
    ("reference_images", [{"data":"a", "path":"b"}]),
    ("reference_images", [{}]),
    ("reference_images", [{"path":"a"}] * 11),
    ("upscale", ["3K"]), ("upscale", ["2K", "2K"]),
])
def test_image_rejects_invalid(field, value):
    with pytest.raises(ValidationError):
        ImageRequest(prompt="test", **{field: value})


def test_request_defaults():
    r = ImageRequest(prompt="test", reference_images=[{"path": "C:/reference.png"}], upscale=["2K"])
    assert r.model == "nano_banana_2"
    assert r.reference_images[0]["path"].endswith(".png")


@pytest.mark.parametrize("bad", ["https://localhost:8765", "http://", "http://user:pass@localhost:8765", "http://localhost:8765/other", "http://localhost:8765?q=1"])
def test_bad_host(bad):
    with pytest.raises(ValueError):
        GlabsClient(bad, "key")


def test_missing_key():
    with pytest.raises(ValueError):
        GlabsClient("http://localhost:8765", "")


@pytest.mark.asyncio
async def test_glabs_cycle(tmp_path):
    responses = iter(["pending", "running", "completed"])
    def handler(req):
        if req.url.path == "/api/image/generate":
            return httpx.Response(202, json={"task_id":"abc12345"})
        if req.url.path == "/api/status/abc12345":
            state = next(responses)
            return httpx.Response(200, json={"status":state,"results":["http://localhost:8765/api/files/one.png"] if state == "completed" else []})
        if req.url.path == "/api/files/one.png":
            return httpx.Response(200, content=b"\x89PNG\r\n\x1a\nTEST")
        if req.url.path == "/api/health":
            return httpx.Response(200, json={"status":"ok"})
        if req.url.path == "/api/stop/abc12345":
            return httpx.Response(200)
        return httpx.Response(404)
    async with GlabsClient("http://localhost:8765", "key", httpx.MockTransport(handler)) as client:
        assert (await client.health())["status"] == "ok"
        task = await client.submit(ImageRequest(prompt="test"))
        result = await client.wait(task, max_polls=3, interval=0)
        assert result["status"] == "completed"
        assert (await client.download(result["results"][0], tmp_path/"image.png")).is_file()
        await client.cancel(task)


@pytest.mark.parametrize("response,status", [
    ({"task_id":"xyz"},202), ({},202), ({"task_id":"aa"},200),
])
@pytest.mark.asyncio
async def test_submit_bad(response,status):
    async with GlabsClient("http://localhost:8765","key",httpx.MockTransport(lambda _: httpx.Response(status,json=response))) as client:
        with pytest.raises(WebhookError):
            await client.submit(ImageRequest(prompt="test"))


@pytest.mark.parametrize("state", ["bad", "failed", "completed", "pending"])
@pytest.mark.asyncio
async def test_status_and_wait_errors(state):
    def handle(req):
        return httpx.Response(200,json={"status":state,"error":"failure"})
    async with GlabsClient("http://localhost:8765","key",httpx.MockTransport(handle)) as client:
        if state == "bad":
            with pytest.raises(WebhookError):
                await client.status("abc")
        elif state == "pending":
            with pytest.raises(TimeoutError):
                await client.wait("abc",max_polls=1,interval=0)
        else:
            with pytest.raises(WebhookError):
                await client.wait("abc",max_polls=1,interval=0)


@pytest.mark.asyncio
async def test_wait_bad_bounds():
    async with GlabsClient("http://localhost:8765","key",httpx.MockTransport(lambda _: httpx.Response(200,json={}))) as client:
        with pytest.raises(ValueError):
            await client.wait("a",max_polls=0)
        with pytest.raises(ValueError):
            await client.wait("a",interval=-1)


@pytest.mark.parametrize("url", [
    "http://evil.test/api/files/a.png",
    "https://localhost:8765/api/files/a.png",
    "http://localhost:8765/api/result/a",
    "http://localhost:8765/api/files/%2fetc",
    "http://localhost:8765/api/files/",
])
def test_download_url_rejected(url):
    client=GlabsClient("http://localhost:8765","key")
    with pytest.raises(WebhookError):
        client._file_path(url)


@pytest.mark.asyncio
async def test_download_bad_content(tmp_path):
    async with GlabsClient("http://localhost:8765","key",httpx.MockTransport(lambda _: httpx.Response(200,content=b"not image"))) as client:
        with pytest.raises(WebhookError):
            await client.download("http://localhost:8765/api/files/a.png",tmp_path/"a.png")


@pytest.mark.parametrize("kwargs", [
    {"start_frame":2,"end_frame":1},
    {"start_frame":-1,"end_frame":0},
])
def test_action_rejected(kwargs):
    with pytest.raises(ValidationError):
        Action(type="idle",**kwargs)


@pytest.mark.parametrize("duration,actions",[
    (0,[]), (2,[Action(type="idle",start_frame=0,end_frame=2)]),
])
def test_shot_rejected(duration,actions):
    with pytest.raises(ValidationError):
        Shot(shot_id="S1",duration_frames=duration,actions=actions)


def test_plan_roundtrip_and_export(tmp_path):
    plan={"schema_version":"1.0","fps":24,"shots":[{"shot_id":"S1","duration_frames":3,"actions":[{"type":"idle","start_frame":0,"end_frame":2}]}]}
    p=tmp_path/"plan.json"
    p.write_text(json.dumps(plan))
    assert import_plan(p).shots[0].actions[0].type == "idle"
    dst=export_task("Make an idle shot",{},tmp_path/"prompt.txt")
    assert "Make an idle shot" in dst.read_text()


def test_duplicate_shots():
    s=Shot(shot_id="S1",duration_frames=1)
    with pytest.raises(ValidationError):
        AnimationPlan(fps=24,shots=[s,s])


def test_motion_prompt_export_and_validation(tmp_path):
    from studio.handoff import export_motion_task
    path=export_motion_task("Make the actor catch the cup",{"character_id":"test"},tmp_path/"prompts"/"motion_task.txt")
    text=path.read_text()
    assert "Make the actor catch the cup" in text
    assert "character_id" in text
    assert "frames-1" in text
    with pytest.raises(ValueError,match="empty"):
        export_motion_task("    ",{},tmp_path/"bad.txt")


def test_motion_api_accepts_valid_plan_and_rejects_unreachable(tmp_path,monkeypatch):
    from fastapi.testclient import TestClient
    from studio.api import app
    from tests.test_motion import BASE
    monkeypatch.setenv("STUDIO_OUTPUT_ROOT",str(tmp_path))
    client=TestClient(app)
    prompt=client.post("/handoff/motion/export",json={"prompt":"Catch a cup","catalog":{}})
    assert prompt.status_code==200
    assert (tmp_path/"motion_task.txt").is_file()
    assert client.post("/handoff/motion/export",json={"prompt":"  ","catalog":{}}).status_code==422
    response=client.post("/motion/compile",json=BASE)
    assert response.status_code==200 and len(response.json()["frames"])==5
    bad={**BASE,"rest_hand":{"x":99,"y":99}}
    response=client.post("/motion/compile",json=bad)
    assert response.status_code==422 and "reach" in str(response.json())


def test_retarget_endpoint_and_fail_closed():
    from fastapi.testclient import TestClient
    from studio.api import app
    from tests.test_retarget import BASE, SKELETON, SOURCE
    client=TestClient(app)
    payload={"plan":SOURCE,"profile":BASE,"skeleton":SKELETON}
    good=client.post("/motion/retarget",json=payload)
    assert good.status_code==200
    assert good.json()["rig"]["rig_id"]=="baseline"
    assert len(good.json()["frames"])==5
    broken={**payload,"skeleton":{"bones":[]}}
    bad=client.post("/motion/retarget",json=broken)
    assert bad.status_code==422 and "missing" in str(bad.json())
