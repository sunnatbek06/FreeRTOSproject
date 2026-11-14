"""Check invalid CLI values fail before starting the scheduler."""
import subprocess
import sys
CASES=[['--policy','bogus'],['--duration','8'],['--duration','-1'],['--duration','text'],
       ['--telemetry-queue','0'],['--stress','1001'],['--service-us','1000001'],
       ['--emergency-interval','99'],['--run-id','bad,id'],['--run-id','x'*48],['--policy'],['--unknown']]
for args in CASES:
    result=subprocess.run([sys.argv[1],*args],capture_output=True,text=True,timeout=5)
    if result.returncode!=2: raise AssertionError((args,result.returncode))
print(f'PASS: {len(CASES)} invalid argument checks')
