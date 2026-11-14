# Experiment protocol and interpretation

Review edition, 15 November 2026. Original results and supplementary results remain separate.

## Original E1-E9 matrix

All missions last 60 nominal seconds, split into three 20-second phases. Each scenario has three repetitions. Unspecified options use defaults. Telemetry queue capacity defaults to 16 and emergency interval to 3,000 ms.

| ID | Purpose | Policy | Loop stress | Telemetry capacity | Emergency interval |
|---|---|---|---|---|---|
| E1 | Baseline | dynamic | 1 | 16 | 3000 ms |
| E2 | Static comparison | static | 1 | 16 | 3000 ms |
| E3 | Equal comparison | equal | 1 | 16 | 3000 ms |
| E4 | Inverted comparison | inverted | 1 | 16 | 3000 ms |
| E5 | Small queue | dynamic | 1 | 2 | 3000 ms |
| E6 | Moderate loop load | dynamic | 10 | 16 | 3000 ms |
| E7 | Heavy loop load | dynamic | 50 | 16 | 3000 ms |
| E8 | Frequent emergency injection | dynamic | 1 | 16 | 100 ms |
| E9 | Baseline transition repeat | dynamic | 1 | 16 | 3000 ms |

E9 duplicates E1 parameters and supplies additional repeatability evidence. It is not an independent fault or scheduling condition. Load labels describe loop multipliers; they do not prove CPU saturation. E8 uses a periodic 100 ms injector, not simultaneous burst packets. The original protocol names are retained for traceability, with their actual behavior stated here.

## Supplementary C1-C6 matrix

Each mission lasts 15 nominal seconds, with three repetitions per scenario. Sources retain their original phase-dependent periods. All cases use loop stress 1 and emergency interval 100 ms. Telemetry CPU demand doubles in orbit insertion. Emergency processing receives no added CPU budget.

| ID | Policy | Added base worker CPU time | Telemetry capacity |
|---|---|---|---|
| C1 | dynamic | 40000 us | 16 |
| C2 | static | 40000 us | 16 |
| C3 | equal | 40000 us | 16 |
| C4 | inverted | 40000 us | 16 |
| C5 | dynamic | 40000 us | 2 |
| C6 | dynamic | 20000 us | 16 |

The CPU budget uses thread CPU time and is a lower-bound demand target with chunk overhead. It is additional to the original burn loop. C1-C4 compare policies under contention. C1 versus C5 studies a queue capacity change. C1 versus C6 studies workload reduction. These comparisons still include the design's producer-priority effects.

## Evidence and statistics

Preserve exact code revision, C/config/binary hashes, kernel commit, compiler, build type, host description, raw CSV, stderr and manifest. Validate accepted/completed/drop counters against trace counts. Reject incomplete or lost-logger traces. Keep legitimate deadline misses and input drops in the dataset.

Report completed count, miss count and proportion, median/p95/maximum tick latency, drop count and maximum observed queue depth. Provide run-level tables and pooled raw-sample summaries. Pooled results combine unequal sample counts and do not replace variability across runs. Do not claim statistical significance from three sequential repetitions or treat every message as an independent policy experiment.

The first complete suite on November 13 used one virtual runner for all 27 runs. The revised suite runs one isolated runner per repetition. The supplemental 18 cases execute on one virtual runner. None provides an invariant physical CPU, a randomized scenario order or hardware real-time guarantees. GitHub shared infrastructure, host contention and clock behavior remain confounders.
