"""Budgeted build-only retrieval. A durable attempt is charged before each request."""
import hashlib
import json
import re
from pathlib import Path
from engine import ROOT, SerpClient, _request, _load_key, _check_error, stamp_response, _write_json
CAPS={'C':105,'D':30,'H':5}
LEDGER=ROOT/'cache/build_usage.json'
EMAIL=re.compile(r'[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}')
PHONE=re.compile(r'(?<![\w\d])(?:\+91[\s-]?)?[6-9](?:[ -]?\d){9}(?![\w\d])')

def redact(value):
    if isinstance(value,dict):
        return {k:redact(v) for k,v in value.items() if k.lower() not in {'api_key','account_email'}}
    if isinstance(value,list):return [redact(v) for v in value]
    if isinstance(value,str):
        value=EMAIL.sub('[REDACTED EMAIL]',value)
        # Preserve opaque IDs and source URLs; their digit sequences are not contact numbers.
        if value.startswith(('http://','https://')):return value
        return PHONE.sub('[REDACTED PHONE]',value)
    return value

def usage():
    return json.loads(LEDGER.read_text()) if LEDGER.exists() else {'attempts':[], 'accounts':[]}

def record_account(label):
    data=_request('account.json',{},_load_key())
    clean={k:data.get(k) for k in ('this_month_usage','total_searches_left')}
    ledger=usage();ledger['accounts'].append({'label':label,**clean});_write_json(LEDGER,ledger)
    print(label,clean,flush=True);return clean

def publish_usage():
    _write_json(ROOT/'reports/build_usage.json',usage())

class BuildClient(SerpClient):
    def __init__(self,phase,category='search'):
        super().__init__(call_cap=None)
        self.phase,self.category=phase,category
    def search(self,params,page=1):
        digest=hashlib.sha256(json.dumps(params,sort_keys=True).encode()).hexdigest()[:20]
        destination=ROOT/'demo_data'/f'search_{digest}.json'
        # Reuse exact demo responses, then existing validation fixtures, then local cache.
        probe=SerpClient(use_fixtures=True,cache_only=True)
        data=probe.search(params,page)
        if data:
            self.replay.extend(probe.replay);return data
        cached=self.cache_dir/f'search_{digest}.json'
        if cached.exists():
            data=json.loads(cached.read_text());self.replay.append({'query':params,'source':'cache'})
        else:
            ledger=usage();attempts=ledger['attempts']
            if len(attempts)>=160 or sum(x['phase']==self.phase for x in attempts)>=CAPS[self.phase]:
                raise RuntimeError('STOP: build search cap would be exceeded')
            if self.phase=='C' and self.category=='revision' and sum(x['phase']=='C' and x['category']=='revision' for x in attempts)>=15:
                raise RuntimeError('STOP: revision cap would be exceeded')
            attempts.append({'phase':self.phase,'category':self.category,'engine':params['engine'],
                             'query':params.get('q') or params.get('search_query'),'location':params.get('location')})
            _write_json(LEDGER,ledger)
            data=stamp_response(_request('search.json',params,_load_key()),fresh=True)
            self.live_calls+=1;self.replay.append({'query':params,'source':'live'})
        _check_error(data)
        data=redact(stamp_response(data));_write_json(destination,data)
        print(self.phase,self.category,params.get('q') or params.get('search_query'), 'saved',flush=True)
        return data
