import csv
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from validate_evidence import validate
from analyze import summarize

HEADER=['run_id','tick','phase','channel','event','queue_depth','latency_ticks','deadline_ticks']
COUNTS='COUNTS sent_tel=1 processed_tel=1 dropped_tel=0 sent_cmd=1 processed_cmd=1 dropped_cmd=0 sent_emg=1 processed_emg=1 dropped_emg=0 dropped_log=0 remaining=0/0/0/0\n'
class EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.e=Path(self.tmp.name)/'events.csv';self.d=self.e.with_suffix('.txt')
        self.rows=[['x',20000,'ASCENT','phase','transition',0,0,0],['x',40000,'ORBIT_INSERTION','phase','transition',0,0,0],
                   ['x',1,'LAUNCH','telemetry','completed',0,100,100],['x',1,'LAUNCH','command','completed',0,0,80],
                   ['x',1,'LAUNCH','emergency','handled',0,0,20],['x',63300,'ORBIT_INSERTION','mission','finished',0,0,0]]
        self.write();self.d.write_text(COUNTS)
    def write(self):
        with self.e.open('w',newline='') as f:
            w=csv.writer(f);w.writerow(HEADER);w.writerows(self.rows)
    def test_valid_and_inclusive_deadline(self): self.assertEqual(validate(self.e,self.d,60)['status'],'PASS')
    def test_lost_log(self):
        self.d.write_text(COUNTS.replace('dropped_log=0','dropped_log=1'))
        with self.assertRaisesRegex(ValueError,'Logger'):validate(self.e,self.d,60)
    def test_undrained(self):
        self.d.write_text(COUNTS.replace('remaining=0/0/0/0','remaining=1/0/0/0'))
        with self.assertRaisesRegex(ValueError,'drain'):validate(self.e,self.d,60)
    def test_counter_mismatch(self):
        self.d.write_text(COUNTS.replace('processed_tel=1','processed_tel=2'))
        with self.assertRaisesRegex(ValueError,'counters'):validate(self.e,self.d,60)
    def test_transition_missing(self):
        self.rows.pop(0);self.write()
        with self.assertRaisesRegex(ValueError,'transition'):validate(self.e,self.d,60)
    def test_deadline_misclassification(self):
        self.rows[2][6]=101;self.write()
        with self.assertRaisesRegex(ValueError,'classification'):validate(self.e,self.d,60)
    def test_early_finish(self):
        self.rows[-1][1]=100;self.write()
        with self.assertRaisesRegex(ValueError,'ended'):validate(self.e,self.d,60)
    def test_monitor_depth_belongs_to_channel(self):
        self.rows.append(['x',200,'LAUNCH','monitor','telemetry_depth',7,0,0]);self.write()
        result=next(r for r in summarize(self.e) if r['channel']=='telemetry')
        self.assertEqual(result['max_queue_depth'],7)
        self.assertEqual(result['processed'],1)
    def test_accepted_inflight_message(self):
        self.d.write_text(COUNTS.replace('sent_tel=1','sent_tel=2'))
        with self.assertRaisesRegex(ValueError,'accepted'):validate(self.e,self.d,60)
