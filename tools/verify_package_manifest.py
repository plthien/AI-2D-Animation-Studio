"""Check all tracked specification payload hashes in PACKAGE_MANIFEST.json."""
from pathlib import Path
import hashlib, json

ROOT=Path(__file__).resolve().parents[1]
def main():
    data=json.loads((ROOT/'PACKAGE_MANIFEST.json').read_text(encoding='utf-8'))
    listed={x['path'] for x in data['files']}
    actual={p.relative_to(ROOT).as_posix() for p in ROOT.rglob('*') if p.is_file() and p.name!='PACKAGE_MANIFEST.json' and '__pycache__' not in p.parts and p.suffix!='.pyc'}
    assert listed==actual, 'manifest paths missing/extra: '+str((sorted(actual-listed),sorted(listed-actual)))
    for x in data['files']:
        b=(ROOT/x['path']).read_bytes()
        assert len(b)==x['bytes'] and hashlib.sha256(b).hexdigest()==x['sha256'],x['path']
    print('PASS manifest integrity',len(listed),'files')
if __name__=='__main__':main()
