# FreeRTOS spacecraft communication simulator

An educational host application using real FreeRTOS tasks, queues and priorities across launch, ascent and orbit insertion.

## Assessment package

Start with [the deliverables index](deliverables/DELIVERABLES.md). It links the technical report, high-level and low-level designs, implementation guide, test evidence, presentation, speaker notes and preserved experiments.

## Verified status - 15 November 2026

- Linux Debug build, real simulator smoke test and 12 analysis/evidence unit tests passed.
- Twelve invalid executable CLI cases were rejected as expected.
- [Full 27-run rerun](https://github.com/sunnatbek06/FreeRTOSproject/actions/runs/43622890428) passed.
- [18 supplementary contention runs](https://github.com/sunnatbek06/FreeRTOSproject/actions/runs/43622890473) passed.
- All 72 preserved traces, including the earlier 27-run suite, passed independent counter and lifecycle checks.
- Tested C source revision: `1abe724835a4779390df2b0b9cc7e73e281a413e`. Documentation/evidence packaging commits preserve that C source.

The original loop workload gives almost entirely zero-tick latencies and cannot establish policy superiority. Added CPU demand exposes queueing and deadline misses. Dynamic priorities avoid measured misses in these cases but delay sources and reduce offered traffic. See the [technical report](docs/TECHNICAL_REPORT.md) for numbers and limitations.

## Build and run in Linux

```
sudo apt-get update
sudo apt-get install -y build-essential cmake ninja-build git python3
cmake -S . -B build -G Ninja -DCMAKE_BUILD_TYPE=Debug
cmake --build build -j2
python3 -m unittest discover -s tests -v
python3 scripts/check_cli.py build/spacecraft_sim
mkdir -p results/smoke
./build/spacecraft_sim --duration 9 --policy dynamic --run-id smoke01 > results/smoke/events.csv 2> results/smoke/diagnostics.txt
python3 scripts/validate_evidence.py results/smoke/events.csv results/smoke/diagnostics.txt --duration 9
```

CMake downloads FreeRTOS-Kernel V11.1.0. Offline builds can use `-DFREERTOS_KERNEL_PATH=/absolute/path/to/kernel`. The project restricts simulator execution to Linux. macOS development, Linux execution and all reproduction commands are covered in the [implementation guide](docs/IMPLEMENTATION_GUIDE.md).

## Experiments and analysis

```
python3 scripts/run_matrix.py --duration 60 --repetitions 3 --output results/full
python3 scripts/run_contention.py --repetitions 3 --output results/contention
python3 tools/review_results.py
```

The first command runs E1-E9. The second runs separate C1-C6 CPU-demand cases. The third extracts the preserved evidence archives if needed, independently validates all 72 traces and rebuilds the run/phase/pooled assessment tables. [Protocol](docs/EXPERIMENTS.md).

The simulator uses nominal kernel ticks, synthetic messages and POSIX process termination. It includes no radio or flight hardware. Native Mac simulator execution and target timing remain unverified. Queue depth is sampled, emergency latency excludes delayed fault-source release, and relative producer delays change offered traffic under load.

## Team and collaboration

| Member | Student ID |
|---|---|
| Esonov Sunnatbek Saydulla Ugli | 202412372 |
| Singla Vaidant | 202608452 |
| Rajbhandari Kusum | 202512310 |

[Notion project and collaboration home](https://app.notion.com/p/4188c3a60ac581cb90f6cc8691c96392). [Contribution record](docs/CONTRIBUTIONS.md). Individual contributions, original assignment-rubric compliance and final team review require confirmation. Historical meetings and student credit have not been invented.
