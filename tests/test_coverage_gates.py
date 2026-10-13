"""Target uncovered first-party branches; no duplicate large UT suite."""
import json
from pathlib import Path
from unittest.mock import patch
import httpx
import pytest
from pydantic import ValidationError
from studio.glabs import GlabsClient, ImageRequest, WebhookError
from studio.rigging import build_rig_config, run_genielabs_builder, RigError
from tests.test_rigging import LAYOUT, LABELS, ANCHORS

@pytest.mark.parametrize("field,value", [("model","bad"),("aspect_ratio","bad")])
def test_field_validation(field,value):
    with pytest.raises(ValidationError):
        ImageRequest(prompt="ok",**{field:value})

def test_client_from_environment(monkeypatch):
    monkeypatch.setenv("GLABS_BASE_URL","http://localhost:8765")
    monkeypatch.setenv("GLABS_API_KEY","local-secret")
    client=GlabsClient.from_env()
    assert client.origin=="http://localhost:8765"

@pytest.mark.asyncio
async def test_status_early_success():
    def respond(request):
        if request.url.path.endswith("/api/status/abcd1234"):
            return httpx.Response(200,json={"status":"completed","results":["http://localhost:8765/api/files/a.png"]})
        return httpx.Response(404)
    async with GlabsClient("http://localhost:8765","secret",httpx.MockTransport(respond)) as client:
        assert (await client.wait("abcd1234",max_polls=2,interval=0))["status"]=="completed"

def test_missing_parent_branch():
    layout={**LAYOUT,"parts":{**LAYOUT["parts"],"arm":{"x":9,"y":60,"width":10,"height":20}}}
    labels={**LABELS,"arm":"left_forearm"}
    anchors={**ANCHORS,"left_forearm":{"x":10,"y":65}}
    with pytest.raises(RigError,match="parent"):
        build_rig_config(layout,labels,anchors,["idle"])

def test_builder_runs_mock_and_checks_output(tmp_path,monkeypatch):
    root=tmp_path/"upstream"
    (root/"scripts").mkdir(parents=True)
    (root/"scripts"/"build_spine_json.py").write_text("print('test')")
    config=tmp_path/"config.json"
    config.write_text("{}")
    output=tmp_path/"out.json"
    def success_run(argv,check):
        output.write_text("{}")
    with patch("studio.rigging.subprocess.run",side_effect=success_run) as called:
        assert run_genielabs_builder(root,config,output)==output
        called.assert_called_once()
    output.unlink()
    with patch("studio.rigging.subprocess.run",return_value=None):
        with pytest.raises(RuntimeError,match="without skeleton"):
            run_genielabs_builder(root,config,output)
