"""Pass/fail matrix for animation-first spec contracts; no real render/provider claims."""
from pathlib import Path
from copy import deepcopy
import json
from jsonschema import Draft202012Validator
from validate_animation_semantics import channel_hashes,check_shot_plan,check_animation_performance,check_rig_bones,check_voice_cues

ROOT=Path(__file__).resolve().parents[1]
def read(stem):return json.loads((ROOT/'contracts'/'examples'/f'{stem}.json').read_text(encoding='utf8'))
def schema(stem):return json.loads((ROOT/'contracts'/'schemas'/f'{stem}.schema.json').read_text(encoding='utf8'))
def accepts(stem,value):return Draft202012Validator(schema(stem)).is_valid(value)
def rejected(func,*args):
    try:func(*args)
    except ValueError:return True
    return False

def main():
    checks=0
    def must(condition,label):
        nonlocal checks
        checks+=1
        assert condition,label
    dna=read('channel_dna');script=read('script');shot=read('shot_plan');anim=read('animation_plan')
    rig=read('rig_profile');compiled=read('compiled_film');voice=read('voice_manifest')
    hashes=channel_hashes(dna)
    must(all(x.startswith('sha256:') for x in hashes.values()),'identity hashes')
    changed=deepcopy(dna);changed['animation_identity']['motion_energy']='high'
    must(channel_hashes(changed)['visual_style_hash']==hashes['visual_style_hash'],'performance change must preserve visual hash')
    must(channel_hashes(changed)['performance_style_hash']!=hashes['performance_style_hash'],'performance hash changes')
    changed=deepcopy(dna);changed['visual_identity']['palette']='a distinct flat palette'
    must(channel_hashes(changed)['visual_style_hash']!=hashes['visual_style_hash'],'palette changes visual hash')
    must(channel_hashes(changed)['performance_style_hash']==hashes['performance_style_hash'],'palette change preserves performance hash')
    changed=deepcopy(dna);changed['schema_version']='channel_dna.v1'
    must(not accepts('channel_dna',changed),'legacy dna schema rejected')
    must(rejected(channel_hashes,changed),'legacy dna semantic rejected')
    changed=deepcopy(dna);changed['narration']['wpm_min']=changed['narration']['wpm_max']
    must(rejected(channel_hashes,changed),'wpm range semantics rejected')
    check_shot_plan(shot,script);checks+=1
    changed=deepcopy(shot);changed['shots'][0]['shot_purpose']='visual_reaction'
    must(rejected(check_shot_plan,changed,script),'voiced visual purpose forbidden')
    changed=deepcopy(shot);changed['shots'][0]['narration_text']=''
    must(rejected(check_shot_plan,changed,script),'mismatched text forbidden')
    silent=deepcopy(shot['shots'][0]);silent['shot_id']='shot_002';silent['order']=2;silent['section_start']=silent['section_end'];silent['narration_text']='';silent['shot_purpose']='visual_reaction'
    changed=deepcopy(shot);changed['shots'].append(silent)
    must(accepts('shot_plan',changed),'silent visual shot JSON accepts')
    check_shot_plan(changed,script);checks+=1
    check_voice_cues(changed,voice);checks+=1
    changed_bad=deepcopy(changed);changed_bad['shots'][1]['section_start']-=1
    must(rejected(check_shot_plan,changed_bad,script),'invalid silent window forbidden')
    check_animation_performance(dna,anim);checks+=1
    changed=deepcopy(anim);changed['shots'][0]['performance']['motion_energy']='high'
    must(rejected(check_animation_performance,dna,changed),'Director mismatched performance forbidden')
    changed=deepcopy(anim);del changed['shots'][0]['performance']
    must(not accepts('animation_plan',changed),'Director missing performance rejected')
    ref=read('generation_request');ref['generation_kind']='character_parts_atlas';ref['reference_image_artifact_id']=None
    must(not accepts('generation_request',ref),'atlas requires source reference')
    changed=deepcopy(read('asset_version'));changed['kind']='effect'
    must(not accepts('asset_version',changed),'unsupported effect rejected')
    changed=deepcopy(read('parts_manifest'));changed['source_atlas_artifact_id']=changed['reference_image_artifact_id']
    must(changed['source_atlas_artifact_id']==changed['reference_image_artifact_id'],'distinct artifact IDs test fixture')
    original=list(rig['runtime_bone_names']);check_rig_bones(rig,original);checks+=1
    must(rejected(check_rig_bones,rig,original[:-1]),'missing bone rejected')
    must(rejected(check_rig_bones,rig,original+['fake_extra']),'unknown bone rejected')
    must(rejected(check_rig_bones,rig,original+original[:1]),'duplicate bone rejected')
    extra=deepcopy(rig);extra['runtime_bone_names'].append('optional_hair')
    must(accepts('rig_profile',extra),'optional bone profile schema accepted')
    check_rig_bones(extra,original+['optional_hair']);checks+=1
    changed=deepcopy(compiled)
    for frame in changed['shots'][0]['frames']:
        frame['actors'][0]['bones'].append({**frame['actors'][0]['bones'][0],'bone_name':'optional_hair'})
    must(accepts('compiled_film',changed),'frame with approved extra bone accepted')
    changed['shots'][0]['frames'][0]['actors'][0]['bones'] += [dict(changed['shots'][0]['frames'][0]['actors'][0]['bones'][0]) for _ in range(50)]
    must(not accepts('compiled_film',changed),'over-64 bone frame rejected')
    changed=deepcopy(voice);changed['cues'].append({**voice['cues'][0],'shot_id':'shot_002'})
    must(rejected(check_voice_cues,shot,changed),'extra silent cue rejected')
    print(f'PASS {checks} animation-first positive/negative and cross-domain contract assertions')

if __name__=='__main__':main()
