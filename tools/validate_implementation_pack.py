"""Static verification of the twelve P0–P11 Codex work orders and normative cross-links."""
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[1]
PLANS={
    'P0':'P0_FOUNDATION.md','P1':'P1_EXTERNAL_AUTHORING.md','P2':'P2_ASSET_REGISTRY.md',
    'P3':'P3_GLABS_INTEGRATION.md','P4':'P4_NATIVE_AUTO_RIG.md','P5':'P5_MOTION_ENGINE.md',
    'P6':'P6_ANIMATION_DIRECTOR.md','P7':'P7_SPINE_RENDERER.md','P8':'P8_VOICE.md',
    'P9':'P9_TIMING_FFMPEG.md','P10':'P10_PRODUCTION_UI_QC.md','P11':'P11_ACCEPTANCE_RELEASE.md'
}

def main():
    assert {p.name for p in (ROOT/'docs/implementation').glob('P*.md')} == set(PLANS.values())
    m=(ROOT/'MASTER_SPEC.md').read_text(encoding='utf-8')
    assert '# AI 2D Animation Studio — CODEX EXECUTION SPECIFICATION v1.3' in m
    assert '## 20. Phase implementation pack and cross-contract fixes' in m
    assert '14 physical tables' not in m or 'Fourteen physical tables' in m
    assert '23040' in m and '768 frames per shot' in m
    assert '`rig_manifest.v1`' in m and 'channel_dna.v2' in m
    for index,(phase,name) in enumerate(PLANS.items()):
        path=ROOT/'docs/implementation'/name
        s=path.read_text(encoding='utf-8')
        assert s.startswith(f'# {phase} —'), (phase,'title')
        assert len(s)>4000, (phase,'must contain substantial phase work orders')
        for anchor in ['## Task','## Work orders','## Work orders,','## Motion','## Tests','## Test','## Negative','## Failure']:
            if anchor in s:break
        else:raise AssertionError((phase,'missing work breakdown'))
        assert '## Mandatory phase protocol' in s,(phase,'protocol')
        assert '## Shared implementation invariants' in s,(phase,'invariants')
        assert 'tests/' in s,(phase,'tests')
        assert 'One phase' in s or 'one phase' in s,(phase,'freeze policy')
        assert phase in (ROOT/'docs/implementation/INDEX.md').read_text(encoding='utf-8')
    for path in [ROOT/'AGENTS.md',ROOT/'README_FOR_CODEX.md'] + list((ROOT/'docs/rules').glob('*.md')) + list((ROOT/'.agents/skills').glob('*/SKILL.md')):
        s=path.read_text(encoding='utf-8')
        assert 'docs/implementation/' in s,(path,'missing phase docs authority')
    assert 'P8 stores exact measured WAV' in (ROOT/'docs/audits/CONTRACT_PHASE_CONSISTENCY_v1_3.md').read_text(encoding='utf-8')
    print(f'PASS {len(PLANS)} phase plans, root/agent/skills/rules references, Master v1.3, timing & provenance gates')

if __name__=='__main__': main()
