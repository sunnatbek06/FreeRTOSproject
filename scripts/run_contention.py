#!/usr/bin/env python3
"""Supplementary CPU-demand experiments. Separate from original E1-E9."""
import argparse
import csv
import json
import subprocess
from pathlib import Path
from validate_evidence import validate

SCENARIOS = [('C1_dynamic', 'dynamic', 40000, 16),
             ('C2_static', 'static', 40000, 16),
             ('C3_equal', 'equal', 40000, 16),
             ('C4_inverted', 'inverted', 40000, 16),
             ('C5_small_queue', 'dynamic', 40000, 2),
             ('C6_lower_demand', 'dynamic', 20000, 16)]

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--executable',type=Path,default=Path('build/spacecraft_sim'))
    p.add_argument('--output',type=Path,default=Path('results/contention'))
    p.add_argument('--repetitions',type=int,default=3)
    a=p.parse_args(); a.output.mkdir(parents=True,exist_ok=True)
    records=[]
    for rep in range(1,a.repetitions+1):
        for name,policy,demand,depth in SCENARIOS:
            ident=f'{name}_r{rep}'
            cmd=[str(a.executable.resolve()),'--duration','15','--policy',policy,'--service-us',str(demand),'--telemetry-queue',str(depth),'--emergency-interval','100','--run-id',ident]
            print(ident,flush=True)
            events=a.output/f'{ident}.csv'; diagnostics=events.with_suffix('.txt')
            with events.open('w') as out,diagnostics.open('w') as err:
                r=subprocess.run(cmd,stdout=out,stderr=err,timeout=60)
            if r.returncode: raise RuntimeError(f'{ident}: exit {r.returncode}')
            result=validate(events,diagnostics,15)
            records.append({'run_id':ident,'policy':policy,'service_us':demand,'telemetry_queue':depth,'command':cmd,'validation':result})
            (a.output/'manifest.json').write_text(json.dumps(records,indent=2))
if __name__=='__main__': main()
