"""Compact P4 motion tests: geometry, contact invariants and invalid branches."""
import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from studio.motion import MotionError, MotionPlan, Point, compile_file, compile_motion, interpolate, solve_two_bone

BASE = {
    "fps":24, "frames":5, "shoulder":{"x":0,"y":0},
    "rest_hand":{"x":6,"y":2}, "upper_arm":7, "forearm":7,
    "initial_prop":{"x":8,"y":3}, "bend":1,
    "actions":[
        {"kind":"reach","start":0,"end":1,"target":{"x":8,"y":3}},
        {"kind":"grab","start":2,"end":2},
        {"kind":"place","start":3,"end":4,"target":{"x":7,"y":1}},
    ],
}


def plan(**kw):
    return MotionPlan.model_validate({**BASE, **kw})


def test_contact_sequence_and_geometry(tmp_path):
    script=plan()
    result=compile_motion(script)
    assert result["duration_frames"]==5
    assert [f["frame"] for f in result["frames"]]==list(range(5))
    assert [f["prop_state"] for f in result["frames"]]==["free","free","held","held","free"]
    for f in result["frames"]:
        elbow=f["elbow"]
        shoulder=f["shoulder"]
        hand=f["hand"]
        assert ((elbow["x"]-shoulder["x"])**2+(elbow["y"]-shoulder["y"])**2)**0.5 == pytest.approx(7,abs=1e-6)
        assert ((hand["x"]-elbow["x"])**2+(hand["y"]-elbow["y"])**2)**0.5 == pytest.approx(7,abs=1e-6)
        if f["prop_state"]=="held":
            assert f["prop"]==f["hand"]
    assert result["frames"][-1]["prop"]=={"x":7.0,"y":1.0}
    p=tmp_path/"plan.json"
    p.write_text(json.dumps(script.model_dump()))
    dst=compile_file(p,tmp_path/"output"/"compiled.json")
    assert json.loads(dst.read_text())==result


@pytest.mark.parametrize("patch",[
    {"frames":0}, {"bend":0}, {"upper_arm":0}, {"fps":0},
    {"actions":[]},
    {"actions":[{"kind":"wait","start":1,"end":4}]},
    {"actions":[{"kind":"wait","start":0,"end":1}]},
    {"actions":[{"kind":"wait","start":0,"end":5}]},
    {"actions":[{"kind":"wait","start":0,"end":4,"target":{"x":1,"y":1}}]},
    {"actions":[{"kind":"reach","start":0,"end":4}]},
    {"actions":[{"kind":"wait","start":0,"end":-1}]},
    {"actions":[{"kind":"wait","start":2,"end":1}]},
])
def test_invalid_plan(patch):
    with pytest.raises(ValidationError):
        plan(**patch)


@pytest.mark.parametrize("actions,initial_prop,rest_hand,error",[
    ([{"kind":"grab","start":0,"end":4}],{"x":8,"y":3},{"x":6,"y":2},"Grab"),
    ([{"kind":"grab","start":0,"end":1},{"kind":"grab","start":2,"end":4}],{"x":6,"y":2},{"x":6,"y":2},"Grab"),
    ([{"kind":"carry","start":0,"end":4,"target":{"x":8,"y":3}}],{"x":8,"y":3},{"x":6,"y":2},"Cannot"),
    ([{"kind":"place","start":0,"end":4,"target":{"x":8,"y":3}}],{"x":8,"y":3},{"x":6,"y":2},"Cannot"),
    ([{"kind":"grab","start":0,"end":1},{"kind":"reach","start":2,"end":4,"target":{"x":8,"y":3}}],{"x":6,"y":2},{"x":6,"y":2},"Use carry"),
    ([{"kind":"grab","start":0,"end":4}],{"x":6,"y":2},{"x":6,"y":2},"Shot ends"),
])
def test_illegal_contact(actions,initial_prop,rest_hand,error):
    with pytest.raises(MotionError,match=error):
        compile_motion(plan(actions=actions,initial_prop=initial_prop,rest_hand=rest_hand))


@pytest.mark.parametrize("target,upper,lower",[
    (Point(x=0,y=0),7,7),
    (Point(x=30,y=0),7,7),
    (Point(x=1,y=0),9,2),
])
def test_unreachable(target,upper,lower):
    with pytest.raises(MotionError,match="reach"):
        solve_two_bone(Point(x=0,y=0),target,upper,lower,1)


def test_one_frame_move_and_opposite_bend():
    script=plan(frames=3,actions=[
        {"kind":"reach","start":0,"end":0,"target":{"x":8,"y":3}},
        {"kind":"grab","start":1,"end":1},
        {"kind":"place","start":2,"end":2,"target":{"x":7,"y":2}},
    ],bend=-1)
    poses=compile_motion(script)["frames"]
    assert poses[0]["hand"]=={"x":8.0,"y":3.0}
    assert poses[-1]["prop_state"]=="free"
    assert interpolate(Point(x=0,y=0),Point(x=10,y=10),0.5)==Point(x=5,y=5)


def test_grip_socket_offset_maintains_true_contact():
    script=plan(
        initial_prop={"x":8,"y":3},
        grip_offset={"x":-2,"y":0},
        actions=[
            {"kind":"reach","start":0,"end":1,"target":{"x":10,"y":3}},
            {"kind":"grab","start":2,"end":2},
            {"kind":"place","start":3,"end":4,"target":{"x":9,"y":1}},
        ],
    )
    result=compile_motion(script)
    assert result["grip_offset"]=={"x":-2,"y":0}
    assert result["frames"][2]["prop"]=={"x":8.0,"y":3.0}
    assert result["frames"][3]["prop"]["x"]==pytest.approx(result["frames"][3]["hand"]["x"]-2)
    assert result["frames"][4]["prop"]=={"x":7.0,"y":1.0}
