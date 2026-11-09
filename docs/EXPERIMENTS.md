# Experiment protocol (planned; NOT completed)

Mission phases: Launch, Ascent, Orbit Insertion. The scheduler should compare adaptive, static, equal, and inverted priorities.

| ID | Purpose | Options |
|---|---|---|
| E1 | Dynamic baseline | --policy dynamic --duration 60 |
| E2 | Static baseline | --policy static --duration 60 |
| E3 | Equal priority | --policy equal --duration 60 |
| E4 | Inverted priority | --policy inverted --duration 60 |
| E5 | Small telemetry queue | --telemetry-queue 2 --duration 60 |
| E6 | Moderate CPU load | --stress 10 --duration 60 |
| E7 | Heavy CPU load | --stress 50 --duration 60 |
| E8 | Emergency bursts | --emergency-interval 100 --duration 60 |
| E9 | Phase transition repeat | --policy dynamic --duration 60 |

Repeat each scenario at least three times with unique run IDs. Hold OS, CPU, FreeRTOS version, compiler and unrelated host workload constant. Export original event CSV, terminal diagnostics, summary CSV, and GitHub Actions evidence. Quantify latency distribution, misses, queue depth, drop count and actual phase transitions.

The POSIX simulation is not spacecraft hardware and does not prove hard-real-time deadlines. Physical device timing would require a hardware timer/trace facility.

Actual team collaboration and contributions must be recorded truthfully, with links to individual commits.
