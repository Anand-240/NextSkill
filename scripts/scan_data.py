"""Check committed response text for contact data and retrieval provenance."""
import json
from pathlib import Path
from engine import ROOT,retrieval_date
from scripts.build_data import EMAIL,PHONE

def findings(value,path=''):
    out=[]
    if isinstance(value,dict):
        for key,item in value.items():out.extend(findings(item,path+'/'+key))
    elif isinstance(value,list):
        for i,item in enumerate(value):out.extend(findings(item,f'{path}/{i}'))
    elif isinstance(value,str):
        if EMAIL.search(value):out.append(path+' email')
        if not value.startswith(('https://','http://')) and PHONE.search(value):out.append(path+' phone')
    return out

def scan():
    problems=[];count=0
    for base in ('demo_data','tests/fixtures'):
        for path in (ROOT/base).rglob('*.json'):
            if path.name=='manifest.json':continue
            data=json.loads(path.read_text());count+=1
            problems.extend(f'{path.relative_to(ROOT)}: {f}' for f in findings(data))
            if isinstance(data,dict) and ('jobs_results' in data or 'video_results' in data) and not retrieval_date(data):
                problems.append(str(path.relative_to(ROOT))+': missing retrieval timestamp')
    return count,problems
if __name__=='__main__':
    count,problems=scan();print(f'Scanned {count} response files; findings: {len(problems)}')
    for problem in problems:print(problem)
    raise SystemExit(bool(problems))
