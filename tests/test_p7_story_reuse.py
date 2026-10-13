"""P7 no-per-story-code proof: the SAME P5/P6 compiler accepts two film packages."""
from __future__ import annotations

import json
from pathlib import Path

import pytest
from studio.film import FilmError
from studio.film_v2 import FilmPlanV2, AssetCatalog, compile_film_v2
from studio.motion import MotionPlan, compile_motion


EXAMPLES=Path(__file__).resolve().parents[1]/"examples"


def compile_story(prefix: str) -> tuple[dict,dict]:
    film=FilmPlanV2.model_validate_json((EXAMPLES/(prefix+"_film.json")).read_text())
    catalog=AssetCatalog.model_validate_json((EXAMPLES/(prefix+"_catalog.json")).read_text())
    definitions=json.loads((EXAMPLES/(prefix+"_motions.json")).read_text())
    motion_to_rig={a.motion_id:a.rig_id for shot in film.shots for a in shot.actors}
    assert set(definitions)==set(motion_to_rig)
    clips={}
    for name,definition in definitions.items():
        pose=compile_motion(MotionPlan.model_validate(definition))
        pose["rig_id"]=motion_to_rig[name]
        clips[name]=pose
    return compile_film_v2(film,catalog,clips), clips


def test_second_story_runs_without_change_to_shared_animation_engine():
    coffee,coffee_clips=compile_story("p6_v2")
    key,key_clips=compile_story("p7_lost_key")
    assert coffee["total_frames"]==672 and coffee["duration_seconds"]==28
    assert key["total_frames"]==504 and key["duration_seconds"]==21
    assert len(coffee["shots"])==len(key["shots"])==5
    assert set(coffee["assets"]["rigs"])==set(key["assets"]["rigs"])=={"baseline","compact"}
    assert set(coffee["assets"]["backgrounds"]).isdisjoint(key["assets"]["backgrounds"])
    assert set(coffee["assets"]["props"]).isdisjoint(key["assets"]["props"])
    assert len(coffee_clips)==6 and len(key_clips)==5
    assert [s["end_exclusive"]-s["start"] for s in key["shots"]]==[72,96,120,96,120]
    assert [n["absolute_frame"] for n in key["narration"]]==[6,80,176,296,390]
    assert key["frames"][0]["props"][0]["visual_id"]=="brass_key"
    assert key["frames"][503]["actors"][0]["rig_id"]=="compact"
    assert [x["frame"] for x in key["frames"]]==list(range(504))
    assert {f["background_id"] for f in key["frames"]}=={"workshop_sunrise","workshop_twilight"}


def test_key_reach_grab_hang_and_second_actor_retrieval_are_continuous():
    film,clips=compile_story("p7_lost_key")
    # One stationary key remains on workshop shelf until the finder grabs it.
    first=clips["key_scan"]["frames"][0]["prop"]
    assert first=={"x":270.0,"y":195.0}
    assert clips["key_reach"]["frames"][-1]["prop"]==first
    lifted=clips["key_hang"]["frames"]
    assert lifted[0]["prop_state"]=="held"
    assert lifted[-1]["prop_state"]=="free"
    assert lifted[-1]["prop"]=={"x":221.0,"y":130.0}
    # Partner enters a DIFFERENT location and picks up exactly that same key.
    next_shot=clips["key_partner_wait"]["frames"][0]["prop"]
    assert next_shot==lifted[-1]["prop"]
    retrieved=clips["key_partner_move"]["frames"]
    assert retrieved[23]["hand"]=={"x":237.0,"y":130.0}
    assert retrieved[24]["prop_state"]=="held"
    assert retrieved[-1]["prop"]=={"x":256.0,"y":178.0}
    assert retrieved[-1]["prop_state"]=="free"
    # The global film timeline must use whole independent source clips.
    for shot in film["shots"]:
        motion_id=shot["motion_ids"][0]
        count=shot["end_exclusive"]-shot["start"]
        assert len(clips[motion_id]["frames"])==count


def test_cross_shot_prop_jump_rejected_for_new_story():
    plan=FilmPlanV2.model_validate_json((EXAMPLES/"p7_lost_key_film.json").read_text())
    catalog=AssetCatalog.model_validate_json((EXAMPLES/"p7_lost_key_catalog.json").read_text())
    source=json.loads((EXAMPLES/"p7_lost_key_motions.json").read_text())
    rigs={a.motion_id:a.rig_id for s in plan.shots for a in s.actors}
    clips={name:dict(compile_motion(MotionPlan.model_validate(value)),rig_id=rigs[name])
           for name,value in source.items()}
    clips["key_partner_wait"]["frames"][0]["prop"]["x"]+=5
    with pytest.raises(FilmError,match="World prop jumps"):
        compile_film_v2(plan,catalog,clips)
