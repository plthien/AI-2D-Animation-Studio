"""P5/P6 v2 independent-shot and asset/continuity gate tests.

A small parametrized suite rather than one unit test per film frame.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest
from pydantic import ValidationError
from studio.film import FilmError
from studio.film_v2 import AssetCatalog, FilmPlanV2, compile_film_v2, compile_film_v2_file
from studio.motion import MotionPlan, compile_motion

ROOT=Path(__file__).parents[1]
PLAN=json.loads((ROOT/"examples/p6_v2_film.json").read_text())
CATALOG=json.loads((ROOT/"examples/p6_v2_catalog.json").read_text())
SOURCE=json.loads((ROOT/"examples/p6_v2_motions.json").read_text())
ACTOR_RIG={actor["motion_id"]:actor["rig_id"] for shot in PLAN["shots"] for actor in shot["actors"]}


def data():
    clips={}
    for name,source in SOURCE.items():
        clip=compile_motion(MotionPlan.model_validate(source))
        clip["rig_id"]=ACTOR_RIG[name]
        clips[name]=clip
    return FilmPlanV2.model_validate(PLAN),AssetCatalog.model_validate(CATALOG),clips


def test_real_five_shot_plan_and_file(tmp_path):
    plan,catalog,clips=data()
    film=compile_film_v2(plan,catalog,clips)
    assert film["total_frames"]==672 and film["duration_seconds"]==28
    assert film["schema_version"]=="film.timeline.v2"
    assert [s["start"] for s in film["shots"]]==[0,96,240,384,528]
    assert [s["end_exclusive"] for s in film["shots"]]==[96,240,384,528,672]
    assert len({s["motion_ids"][0] for s in film["shots"]})==5
    assert len({m for shot in film["shots"] for m in shot["motion_ids"]})==6
    assert len(film["frames"][384]["actors"])==2
    assert len(film["frames"][528]["actors"])==2
    assert {f["background_id"] for f in film["frames"]}=={"cafe_morning","cafe_evening"}
    assert {a["rig_id"] for f in film["frames"] for a in f["actors"]}=={"baseline","compact"}
    assert [n["absolute_frame"] for n in film["narration"]]==[8,102,246,392,536]
    for shot in film["shots"]:
        sequence=film["frames"][shot["start"]:shot["end_exclusive"]]
        assert all(frame["local_frame"]==frame["actors"][0]["pose_frame"] for frame in sequence)
    p=tmp_path/"plan.json"; c=tmp_path/"catalog.json"; m=tmp_path/"motion.json"
    p.write_text(json.dumps(PLAN));c.write_text(json.dumps(CATALOG));m.write_text(json.dumps(clips))
    output=compile_film_v2_file(p,c,m,tmp_path/"out"/"timeline.json")
    assert json.loads(output.read_text())==film


@pytest.mark.parametrize("which,change",[
    ("plan",lambda p:p.update({"schema_version":"film.v1"})),
    ("plan",lambda p:p.update({"fps":25})),
    ("plan",lambda p:p.update({"shots":[]})),
    ("plan",lambda p:p["shots"].append(copy.deepcopy(p["shots"][0]))),
    ("plan",lambda p:p["shots"][0]["actors"].append(copy.deepcopy(p["shots"][0]["actors"][0]))),
    ("plan",lambda p:p["shots"][0]["props"].append(copy.deepcopy(p["shots"][0]["props"][0]))),
    ("plan",lambda p:p["shots"][0]["props"].append({**p["shots"][0]["props"][0],"prop_id":"another"})),
    ("plan",lambda p:p["shots"][0]["props"][0].update({"owner_actor_id":"missing"})),
    ("plan",lambda p:p["shots"][0]["narration"].update({"start_frame":96})),
    ("plan",lambda p:p["shots"][0]["actors"][0].update({"actor_id":"not-safe"})),
    ("catalog",lambda c:c["rigs"].update({"../invalid":{"directory":"baseline"}})),
    ("catalog",lambda c:c["backgrounds"]["cafe_morning"].update({"image":"../../evil.png"})),
])
def test_reject_director_or_catalog_schema(which,change):
    source=copy.deepcopy(PLAN if which=="plan" else CATALOG)
    change(source)
    with pytest.raises(ValidationError):
        if which=="plan":
            FilmPlanV2.model_validate(source)
        else:
            AssetCatalog.model_validate(source)


@pytest.mark.parametrize("case",[
    "empty", "background", "rig", "motion", "fps", "duration", "not_list",
    "wrong_length", "clip_identity", "frame_index", "missing_pose",
    "missing_prop", "wrist_jump", "prop_jump",
])
def test_compiler_rejects_invalid_resources_and_continuity(case):
    plan,catalog,clips=data()
    plan=copy.deepcopy(plan)
    catalog=copy.deepcopy(catalog)
    clips=copy.deepcopy(clips)
    if case=="empty":
        clips={}
    elif case=="background":
        plan.shots[0].background_id="unknown"
    elif case=="rig":
        plan.shots[0].actors[0].rig_id="unknown"
    elif case=="motion":
        plan.shots[0].actors[0].motion_id="unknown"
    elif case=="fps":
        clips["hero_wait"]["fps"]=30
    elif case=="duration":
        clips["hero_wait"]["duration_frames"]=95
    elif case=="not_list":
        clips["hero_wait"]["frames"]=None
    elif case=="wrong_length":
        clips["hero_wait"]["frames"].pop()
    elif case=="clip_identity":
        clips["hero_wait"]["rig_id"]="compact"
    elif case=="frame_index":
        clips["hero_wait"]["frames"][0]["frame"]=9
    elif case=="missing_pose":
        del clips["hero_wait"]["frames"][-1]["hand"]
    elif case=="missing_prop":
        plan.shots[0].props[0].visual_id="absent"
    elif case=="wrist_jump":
        clips["hero_reach"]["frames"][0]["hand"]["x"]+=5
    elif case=="prop_jump":
        clips["hero_reach"]["frames"][0]["prop"]["x"]+=5
    with pytest.raises(FilmError):
        compile_film_v2(plan,catalog,clips)


def test_explicit_continuity_break_and_multiple_actor_instance():
    plan,catalog,clips=data()
    # A discontinuity may be intentional, but must be explicitly authored.
    clips["hero_reach"]["frames"][0]["hand"]["x"]+=6
    plan.shots[1].continuity_break=True
    compiled=compile_film_v2(plan,catalog,clips)
    assert compiled["frames"][96]["shot_id"]=="hero_reaches"
    # Same Spine asset can be referenced by two distinct actor IDs in one shot.
    plan,catalog,clips=data()
    second=plan.shots[0].actors[0].model_copy(update={"actor_id":"duplicate_rig",
                                                        "offset_x":200,"layer":1})
    plan.shots[0].actors.append(second)
    compiled=compile_film_v2(plan,catalog,clips)
    assert len(compiled["frames"][0]["actors"])==2


def test_missing_prior_actor_or_prop_still_valid():
    plan,catalog,clips=data()
    # Remove prop from the reaction shot, then remove that actor from comparison
    # by allowing an explicit jump cut; next shot starts with the same asset.
    plan.shots[3].props=[]
    # The prop is absent in the previous shot: normal continuity validation
    # must permit it to newly enter the next shot, without a forced jump-cut.
    compiled=compile_film_v2(plan,catalog,clips)
    assert len(compiled["frames"][384]["props"])==0
    assert compiled["frames"][528]["props"][0]["prop_id"]=="coffee_cup"


def test_optional_narration_and_reused_catalog_paths():
    plan,catalog,clips=data()
    plan.shots[3].narration=None
    compiled=compile_film_v2(plan,catalog,clips)
    assert len(compiled["narration"])==4
    assert compiled["assets"]["rigs"]["baseline"]["directory"]=="baseline"
