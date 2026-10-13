import json
from pathlib import Path
import pytest
from studio.rigging import RigError, build_rig_config, write_rig_config, run_genielabs_builder

LAYOUT = {"canvas_width": 100, "canvas_height": 200,
          "parts": {"body": {"x":20, "y":60, "width":60, "height":100},
                    "face": {"x":30, "y":10, "width":40, "height":40}}}
LABELS = {"body":"torso", "face":"head"}
ANCHORS = {"torso":{"x":50,"y":85},"head":{"x":50,"y":30}}

def test_build_and_write(tmp_path):
    result = build_rig_config(LAYOUT,LABELS,ANCHORS,["idle"])
    assert result["bones"][1]["name"] == "torso"
    assert result["bones"][2]["parent"] == "torso"
    assert result["attachments"]["face"]["width"] == 40
    for name, obj in [("layout",LAYOUT),("semantic",LABELS),("anchors",ANCHORS)]:
        (tmp_path/f"{name}.json").write_text(json.dumps(obj))
    p=write_rig_config(tmp_path/"layout.json",tmp_path/"semantic.json",tmp_path/"anchors.json",tmp_path/"rig.json",["walk"])
    assert json.loads(p.read_text())["animations"] == ["walk"]

@pytest.mark.parametrize("layout,labels,anchors,animations",[
    ({},LABELS,ANCHORS,["idle"]),
    (LAYOUT,{"body":"torso"},ANCHORS,["idle"]),
    (LAYOUT,{"body":"torso","face":"torso"},ANCHORS,["idle"]),
    (LAYOUT,{"body":"torso","face":"??? "},ANCHORS,["idle"]),
    (LAYOUT,{"body":"torso","face":"left_forearm"},ANCHORS,["idle"]),
    (LAYOUT,LABELS,{"torso":{"x":50,"y":85}},["idle"]),
    (LAYOUT,LABELS,{"torso":{"x":50,"y":85},"head":{"x":150,"y":5}},["idle"]),
    (LAYOUT,LABELS,{"torso":{"x":50,"y":85},"head":{"x":"oops","y":5}},["idle"]),
    (LAYOUT,LABELS,ANCHORS,["spin"]),
    ({"canvas_width":100,"canvas_height":200,"parts":{"body":{"x":1,"y":1,"width":0,"height":2},"face":LAYOUT["parts"]["face"]}},LABELS,ANCHORS,["idle"]),
    ({"canvas_width":100,"canvas_height":200,"parts":{"body":{"x":1,"y":1,"width":2},"face":LAYOUT["parts"]["face"]}},LABELS,ANCHORS,["idle"]),
])
def test_invalid_rig_rejected(layout,labels,anchors,animations):
    with pytest.raises(RigError):
        build_rig_config(layout,labels,anchors,animations)

def test_builder_requires_inputs(tmp_path):
    with pytest.raises(FileNotFoundError):
        run_genielabs_builder(tmp_path,tmp_path/"missing.json",tmp_path/"output.json")


def test_no_duplicate_head_and_root_attachment_alignment():
    config = build_rig_config(LAYOUT, LABELS, ANCHORS, ["idle"])
    names = [bone["name"] for bone in config["bones"]]
    assert len(names) == len(set(names))
    assert names == ["root", "torso", "head"]
    assert len(config["slots"]) == 2
    assert config["attachments"]["face"]["y"] == 0
