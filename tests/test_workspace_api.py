"""Local cockpit API tests; job renderer subprocess is not invoked in unit tests."""
from io import BytesIO
import json
import wave

from fastapi.testclient import TestClient
import pytest
from PIL import Image

from studio.api import app
import studio.workspace_api as ws


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(ws, "PROJECTS", tmp_path / "projects")
    return TestClient(app)


def make_project(client):
    response = client.post("/studio/projects", json={"name": "My first film", "template": "coffee"})
    assert response.status_code == 201
    return response.json()["id"]


def png(width=640, height=480):
    buffer=BytesIO()
    Image.new("RGB",(width,height),"#eeeeaa").save(buffer,format="PNG")
    return buffer.getvalue()


def wav(seconds=2):
    buffer=BytesIO()
    with wave.open(buffer, "wb") as data:
        data.setnchannels(1)
        data.setsampwidth(2)
        data.setframerate(24000)
        data.writeframes(b"\x00\x00" * (24000 * seconds))
    return buffer.getvalue()


def test_project_crud_director_read_and_validated_write(client):
    project_id=make_project(client)
    index=client.get("/studio/projects").json()["projects"]
    assert len(index)==1 and index[0]["id"]==project_id
    details=client.get(f"/studio/projects/{project_id}").json()
    assert details["preflight"]["ready"] is False
    film=client.get(f"/studio/projects/{project_id}/documents/film").json()
    assert film["schema_version"]=="film.v2" and len(film["shots"])==5
    film["shots"][0]["camera"]["zoom"]=1.1
    assert client.put(f"/studio/projects/{project_id}/documents/film",json=film).status_code==200
    assert client.get(f"/studio/projects/{project_id}/documents/film").json()["shots"][0]["camera"]["zoom"]==1.1
    film["shots"][0]["duration_frames"]=0
    assert client.put(f"/studio/projects/{project_id}/documents/film",json=film).status_code==422
    assert client.get("/studio/projects/not-a-real-id").status_code==404
    assert client.get(f"/studio/projects/{project_id}/documents/unknown").status_code==404
    assert client.get("/studio/jobs/not-found").status_code==404


def test_assets_upload_read_and_quality_preflight(client):
    project_id=make_project(client)
    url=f"/studio/projects/{project_id}"
    assert client.get(url+"/preflight").json()["ready"] is False
    response=client.post(url+"/assets/backgrounds/cafe_morning.png",
      files={"file":("test.png",png(),"image/png")})
    assert response.status_code==200
    assert client.get(url+"/media/backgrounds/cafe_morning.png").status_code==200
    assert client.get(url+"/media/backgrounds/missing.png").status_code==404
    assert client.post(url+"/assets/backgrounds/wrong.png",
      files={"file":("x.png",b"fake","image/png")}).status_code==422
    assert client.post(url+"/assets/voices/shot_01.wav",
      files={"file":("voice.wav",wav(),"audio/wav")}).status_code==200
    assert any(x["path"]=="voices/shot_01.wav" for x in client.get(url+"/assets").json()["files"])
    assert client.post(url+"/rigs/baseline/skeleton.json",
      files={"file":("a.json",b'{"bones":[]}',"application/json")}).status_code==200
    assert client.post(url+"/rigs/baseline/skeleton.png",
      files={"file":("a.png",png(64,64),"image/png")}).status_code==200
    assert client.post(url+"/rigs/baseline/rig_profile.json",
      files={"file":("bad.json",b"not json","application/json")}).status_code==422
    assert client.post(url+"/rigs/../skeleton.atlas",
      files={"file":("a.atlas",b"atlas","text/plain")}).status_code in (404,422)
    assert client.get(url+"/preflight").json()["missing_assets"]
    assert client.post(url+"/render").status_code==422
    assert client.get(url+"/video").status_code==404


def test_story_b_import_and_motion_boundary(client):
    p=client.post("/studio/projects",json={"name":"Different story","template":"lost_key"}).json()["id"]
    root=f"/studio/projects/{p}"
    film=client.get(root+"/documents/film").json()
    assert film["shots"][0]["background_id"]=="workshop_sunrise"
    motions=client.get(root+"/documents/motions").json()
    motions["key_scan"]["frames"]=0
    assert client.put(root+"/documents/motions",json=motions).status_code==422
    motions["key_scan"]["frames"]=72
    assert client.put(root+"/documents/motions",json=motions).status_code==200
    assert client.get(root+"/preflight").json()["frames"]==504
    assert client.post(root+"/assets/voices/../invalid.wav",
        files={"file":("x.wav",wav(),"audio/wav")}).status_code in (404,422)


def test_jpeg_asset_normalized_to_png_for_film_catalog(client):
    project_id=make_project(client)
    jpg=BytesIO()
    Image.new("RGB",(640,480),"#2c899a").save(jpg,format="JPEG")
    url=f"/studio/projects/{project_id}"
    result=client.post(url+"/assets/backgrounds/cafe_evening.png",
      files={"file":("glabs-result.jpg",jpg.getvalue(),"image/jpeg")})
    assert result.status_code==200
    response=client.get(url+"/media/backgrounds/cafe_evening.png")
    assert response.status_code==200 and response.content.startswith(b"\x89PNG\r\n\x1a\n")
    with Image.open(BytesIO(response.content)) as im:
        assert im.size==(640,480) and im.format=="PNG"


def test_glabs_project_task_explicit_submit_import_and_idempotent_poll(client, monkeypatch, tmp_path):
    class FakeClient:
        @classmethod
        def from_env(cls):
            return cls()
        async def __aenter__(self):
            return self
        async def __aexit__(self, *args):
            return None
        async def submit(self, request):
            assert request.prompt.startswith("Clean 2D")
            return "aabbccdd"
        async def status(self, task_id):
            assert task_id == "aabbccdd"
            return {"status":"completed", "results":["http://127.0.0.1:8765/api/files/generated.png"]}
        async def download(self, url, destination):
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(png())
            return destination
    monkeypatch.setattr(ws, "GlabsClient", FakeClient)
    project_id=make_project(client)
    url=f"/studio/projects/{project_id}"
    submitted=client.post(url+"/images/generate",json={
      "asset_path":"backgrounds/cafe_morning.png",
      "prompt":"Clean 2D cartoon morning cafe illustration",
      "model":"nano_banana_2","aspect_ratio":"16:9"})
    assert submitted.status_code==202 and submitted.json()["task_id"]=="aabbccdd"
    assert client.post(url+"/images/generate",json={
      "asset_path":"backgrounds/cafe_morning.png",
      "prompt":"Clean 2D cartoon morning cafe illustration"}).status_code==409
    result=client.get(url+"/images/tasks/aabbccdd")
    assert result.status_code==200 and result.json()["status"]=="completed"
    assert client.get(url+"/images/tasks/aabbccdd").status_code==200
    image=client.get(url+"/media/backgrounds/cafe_morning.png")
    assert image.content.startswith(b"\x89PNG\r\n\x1a\n")
    assert client.get(url+"/images/tasks/bad").status_code==404
    assert client.post(url+"/images/generate",json={
      "asset_path":"backgrounds/not_catalog.png",
      "prompt":"Clean 2D cartoon unknown asset"}).status_code==422
