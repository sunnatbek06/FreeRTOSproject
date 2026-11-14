#!/usr/bin/env python3
"""Reject incomplete simulator traces before using latency summaries."""
import argparse
import csv
import re
from collections import Counter
from pathlib import Path


def validate(events, diagnostics, duration=None):
    with Path(events).open(encoding='utf-8', newline='') as stream:
        reader = csv.DictReader(stream)
        required = {'run_id','tick','phase','channel','event','queue_depth','latency_ticks','deadline_ticks'}
        if not required.issubset(reader.fieldnames or []):
            raise ValueError('Missing required event columns')
        rows = list(reader)
    for row in rows:
        if row['phase'] not in ('LAUNCH','ASCENT','ORBIT_INSERTION'):
            raise ValueError('Invalid mission phase')
        for field in ('tick','queue_depth','latency_ticks','deadline_ticks'):
            if int(row[field]) < 0:
                raise ValueError('Negative event measurement')
    text = Path(diagnostics).read_text(encoding='utf-8')
    lines = [s for s in text.splitlines() if s.startswith('COUNTS ')]
    if len(lines) != 1:
        raise ValueError('Expected exactly one final COUNTS record')
    counts = dict(re.findall(r'(\w+)=(\d+)', lines[0]))
    remaining = re.search(r'remaining=(\d+)/(\d+)/(\d+)/(\d+)', lines[0])
    if not remaining or any(map(int, remaining.groups())):
        raise ValueError('Queues did not drain')
    if int(counts.get('dropped_log', '-1')) != 0:
        raise ValueError('Logger lost events')
    if len({r['run_id'] for r in rows}) != 1:
        raise ValueError('Expected one run ID')
    finished = [r for r in rows if r['channel'] == 'mission' and r['event'] == 'finished']
    if len(finished) != 1:
        raise ValueError('Missing or duplicate mission completion')
    phases = [r['phase'] for r in rows if r['channel'] == 'phase' and r['event'] == 'transition']
    if phases != ['ASCENT', 'ORBIT_INSERTION']:
        raise ValueError('Incorrect phase transition sequence')
    if duration is not None and int(finished[0]['tick']) < duration * 1000:
        raise ValueError('Mission ended before requested duration')
    for channel, suffix, deadline in [('telemetry','tel',100),('command','cmd',80),('emergency','emg',20)]:
        observed = Counter(r['event'] for r in rows if r['channel'] == channel)
        processed = sum(observed[e] for e in ['completed','handled','deadline_miss'])
        for key, actual in [('processed',processed),('dropped',observed['dropped'])]:
            if int(counts.get(f'{key}_{suffix}', '-1')) != actual:
                raise ValueError(f'{channel}: {key} counters disagree with trace')
        if int(counts.get(f'sent_{suffix}', '-1')) != processed:
            raise ValueError(f'{channel}: accepted messages did not all complete')
        if processed == 0:
            raise ValueError(f'{channel}: no completed messages')
        for r in rows:
            if r['channel'] == channel and r['event'] in ('completed','handled','deadline_miss'):
                if int(r['deadline_ticks']) != deadline or (int(r['latency_ticks']) > deadline) != (r['event'] == 'deadline_miss'):
                    raise ValueError(f'{channel}: deadline classification mismatch')
    return {'run_id': rows[0]['run_id'], 'events': len(rows), 'status': 'PASS', 'counts': counts}


if __name__ == '__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('events', type=Path); p.add_argument('diagnostics', type=Path)
    p.add_argument('--duration', type=int)
    a=p.parse_args()
    print(validate(a.events, a.diagnostics, a.duration))
