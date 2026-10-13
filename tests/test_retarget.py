"""Small focused branch/geometry suite; browser CI covers actual Spine integration."""
import json

import pytest
from pydantic import ValidationError

from studio.motion import MotionError, MotionPlan
from studio.retarget import BoneRoles, RigProfile, compile_retargeted, compile_retargeted_file, retarget_motion, validate_spine_profile


SOURCE = {
    "fps":24, "frames":5, "shoulder":{"x":140,"y":165},
    "rest_hand":{"x":212,"y":165}, "upper_arm":90, "forearm":80,
    "initial_prop":{"x":270,"y":195}, "grip_offset":{"x":-16,"y":0},
    "actions":[
        {"kind":"reach","start":0,"end":1,"target":{"x":286,"y":195}},
        {"kind":"grab","start":2,"end":2},
        {"kind":"place","start":3,"end":4,"target":{"x":302,"y":195}},
    ],
}
BASE = {
    "rig_id":"baseline", "bones":{"upper_arm":"left-upper-arm","forearm":"left-lower-arm","hand":"left-hand"},
    "actor_origin":{"x":320,"y":480}, "shoulder":{"x":140,"y":165},
    "upper_arm":90,"forearm":80,"grip_offset":{"x":-16,"y":0},
}
OTHER = {**BASE,"rig_id":"compact","shoulder":{"x":175,"y":185},"upper_arm":70,"forearm":65}
SKELETON = {"bones":[
    {"name":"left-upper-arm","parent":"torso","x":0,"y":0},
    {"name":"left-lower-arm","parent":"left-upper-arm","x":90,"y":0},
    {"name":"left-hand","parent":"left-lower-arm","x":80,"y":0},
]}


def test_both_rigs_use_identical_authored_motion():
    source=MotionPlan.model_validate(SOURCE)
    first=compile_retargeted(source,RigProfile.model_validate(BASE),SKELETON)
    compact_skeleton=json.loads(json.dumps(SKELETON))
    compact_skeleton["bones"][1]["x"]=70
    compact_skeleton["bones"][2]["x"]=65
    second=compile_retargeted(source,RigProfile.model_validate(OTHER),compact_skeleton)
    assert first["frames"][1]["hand"]=={"x":286.0,"y":195.0}
    assert first["retarget"]["reach_scale"]==1.0
    assert second["retarget"]["reach_scale"]==pytest.approx(135/170)
    assert [f["phase"] for f in first["frames"]]==[f["phase"] for f in second["frames"]]
    for a,b in zip(first["frames"],second["frames"]):
        for axis in ("x","y"):
            s=(a["hand"][axis]-BASE["shoulder"][axis])/170
            t=(b["hand"][axis]-OTHER["shoulder"][axis])/135
            assert s==pytest.approx(t,abs=1e-10)
        if b["prop_state"]=="held":
            assert b["prop"]["x"]-b["hand"]["x"]==-16
            assert b["prop"]["y"]==b["hand"]["y"]
    assert first["frames"][-1]["prop_state"]=="free"
    assert second["frames"][-1]["prop_state"]=="free"


def test_roundtrip_profile_file(tmp_path):
    motion=tmp_path/"motion.json"
    profile=tmp_path/"profile.json"
    skeleton=tmp_path/"skeleton.json"
    motion.write_text(json.dumps(SOURCE))
    profile.write_text(json.dumps(BASE))
    skeleton.write_text(json.dumps(SKELETON))
    path=compile_retargeted_file(motion,profile,skeleton,tmp_path/"output"/"poses.json")
    assert json.loads(path.read_text())["rig"]["rig_id"]=="baseline"


@pytest.mark.parametrize("rig,skeleton,error",[
    (BASE,{"bones":[]}, "missing"),
    (BASE,{"bones":[SKELETON["bones"][0],{**SKELETON["bones"][1],"parent":"root"},SKELETON["bones"][2]]},"hierarchy"),
    (BASE,{"bones":[SKELETON["bones"][0],{**SKELETON["bones"][1],"x":89},SKELETON["bones"][2]]},"lengths"),
    (BASE,{"bones":[SKELETON["bones"][0],{**SKELETON["bones"][1],"y":1},SKELETON["bones"][2]]},"zero-offset"),
    (BASE,{"bones":[SKELETON["bones"][0],{**SKELETON["bones"][1],"rotation":5},SKELETON["bones"][2]]},"neutral setup"),
    (BASE,{"bones":[SKELETON["bones"][0],{**SKELETON["bones"][1],"scaleX":0.8},SKELETON["bones"][2]]},"neutral setup"),
])
def test_reject_mismatched_actual_rig(rig,skeleton,error):
    with pytest.raises(MotionError,match=error):
        validate_spine_profile(RigProfile.model_validate(rig),skeleton)


def test_unreachable_nonuniform_proportions_fail_closed():
    skeleton=json.loads(json.dumps(SKELETON))
    skeleton["bones"][1]["x"]=130
    skeleton["bones"][2]["x"]=5
    wrong={**OTHER,"upper_arm":130,"forearm":5}
    with pytest.raises(MotionError,match="reach"):
        compile_retargeted(MotionPlan.model_validate(SOURCE),RigProfile.model_validate(wrong),skeleton)


@pytest.mark.parametrize("invalid",[
    {"bones":{"upper_arm":"a","forearm":"a","hand":"b"}},
    {"rig_id":""},
    {"forearm":0},
    {"schema_version":"2.0"},
])
def test_invalid_profile(invalid):
    with pytest.raises(ValidationError):
        RigProfile.model_validate({**BASE,**invalid})
