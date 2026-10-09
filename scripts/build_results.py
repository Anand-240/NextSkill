"""Regenerate measured demo results offline; never request SerpApi."""
import json
from pathlib import Path
from unittest.mock import patch
from engine import run, SerpClient, headline_picks
ROOT = Path(__file__).resolve().parents[1]

def summary(r):
    picks = headline_picks(r['ranked'])
    return {
        **{k:r[k] for k in ('role','threshold','core_share','retrieved_dates','raw','deduplicated','ignored')},
        'experience_excluded':len(r['experience_excluded']), 'eligible':r['eligible_count'],
        'scored':len(r['jobs']), 'matches':r['ready'],
        'must_haves_met':r.get('must_haves_met',0),
        'fastest_win':(picks['fastest'] or {}).get('skill'), 'biggest_unlock':(picks['biggest'] or {}).get('skill'),
        'ranked':[{'skill':x['skill'],'display_skill':x['display_skill'],'unlocked':x['unlocked_count'],
                   'hours':round(x['hours'],2) if x['hours'] else None,'course_confidence':x['confidence'],
                   'jobs_per_hour':round(x['score'],3) if x['score'] else None,'videos':x['videos']} for x in r['ranked']],
        'bootstrap':{k:r['bootstrap'][k] for k in ('top_share','shares','samples')},
        'hour_variation':{'top_share':round(r['robustness']['top_share'],4),'checks':r['robustness']['samples']},
        'confidence':r['robustness']['label'],
        'curve':[{'skill':x['skill'],'hours':round(x['hours'],2),'cumulative_hours':round(x['cumulative_hours'],2),
                  'gained':x['jobs_gained'],'total':x['total_jobs']} for x in r['opportunity']['steps']],
        'greedy_vs_exact':r['opportunity']['quality'],'distance':r['distance']['counts'],
        'flags':{'limited_data':r['limited_data'],'dictionary_warning':r['dictionary_warning'],
                 'hours_unknown':r['opportunity']['hours_unknown']}}

def build():
    output={}
    with patch('engine._request',side_effect=AssertionError('Offline build forbids requests')):
        for role,city,resume in [('Frontend Developer','Bengaluru','HTML, CSS, JavaScript'),('Data Analyst','Noida','Excel, basic Python')]:
            r=run(role,city,resume=resume,client=SerpClient(use_fixtures=True,cache_only=True),experience_level='Fresher')
            output[city]=summary(r)
    return {'note':'Generated offline by scripts/build_results.py. Seed 2026.','after':output}
if __name__=='__main__':
    (ROOT/'reports/final_results.json').write_text(json.dumps(build(),indent=2,ensure_ascii=False)+'\n')
