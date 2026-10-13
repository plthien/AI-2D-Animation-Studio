"""Compact coverage: world anchors, rotated socket and two actual rig profiles."""
import json
import pytest
from pydantic import ValidationError

from studio.motion import MotionError, MotionPlan, Point
from studio.retarget import RigProfile
from studio.world import WorldProp, socket_offset, wrist_for_prop, compile_world_motion
from tests.test_retarget import BASE, OTHER, SKELETON


WORLD = {"prop_id": "coffee-cup", "initial": {"x":270,"y":195},
         "destination": {"x":286,"y":195}, "grip_offset": {"x":-16,"y":0},
         "initial_angle_deg":0,"carry_angle_deg":25,"final_angle_deg":0}


def test_fixed_world_coordinates_two_rigs():
    source=MotionPlan.model_validate(json.loads((__import__('pathlib').Path(__file__).parents[1]/'examples/p4_coffee_motion.json').read_text()))
    obj=WorldProp.model_validate(WORLD)
    baseline=compile_world_motion(source,RigProfile.model_validate(BASE),SKELETON,obj)
    compact_skeleton=json.loads(json.dumps(SKELETON))
    compact_skeleton["bones"][1]["x"]=70
    compact_skeleton["bones"][2]["x"]=65
    compact=compile_world_motion(source,RigProfile.model_validate(OTHER),compact_skeleton,obj)
    for c in (baseline,compact):
        assert c["retarget"]["mode"]=="world_fixed_prop"
        assert c["frames"][0]["prop"]=={"x":270.0,"y":195.0}
        assert c["frames"][-1]["prop"]["x"]==pytest.approx(286,abs=0.001)
        assert c["frames"][-1]["prop"]["y"]==pytest.approx(195,abs=0.001)
        assert c["frames"][-1]["prop_state"]=="free"
        assert c["frames"][12]["prop_state"]=="held"
        assert c["frames"][12]["prop"]=={"x":270.0,"y":195.0}
        for frame in c["frames"]:
            if frame["prop_state"]=="held":
                offset=socket_offset(obj.grip_offset, frame["prop_rotation_deg"])
                assert frame["prop"]["x"]==pytest.approx(frame["hand"]["x"]+offset.x)
                assert frame["prop"]["y"]==pytest.approx(frame["hand"]["y"]+offset.y)
    assert compact["frames"][11]["hand"]==baseline["frames"][11]["hand"]
    assert compact["frames"][0]["hand"]!=baseline["frames"][0]["hand"]
    assert compact["frames"][27]["prop_rotation_deg"]==pytest.approx(25)
    assert compact["frames"][15]["prop_rotation_deg"]==pytest.approx(0)
    assert compact["frames"][32]["prop_rotation_deg"]==pytest.approx(25)
    assert wrist_for_prop(obj.initial,obj.grip_offset,0)==Point(x=286,y=195)


def test_socket_rotation():
    pt=socket_offset(Point(x=-16,y=0),90)
    assert pt.x==pytest.approx(0,abs=1e-10)
    assert pt.y==pytest.approx(-16)
    result=wrist_for_prop(Point(x=270,y=195),Point(x=-16,y=0),90)
    assert result.x==pytest.approx(270,abs=1e-10)
    assert result.y==pytest.approx(211,abs=1e-10)


@pytest.mark.parametrize("actions",[
    [{"kind":"wait","start":0,"end":4}],
    [{"kind":"grab","start":0,"end":0},{"kind":"reach","start":1,"end":1,"target":{"x":286,"y":195}},
     {"kind":"place","start":2,"end":4,"target":{"x":302,"y":195}}],
])
def test_world_rejects_unsupported_action_structure(actions):
    source=MotionPlan.model_validate({"fps":24,"frames":5,"shoulder":{"x":140,"y":165},
        "rest_hand":{"x":212,"y":165},"upper_arm":90,"forearm":80,
        "initial_prop":{"x":270,"y":195},"grip_offset":{"x":-16,"y":0},"actions":actions})
    with pytest.raises(MotionError,match="World contact"):
        compile_world_motion(source,RigProfile.model_validate(BASE),SKELETON,WorldProp.model_validate(WORLD))


def test_world_unreachable_and_endpoint_fail_closed():
    obj=WorldProp.model_validate({**WORLD,"initial":{"x":600,"y":195}})
    with pytest.raises(MotionError,match="reach"):
        compile_world_motion(MotionPlan.model_validate(json.loads((__import__("pathlib").Path(__file__).parents[1]/"examples/p4_coffee_motion.json").read_text())),RigProfile.model_validate(BASE),SKELETON,obj)
    # An invalid schema is rejected at the manual-AI boundary.
    with pytest.raises(ValidationError):
        WorldProp.model_validate({**WORLD,"prop_id":""})
