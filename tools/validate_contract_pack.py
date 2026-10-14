"""Validate the accompanying CODEX SPEC contract pack (documentation utility only)."""
from pathlib import Path
import json
import sys
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = ROOT / 'contracts' / 'schemas'
EXAMPLES = ROOT / 'contracts' / 'examples'

def require(condition, message):
    if not condition:
        raise AssertionError(message)

def load(stem):
    return json.loads((EXAMPLES / f'{stem}.json').read_text(encoding='utf-8'))

def main():
    names = sorted(p.name.removesuffix('.schema.json') for p in SCHEMAS.glob('*.schema.json'))
    require(len(names) == 19, f'Expected 19 schemas, found {len(names)}')
    require(names == sorted(p.stem for p in EXAMPLES.glob('*.json')), 'Every schema must have exactly one same-named example')
    for name in names:
        schema = json.loads((SCHEMAS / f'{name}.schema.json').read_text(encoding='utf-8'))
        Draft202012Validator.check_schema(schema)
        example = load(name)
        errors = list(Draft202012Validator(schema).iter_errors(example))
        require(not errors, f'{name} example validation failed: {errors[:2]}')
    script,shot,requirements,resolution = [load(k) for k in ('script','shot_plan','asset_requirements','asset_resolution')]
    require(shot['script_artifact_id'] == script['artifact_id'], 'Shot Plan script pointer')
    sections = {s['section_id']:s['narration_text'] for s in script['sections']}
    for item in shot['shots']:
        s=sections[item['section_id']]
        require(s[item['section_start']:item['section_end']] == item['narration_text'], 'Shot exact-text source range')
    require(requirements['shot_plan_artifact_id'] == shot['artifact_id'], 'Requirements ShotPlan reference')
    require(resolution['asset_requirements_artifact_id'] == requirements['artifact_id'], 'Resolution requirement reference')
    require([r['requirement_id'] for r in requirements['requirements']] == [r['requirement_id'] for r in resolution['decisions']], 'Resolution requirement completeness/order')
    anim=load('animation_plan');compiled=load('compiled_film');voice=load('voice_manifest');final=load('final_timeline')
    require(anim['shot_plan_artifact_id'] == shot['artifact_id'] and anim['asset_resolution_artifact_id'] == resolution['artifact_id'], 'Director lineage')
    require(compiled['source_ids']['animation_plan_artifact_id'] == anim['artifact_id'], 'Compiled film lineage')
    require(compiled['total_frames'] == sum(s['duration_frames'] for s in compiled['shots']), 'Compiled total frame equality')
    require(all(len(s['frames']) == s['duration_frames'] and [f['frame'] for f in s['frames']] == list(range(s['duration_frames'])) for s in compiled['shots']), 'Contiguous frame list')
    require(voice['compiled_film_artifact_id'] == compiled['artifact_id'], 'Voice source')
    require(all(c['start_sample']==c['start_frame']*2000 for c in voice['cues']), '2000 sample/frame voice offset')
    require(final['voice_manifest_artifact_id']==voice['artifact_id'] and final['compiled_film_artifact_id']==compiled['artifact_id'], 'Final timeline lineage')
    require(final['total_frames'] == sum(s['final_frames'] for s in final['shots']), 'Final frame total')
    require(final['audio']['sample_count']==final['total_frames']*2000, 'Final exact sample duration')
    rig,parts,layout,joints,manifest = [load(x) for x in ('rig_profile','parts_manifest','rig_layout','rig_joints','rig_manifest')]
    roles=[p['semantic_role'] for p in parts['parts']]
    require(len(roles)==14 and len(set(roles))==14, '14 unique semantic roles')
    require(sorted(roles)==sorted(p['semantic_role'] for p in layout['parts']), 'Layout part roles')
    require(joints['rig_layout_artifact_id']==layout['artifact_id'], 'Joint layout reference')
    require(manifest['parts_manifest_artifact_id']==parts['artifact_id'] and manifest['rig_layout_artifact_id']==layout['artifact_id'] and manifest['rig_joints_artifact_id']==joints['artifact_id'], 'Rig manifest source chain')
    require(manifest['rig_version_id']==rig['rig_version_id'], 'RigProfile matching version')
    frm=load('frame_sequence_manifest')
    require(frm['frame_count']==len(frm['frames']) and frm['shot_id']==compiled['shots'][0]['shot_id'], 'Frame sequence consistency')
    print(f'PASS {len(names)} schema/example pairs, 21 cross-artifact/semantic assertions')

if __name__ == '__main__':
    try:main()
    except Exception as exc:
        print('FAIL',exc,file=sys.stderr);raise
