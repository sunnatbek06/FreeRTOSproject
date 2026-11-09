# FreeRTOS Spacecraft Communication Simulator

Educational mission-phase spacecraft communication system using **real FreeRTOS tasks and queues**, the Linux GCC_POSIX simulator port, and a repeatable measurement pipeline.

## Status

- Initial FreeRTOS Linux build and 9-second smoke simulation: **passed** in GitHub Actions on November 9, 2026 ([evidence](https://github.com/sunnatbek06/FreeRTOSproject/actions/runs/42571906618)).
- Initial CSV analysis unit tests: **passed** in the same run.
- Full E1–E9 experiments and controlled host replication: **not yet complete**.
- System is an academic scheduler simulation, **not flight software**.

## Simulated design

Three phases: Launch, Ascent, Orbit Insertion. Periodic telemetry, periodic ground commands, emergency injector, three priority-aware handlers, phase manager, queue monitor, logger, and mission controller. Emergency handler has priority 5; phase manager 4; telemetry/command worker priorities are varied according to the selected scheduling policy.

| Mission phase | Telemetry period | Command period | Dynamic telemetry / command priority |
| --- | --- | --- | --- |
| Launch | 50 ms | 160 ms | 3 / 2 |
| Ascent | 100 ms | 60 ms | 2 / 3 |
| Orbit insertion | 40 ms | 100 ms | 3 / 2 |

Worker deadlines are 100 ticks (telemetry), 80 ticks (command), 20 ticks (emergency), at nominal 1000 ticks/s.

## Build in Linux

On macOS use **Ubuntu in a VM or Linux container**, rather than attempting a native GCC_POSIX build. Full instructions: [docs/MACOS_SETUP.md](docs/MACOS_SETUP.md).

```bash
sudo apt-get update && sudo apt-get install -y build-essential cmake ninja-build git python3
cmake -S . -B build -G Ninja -DCMAKE_BUILD_TYPE=Debug
cmake --build build -j2
python3 -m unittest discover -s tests -v
mkdir -p results
./build/spacecraft_sim --policy dynamic --duration 30 --run-id baseline01 > results/baseline01.csv 2> results/baseline01.txt
python3 scripts/analyze.py results/baseline01.csv results/baseline01_summary.csv
```

The first CMake configure downloads FreeRTOS-Kernel **V11.1.0** via FetchContent. To use a local kernel checkout, set `-DFREERTOS_KERNEL_PATH=/absolute/path/to/FreeRTOS-Kernel`.

## Options and experiments

```bash
./build/spacecraft_sim --policy dynamic|static|equal|inverted --duration 60 \
  --stress 1 --telemetry-queue 16 --emergency-interval 3000 --run-id test01
```

The pipe-separated values above describe alternatives for `--policy`: select **one** of the four. Real example: `--policy dynamic`.

Read [docs/EXPERIMENTS.md](docs/EXPERIMENTS.md) for the nine planned experiment scenarios. Each should be repeated three times on a controlled Linux environment. Record the command line, raw CSV, stderr COUNTS, kernel version, build flags, OS, CPU, summary CSV, and contribution evidence.

## Interpreting results

The measured latency is queue entry to completion in **nominal FreeRTOS scheduler ticks**. It includes synthetic workload and scheduler delays, not radio transmission time. The Linux host, terminal/CSV I/O, and POSIX simulator introduce jitter and prevent real flight-time guarantees. Verify the stderr COUNTS diagnostics (including lost logger events and undrained queues) before trusting CSV totals.

## Teamwork

See [docs/CONTRIBUTIONS.md](docs/CONTRIBUTIONS.md) to record actual work completed by the three members. Commit authorship, reviews, test artifacts, and real Notion history should be documented honestly.
