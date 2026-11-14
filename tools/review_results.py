#!/usr/bin/env python3
"""Revalidate preserved raw traces and produce run/pooled assessment tables."""
import csv
import hashlib
import json
import sys
import zipfile
from collections import defaultdict
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from analyze import summarize, percentile
from validate_evidence import validate

ROOT=Path(__file__).resolve().parents[1]

def write_csv(path, rows):
    with path.open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

def process(paths,duration,suite):
    runs=[]; groups=defaultdict(lambda:{'latencies':[],'misses':0,'drops':0,'depth':0});checks=[]; phase_rows=[]
    for p in sorted(paths):
        result=validate(p,p.with_suffix('.txt'),duration);result['suite']=suite;checks.append(result)
        with p.open(encoding='utf-8',newline='') as stream:
            rows=list(csv.DictReader(stream))
        case=p.stem.rsplit('_r',1)[0]; local=defaultdict(lambda:{'latencies':[],'misses':0,'drops':0,'depth':0})
        for r in rows:
            c=r['channel']
            if c=='monitor' and r['event'].endswith('_depth'):c=r['event'][:-6]
            if c not in ('telemetry','command','emergency'):continue
            for g in [groups[(case,c)],local[c]]:
                g['depth']=max(g['depth'],int(r['queue_depth']))
                if r['event'] in ('completed','handled','deadline_miss'):
                    g['latencies'].append(int(r['latency_ticks']));g['misses']+=r['event']=='deadline_miss'
                elif r['event']=='dropped':g['drops']+=1
        for c,g in sorted(local.items()):runs.append(stats(suite,case,c,g,run=p.stem))
        phase_rows.extend({'suite':suite,**r} for r in summarize(p) if r['channel'] in ('telemetry','command','emergency'))
    pooled=[stats(suite,case,c,g) for (case,c),g in sorted(groups.items())]
    return runs,pooled,checks,phase_rows

def stats(suite,case,c,g,**extra):
    ls=g['latencies'];return {'suite':suite,'scenario':case,**extra,'channel':c,'processed':len(ls),'median_ticks':percentile(ls,.5),'p95_ticks':percentile(ls,.95),'max_ticks':max(ls),'misses':g['misses'],'miss_percent':round(g['misses']/len(ls)*100,3),'drops':g['drops'],'max_observed_depth':g['depth']}

def main():
    archives=[('full-27-runs.zip','full'),('contention-18-runs.zip','contention')]
    archives += [(f'freertos-full-repetition-{i}.zip',f'final/repetition-{i}') for i in range(1,4)]
    for archive,target in archives:
        dest=ROOT/'evidence'/target
        if not dest.exists():
            with zipfile.ZipFile(ROOT/'evidence'/archive) as z:
                if any(Path(n).name != n for n in z.namelist()):
                    raise ValueError('Expected flat archive members')
                z.extractall(dest)
    final=ROOT/'evidence/final'
    runs,pooled,checks,phases=[],[],[],[]
    for suite,paths,duration in [('original_2026_11_13',(ROOT/'evidence/full').glob('E*.csv'),60),('full_rerun',final.glob('repetition-*/E*.csv'),60),('contention',(ROOT/'evidence/contention').glob('C*.csv'),15)]:
        a,b,c,d=process(paths,duration,suite);runs+=a;pooled+=b;checks+=c;phases+=d
    dest=ROOT/'evidence/analysis';dest.mkdir(exist_ok=True)
    write_csv(dest/'run_metrics.csv',runs);write_csv(dest/'pooled_metrics.csv',pooled);write_csv(dest/'phase_metrics.csv',phases)
    (dest/'validation.json').write_text(json.dumps(checks,indent=2))
    hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'evidence').rglob('*')) if p.is_file() and p.parent!=dest}
    (dest/'SHA256SUMS.json').write_text(json.dumps(hashes,indent=2))
    print('Validated',len(checks),'runs:',dict((s,sum(c['suite']==s for c in checks)) for s in sorted(set(c['suite'] for c in checks))))
    for r in pooled:
        if r['suite']=='full_rerun':print(r)
if __name__=='__main__':main()
