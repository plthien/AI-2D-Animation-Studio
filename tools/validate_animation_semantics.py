"""Executable cross-artifact contract helpers for the Codex specification (not product runtime)."""
from __future__ import annotations
import hashlib
import json
from collections import defaultdict


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def canonical_hash(value: dict) -> str:
    payload=json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False).encode('utf-8')
    return 'sha256:'+hashlib.sha256(payload).hexdigest()


def channel_hashes(dna: dict) -> dict[str,str]:
    require(dna.get('schema_version')=='channel_dna.v2','CHANNEL_DNA_VERSION_UNSUPPORTED')
    narr=dna['narration']
    require(narr['wpm_min']<narr['wpm_max'],'CHANNEL_DNA_STYLE_INVALID: wpm')
    require(len(set(dna['visual_identity']))==7,'CHANNEL_DNA_STYLE_INVALID: missing visual identity')
    require(0<=dna['animation_identity']['reaction_hold_frames']<=24,'CHANNEL_DNA_STYLE_INVALID: hold')
    return {
      'visual_style_hash':canonical_hash({k:dna[k] for k in ('visual_identity','entity_styles','global_negative_constraints')}),
      'performance_style_hash':canonical_hash({k:dna[k] for k in ('animation_identity','editorial_identity')}),
      'narration_identity_hash':canonical_hash({k:dna[k] for k in ('narration','narration_identity')}),
    }


def check_shot_plan(plan:dict, script:dict) -> None:
    require(plan['script_artifact_id']==script['artifact_id'],'SHOT_SCRIPT_SOURCE_MISMATCH')
    sections={x['section_id']:x['narration_text'] for x in script['sections']}
    require(len(sections)==len(script['sections']),'SCRIPT_SECTION_DUPLICATE')
    orders=[s['order'] for s in plan['shots']]
    require(orders==list(range(1,len(orders)+1)),'SHOT_ORDER_INVALID')
    shotids=[s['shot_id'] for s in plan['shots']]
    require(len(set(shotids))==len(shotids),'SHOT_ID_DUPLICATE')
    voiced=0
    positions=defaultdict(int)
    characters={}
    props={}
    for item in plan['shots']:
        sid=item['section_id'];require(sid in sections,'SHOT_SECTION_UNKNOWN')
        raw=sections[sid];a=item['section_start'];b=item['section_end']
        require(0<=a<=b<=len(raw),'SHOT_SILENCE_RANGE_INVALID: bounds')
        require(item['narration_text']==raw[a:b],'SHOT_QUOTE_MISMATCH')
        if a==b:
            require(item['narration_text']=='' and item['shot_purpose'] in ('visual_reaction','establishing'),'SHOT_SILENCE_RANGE_INVALID')
        else:
            require(item['shot_purpose']=='story_action','SHOT_SILENCE_RANGE_INVALID: voiced purpose')
            require(a==positions[sid],'SHOT_QUOTE_PARTITION_INVALID')
            positions[sid]=b;voiced+=1
        for actor in item['actors']:
            old=characters.setdefault(actor['actor_id'],actor['character_key'])
            require(old==actor['character_key'],'SHOT_ACTOR_IDENTITY_CHANGED')
        for prop in item['props']:
            old=props.setdefault(prop['prop_id'],prop['prop_key'])
            require(old==prop['prop_key'],'SHOT_PROP_IDENTITY_CHANGED')
    require(voiced>=1,'SHOT_ALL_SILENT_UNSUPPORTED')
    for sid,raw in sections.items():
        require(positions[sid]==len(raw),'SHOT_QUOTE_PARTITION_INVALID: incomplete '+sid)


def check_animation_performance(dna:dict, plan:dict)->None:
    keys=('motion_energy','movement_rhythm','transition_easing','reaction_hold_frames')
    expect={k:dna['animation_identity'][k] for k in keys}
    for shot in plan['shots']:
        require(shot['performance']==expect,'DIRECTOR_PERFORMANCE_SOURCE_MISMATCH')


def check_rig_bones(rig:dict, actual_bone_names:list[str])->None:
    expected=rig['runtime_bone_names'];roles=list(rig['bone_roles'].values())
    require(len(set(expected))==len(expected) and 16<=len(expected)<=64,'RIG_BONE_SET_MISMATCH: profile invalid')
    require(len(set(roles))==16 and set(roles).issubset(set(expected)),'RIG_BONE_SET_MISMATCH: missing roles')
    require(len(set(actual_bone_names))==len(actual_bone_names) and set(actual_bone_names)==set(expected),'RIG_BONE_SET_MISMATCH')


def check_voice_cues(shot_plan:dict,voice:dict)->None:
    expected={s['shot_id'] for s in shot_plan['shots'] if s['narration_text']}
    actual=[c['shot_id'] for c in voice['cues']]
    require(len(actual)==len(set(actual)) and set(actual)==expected,'VOICE_CUE_SET_MISMATCH')
    for c in voice['cues']:
        require(c['start_sample']==c['start_frame']*2000,'VOICE_SAMPLE_OFFSET_INVALID')
