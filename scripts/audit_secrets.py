"""Scoped, value-free secret audit. Does not contact a service or print secrets."""
import argparse
import hashlib
import ast
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
ASSET_MANIFEST=ROOT/'scripts/reviewed-assets.json'
REVIEWED_ASSET_HASHES={f['sha256'] for f in json.loads(ASSET_MANIFEST.read_text()).get('files',[])} if ASSET_MANIFEST.exists() else set()
EXCLUDED={'.git','.venv','venv','__pycache__','.pytest_cache','.DS_Store'}
PRIVATE={'.private','.history','raw-evidence','recordings','artifacts'}
TOKEN=re.compile(r'\b(?:wk-|ws-|ak-|as-|sk-|hf_)[A-Za-z0-9_-]{12,}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY|\beyJ[A-Za-z0-9_-]{15,}\.[A-Za-z0-9_-]{15,}\.[A-Za-z0-9_-]{10,}')
SENSITIVE=re.compile(r'(?:api[_-]?key|token|secret|password|authorization)',re.I)
ASSIGN=re.compile(r'^\s*(?:export\s+)?([A-Z][A-Z0-9_]*)\s*=\s*[\"\']?([^\s\"\']+)',re.M)
BEARER=re.compile(r'\bBearer\s+([A-Za-z0-9._-]{12,})')
PERSONAL=re.compile(r'/Users/[A-Za-z0-9][^\s\"\'<>]*|https://(?!YOUR-SERVER|example)[a-zA-Z0-9_-]+(?:--[a-zA-Z0-9_-]+)+\.modal\.(?:run|host)')

def placeholder(value):
    # Exact demonstration values only; real tokens containing an English word still count.
    return value in {
        "wk-REPLACE", "ws-REPLACE", "invalid-test-key", "Bearer invalid-test-key",
        "Bearer wk-invalid.ws-invalid", "Bearer wk-test.ws-test", "Bearer secret-test",
        "Bearer wk-ID.ws-SECRET", "wk-ID.ws-SECRET",
    }


def scan(label, raw, *, python=False, identifiers=False):
    findings=[]
    try: text=raw.decode('utf-8')
    except UnicodeDecodeError:
        if hashlib.sha256(raw).hexdigest() in REVIEWED_ASSET_HASHES:
            return []
        # Image/binary content cannot be cleared by a text scanner.
        return [{'file':label,'line':None,'kind':'binary_requires_manual_review'}]
    for pattern,kind in [(TOKEN,'credential_pattern'),(BEARER,'bearer_literal')]+([(PERSONAL,'personal_identifier')] if identifiers else []):
        for match in pattern.finditer(text):
            if not placeholder(match.group()):
                findings.append({'file':label,'line':text.count('\n',0,match.start())+1,'kind':kind})
    for match in ASSIGN.finditer(text):
        if SENSITIVE.search(match[1]) and len(match[2])>=8 and not placeholder(match[2]) and not match[2].startswith(('$','{')) and not any(c in match[2] for c in ('(', ')')):
            findings.append({'file':label,'line':text.count('\n',0,match.start())+1,'kind':'environment_secret_assignment'})
    try:
        tree=ast.parse(text)
    except SyntaxError:
        if python: findings.append({'file':label,'line':None,'kind':'python_parse_error'})
        tree=ast.Module(body=[],type_ignores=[])
    if tree:
        for node in ast.walk(tree):
            if isinstance(node,(ast.Assign,ast.AnnAssign)):
                targets=node.targets if isinstance(node,ast.Assign) else [node.target]
                value=node.value
                if isinstance(value,ast.Constant) and isinstance(value.value,str) and len(value.value)>=12 and not placeholder(value.value):
                    if any(isinstance(t,ast.Name) and SENSITIVE.search(t.id) for t in targets):
                        findings.append({'file':label,'line':node.lineno,'kind':'hardcoded_credential_assignment'})
    # Report only location and category. Never echo the matched bytes.
    return list({(x['file'],x['line'],x['kind']):x for x in findings}.values())

def git(*args):
    r=subprocess.run(['git','-C',str(ROOT),*args],capture_output=True)
    if r.returncode:raise RuntimeError('Scoped Git inspection failed; inspect configuration privately.')
    return r.stdout

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--include-private',action='store_true',help='Scan private originals/history too; output locations only.')
    args=parser.parse_args()
    findings=[];count=0
    for p in sorted(ROOT.rglob('*')):
        rel=p.relative_to(ROOT)
        if any(x in EXCLUDED for x in rel.parts):continue
        if not args.include_private and any(x in PRIVATE for x in rel.parts):continue
        if p.is_symlink():
            findings.append({'file':str(rel),'line':None,'kind':'symlink_requires_review'});continue
        if not p.is_file():continue
        count+=1
        # Manually authored SVG is source; raster screenshots still need pixel review.
        raw=p.read_bytes()
        if p.suffix.lower() in ('.png','.jpg','.jpeg','.webp','.gif','.pdf','.mp4','.mov'):
            if hashlib.sha256(raw).hexdigest() not in REVIEWED_ASSET_HASHES:
                findings.append({'file':str(rel),'line':None,'kind':'media_requires_manual_review'})
                continue
        findings+=scan(str(rel),raw,python=p.suffix=='.py',identifiers=not any(x in PRIVATE for x in rel.parts))
    blobs=set();index_count=0
    if (ROOT/'.git').exists():
        top=git('rev-parse','--show-toplevel').decode().strip()
        if Path(top).resolve()!=ROOT.resolve():raise RuntimeError('Refusing parent Git repository.')
        # Inspect both index contents and the reachable/reflog history, independent of ignore rules.
        for entry in git('ls-files','--stage','-z').split(b'\0'):
            if not entry:continue
            meta,path=entry.split(b'\t',1);mode,sha,stage=meta.split();index_count+=1
            name=path.decode(errors='replace')
            if any(x in PRIVATE for x in Path(name).parts) or name.startswith('.env') and name!='.env.example':
                findings.append({'file':name,'line':None,'kind':'private_path_in_index'})
            raw=git('cat-file','blob',sha.decode()) if mode!=b'160000' else b''
            findings+=scan('index:'+name,raw,python=name.endswith('.py'),identifiers=True)
        objects=git('rev-list','--objects','--all','--reflog').splitlines()
        for row in objects:
            sha=row.split(b' ',1)[0].decode()
            if git('cat-file','-t',sha).strip()==b'blob':blobs.add(sha)
        fsck=git('fsck','--full','--no-reflogs','--unreachable').decode(errors='replace')
        for row in fsck.splitlines():
            fields=row.split()
            if len(fields)==3 and fields[1]=='blob':blobs.add(fields[2])
        for sha in sorted(blobs):
            # Blob path can be absent for unreachable objects; token/header detection still runs.
            findings+=scan('git-blob:'+sha,git('cat-file','blob',sha),identifiers=True)
    result={'scope':'public candidate + Git objects' if not args.include_private else 'public + private originals/history + Git objects',
            'files_scanned':count,'index_entries':index_count,'git_blobs_scanned':len(blobs),'findings':findings,
            'limits':'Pattern and assignment audit. Known reviewed binary assets are hash matched. Manual review required for arbitrary secrets and image pixels.'}
    print(json.dumps(result,indent=2))
    return 1 if findings else 0
if __name__=='__main__':
    try:raise SystemExit(main())
    except RuntimeError as exc:print(str(exc),file=sys.stderr);raise SystemExit(2)
