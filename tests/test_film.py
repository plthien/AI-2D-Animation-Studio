"""P5 film DSL contract: minimum parametrized validation plus exact frame audit."""
from pathlib import Path
import json
import pytest
from pydantic import ValidationError
from studio.film import FilmPlan, FilmError, compile_film, compile_film_file


ROOT=Path(__file__).parents[1]
BASE=json.loads((ROOT/"examples/p6_coffee_film.json").read_text())
POSES={"baseline":{"fps":24,"frames":[{"frame":i} for i in range(48)]}}


def test_full_five_shot_timeline_and_file_io(tmp_path):
    plan=FilmPlan.model_validate(BASE)
    result=compile_film(plan,POSES)
    assert result["total_frames"]==672
    assert result["duration_seconds"]==28
    assert len(result["frames"])==672
    assert [s["start"] for s in result["shots"]]==[0,96,240,384,528]
    assert [s["end_exclusive"] for s in result["shots"]]==[96,240,384,528,672]
    assert [x["clip_frame"] for x in (result["frames"][0],result["frames"][95],
        result["frames"][96],result["frames"][239],result["frames"][671])]==[0,11,12,14,47]
    assert [n["absolute_frame"] for n in result["narration"]]==[8,102,246,392,536]
    clip=tmp_path/"actor.json";clip.write_text(json.dumps(POSES["baseline"]))
    file=compile_film_file(ROOT/"examples/p6_coffee_film.json",{"baseline":clip},tmp_path/"render"/"timeline.json")
    assert json.loads(file.read_text())==result


@pytest.mark.parametrize("patch",[
    {"schema_version":"bad"},
    {"fps":30},
    {"shots":[]},
    {"shots":[BASE["shots"][0]]*2},
    {"shots":[{**BASE["shots"][0],"clip_in":4,"clip_out":2}]},
    {"shots":[{**BASE["shots"][0],"narration":{**BASE["shots"][0]["narration"],"start_frame":96}}]},
    {"shots":[{**BASE["shots"][0],"narration":{**BASE["shots"][0]["narration"],"wav":"../evil.wav"}}]},
    {"shots":[{**BASE["shots"][0],"duration_frames":0}]},
])
def test_reject_invalid_director_input(patch):
    with pytest.raises(ValidationError):
        FilmPlan.model_validate({**BASE,**patch})


@pytest.mark.parametrize("case,asset",[
    ("none",POSES),
    ("unknown",POSES),
    ("fps",{"baseline":{"fps":25,"frames":[{}]*48}}),
    ("frames",{"baseline":{"fps":24,"frames":None}}),
    ("overflow",POSES),
    ("gap",POSES),
    ("incomplete",{"baseline":{"fps":24,"frames":[{}]*49}}),
])
def test_fail_closed_damaged_shot_or_rig(case,asset):
    if case=="none":
        with pytest.raises(FilmError,match="No compiled"):
            compile_film(FilmPlan.model_validate(BASE),{})
        return
    if case=="unknown":
        plan=FilmPlan.model_validate({**BASE,"shots":[{**s,"rig_id":"compact"} for s in BASE["shots"]]})
    elif case=="overflow":
        plan=FilmPlan.model_validate({**BASE,"shots":[*BASE["shots"][:-1],
            {**BASE["shots"][-1],"clip_out":48}]})
    elif case=="gap":
        plan=FilmPlan.model_validate({**BASE,"shots":[BASE["shots"][0],
            {**BASE["shots"][1],"clip_in":14},*BASE["shots"][2:]]})
    else:
        plan=FilmPlan.model_validate(BASE)
    with pytest.raises(FilmError):
        compile_film(plan,asset)


def test_single_frame_shot_mapped_to_last_clip_frame():
    shot={**BASE["shots"][0],"duration_frames":1,"clip_in":0,"clip_out":0,
          "narration":{**BASE["shots"][0]["narration"],"start_frame":0}}
    plan=FilmPlan.model_validate({**BASE,"shots":[shot]})
    compiled=compile_film(plan,{"baseline":{"fps":24,"frames":[{}]}})
    assert compiled["total_frames"]==1 and compiled["frames"][0]["clip_frame"]==0
