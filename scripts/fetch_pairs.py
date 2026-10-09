"""Explicit saved-market collection, using the durable Phase C cap."""
import argparse
import json
from engine import ROOT,fetch_jobs,analyze_jobs,course_videos,canonical_manual_skills
from scripts.build_data import BuildClient,publish_usage,_write_json
PERSONAS={'Frontend Developer':'HTML, CSS, JavaScript','Data Analyst':'Excel, basic Python',
          'Python Developer':'Python, Git','Accountant':'Excel, Accounting',
          'Digital Marketing Executive':'Canva, Social Media Marketing'}
INITIAL=[('Frontend Developer','Bengaluru'),('Data Analyst','Noida'),('Data Analyst','Hyderabad'),
         ('Data Analyst','Pune'),('Data Analyst','Jaipur'),('Data Analyst','Indore'),
         ('Accountant','Jaipur'),('Digital Marketing Executive','Dehradun')]
EXTRA=[('Python Developer','Bengaluru'),('Python Developer','Kochi'),('Accountant','Mumbai'),
       ('Accountant','Indore'),('Digital Marketing Executive','Pune'),
       ('Digital Marketing Executive','Chennai'),('Frontend Developer','Hyderabad')]

def collect(pairs):
    manifest_path=ROOT/'demo_data/manifest.json'
    manifest=json.loads(manifest_path.read_text()) if manifest_path.exists() else []
    for role,city in pairs:
        if any(x['role']==role and x['city']==city for x in manifest):continue
        client=BuildClient('C','jobs')
        original=(role,city) in INITIAL[:2]
        low=city=='Dehradun'
        jobs=fetch_jobs(role,city,pages=3 if original else 1,client=client,
                        experience_level=None if low else 'Fresher')
        analysis=analyze_jobs(jobs,canonical_manual_skills(PERSONAS[role]),experience_level='Fresher')
        for skill in analysis['candidates'][:3]:
            course_videos(skill,BuildClient('C','course'))
        manifest.append({'id':(role+'-'+city).lower().replace(' ','-'),'role':role,'city':city,
                         'resume':PERSONAS[role],'pages':3 if original else 1,
                         'query_scope':'base only' if low else 'base plus fresher and junior',
                         'low_data_case':low})
        _write_json(manifest_path,manifest);publish_usage()
        print('PAIR',role,city,'eligible',analysis['eligible_count'],'scored',len(analysis['jobs']),flush=True)
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--extended',action='store_true');args=parser.parse_args()
    collect(EXTRA if args.extended else INITIAL)
