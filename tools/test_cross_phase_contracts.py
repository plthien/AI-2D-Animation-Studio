"""Executable cross-phase documentation/contract negative and positive checks.

Not a replacement for backend runtime tests, provider calls, or physical browser inspection.
"""
from copy import deepcopy
from pathlib import Path
import json
from jsonschema import Draft202012Validator
ROOT=Path(__file__).resolve().parents[1]

def read(kind,stem):return json.loads((ROOT/'contracts'/kind/f'{stem}.{ "schema.json" if kind=="schemas" else "json" }').read_text(encoding='utf-8'))
def valid(stem,payload):return Draft202012Validator(read('schemas',stem)).is_valid(payload)
def must(cond,label):
    if not cond:raise AssertionError(label)

def ceil_div(a,b):return (a+b-1)//b

def reconcile_formula(raw_samples,original_frames,has_legal_hold=True):
    added=max(0,ceil_div(raw_samples,2000)-original_frames)
    if added>48:raise ValueError('VOICE_WINDOW_OVERFLOW')
    if added and not has_legal_hold:raise ValueError('VOICE_HOLD_UNSAFE')
    return original_frames+added

def main():
    checks=0
    def t(x,label):
        nonlocal checks
        checks+=1;must(x,label)
    final=read('examples','final_timeline');compiled=read('examples','compiled_film');voice=read('examples','voice_manifest');shot=read('examples','shot_plan')
    t(valid('final_timeline',final),'valid final example')
    test=deepcopy(final);test['shots'][0]['original_frames']=720;test['shots'][0]['final_frames']=768;test['shots'][0]['extension_frames']=48;test['total_frames']=768;test['audio']['sample_count']=768*2000
    t(valid('final_timeline',test),'720+48 must be representable in final schema')
    bad=deepcopy(test);bad['shots'][0]['final_frames']=769
    t(not valid('final_timeline',bad),'+49 final shot rejected')
    bad=deepcopy(test);bad['total_frames']=23041;bad['audio']['sample_count']=bad['total_frames']*2000
    t(not valid('final_timeline',bad),'film >23040 rejected')
    t(reconcile_formula(720*2000,720)==720,'voice fits original')
    t(reconcile_formula(720*2000+1,720)==721,'one sample overrun requires one frame')
    t(reconcile_formula(720*2000+48*2000,720)==768,'exact 48-frame hold valid')
    try:reconcile_formula(720*2000+48*2000+1,720)
    except ValueError as e:t(str(e)=='VOICE_WINDOW_OVERFLOW','beyond 48 rejected')
    else:raise AssertionError('overflow accepted')
    try:reconcile_formula(720*2000+1,720,False)
    except ValueError as e:t(str(e)=='VOICE_HOLD_UNSAFE','unsafe hold rejected')
    else:raise AssertionError('unsafe hold accepted')
    t(compiled['shots'][0]['duration_frames']<=720,'compiled cap remains 720')
    b=deepcopy(compiled);b['shots'][0]['duration_frames']=721
    t(not valid('compiled_film',b),'compiled 721 rejected')
    t(voice['cues'][0]['start_sample']==voice['cues'][0]['start_frame']*2000,'global frame/sample authority')
    t(voice['cues'][0]['start_frame']==0 and shot['shots'][0]['order']==1,'example cue begins at absolute shot start')
    source=(ROOT/'MASTER_SPEC.md').read_text(encoding='utf-8')
    t('start_frame` is **absolute within the ORIGINAL compiled film**' in source,'source frame reference locked')
    t('P8 records this as `needs_reconciliation`' in source,'raw overrun P8 holds for P9')
    t('`final_timeline.v1` permits `shots[].final_frames<=768`' in source,'master final bounds')
    t('**Fourteen physical tables**' in source,'new DB table authority')
    phase9=(ROOT/'docs/implementation/P9_TIMING_FFMPEG.md').read_text(encoding='utf-8')
    t('23040' in phase9 and '768' in phase9,'P9 plan aligned with schema')
    phase8=(ROOT/'docs/implementation/P8_VOICE.md').read_text(encoding='utf-8')
    t('needs_reconciliation' in phase8 and 'absolute' in phase8,'P8 plan aligned')
    print(f'PASS {checks} cross-phase policy/schema positive and negative assertions')

if __name__=='__main__':main()
