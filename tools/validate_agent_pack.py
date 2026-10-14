"""Check Codex execution policy files and cross-references (docs only)."""
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[1]
SKILLS={'ytb-source-port','external-authoring','asset-resolution','glabs-integration','native-auto-rig','motion-engine','spine-renderer','voice-video-assembly','phase-self-review'}
RULES={'PROJECT_RULES.md','ARCHITECTURE_RULES.md','CODING_RULES.md','TESTING_RULES.md','REVIEW_RULES.md'}

def main():
    agents=(ROOT/'AGENTS.md').read_text(encoding='utf-8')
    master=(ROOT/'MASTER_SPEC.md').read_text(encoding='utf-8')
    assert 'feat/p0-p1-foundation' in agents and 'feat/p0-p1-foundation' in master
    assert '393d0eb5516ac8bb8455f859b79bfc64388b128e' in agents and '393d0eb5516ac8bb8455f859b79bfc64388b128e' in master
    assert (ROOT/'README_FOR_CODEX.md').is_file()
    assert set(p.name for p in (ROOT/'docs/rules').glob('*.md'))==RULES
    actual={p.parent.name for p in (ROOT/'.agents/skills').glob('*/SKILL.md')}
    assert actual==SKILLS, (actual,SKILLS)
    for name in SKILLS:
        p=ROOT/'.agents/skills'/name/'SKILL.md'
        contents=p.read_text(encoding='utf-8')
        assert re.match(r'\A---\nname: '+re.escape(name)+r'\ndescription: \S.+\n---\n',contents), name
        assert 'MASTER_SPEC.md' in contents or 'phase-self-review' in contents, name
        assert name in agents, name
    for name in RULES:
        assert name in agents, name
    assert '## 14.' in master and '## A.' in master and '## H.' in master
    print('PASS 1 AGENTS + 9 skills + 5 rules + authoritative references')
if __name__=='__main__': main()
