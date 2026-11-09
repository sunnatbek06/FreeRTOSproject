# OS Final Project — Technical Report (living draft)

**Title:** Spacecraft Communication Scheduling Across Mission Phases Using FreeRTOS

**Repository:** https://github.com/sunnatbek06/FreeRTOSproject  
**Implementation branch:** `feature/spacecraft-simulator`  
**Review:** https://github.com/sunnatbek06/FreeRTOSproject/pull/1  
**Date:** November 9, 2026  
**Evidence status:** Linux CI smoke passed. Full controlled E1–E9 measurements are pending.

## 1. Abstract

This project implements a spacecraft-inspired communication workload using FreeRTOS tasks, queues, task priorities, and periodic delays. The simulator progresses through launch, ascent, and orbit insertion while generating telemetry, ground commands, and emergency messages. Scheduling behavior is compared across static, equal, inverted and mission-adaptive priority policies. The implementation records event latencies, missed deadlines, queue occupancy and dropped messages. At this stage an automated Linux kernel build, nine-second smoke simulation, and analysis tests have passed. The experimental comparisons and recommendations will be completed using measured evidence.

## 2. Problem and objectives

Spacecraft communications may compete with time-critical events for CPU resources. If a task has insufficient priority, processing latency may increase and queued messages may be delayed or dropped. The objective is to evaluate whether adapting task priorities to mission phase improves responsiveness while preserving emergency handling.

Specific questions:

1. How does phase-dependent priority reassignment affect telemetry and ground-command latency?
2. Which task becomes deadline-sensitive during launch, ascent and orbit insertion?
3. How do queue depth and CPU stress change completion rate, deadline misses and message loss?
4. How consistently does the emergency task respond during phase transitions and high load?
5. What limitations prevent transferring simulator timing claims to real spacecraft hardware?

## 3. Architecture

The system uses the actual FreeRTOS task/queue APIs, rather than a Python imitation of a scheduler.

```
Telemetry generator ---> Telemetry queue ---> Telemetry worker ---+
Ground simulator  ---> Command queue   ---> Command worker   ----+---> Event queue ---> CSV logger
Fault injector    ---> Emergency queue ---> Emergency worker ----+
Phase manager ----> priority changes
Monitor ---------> periodic queue-depth events
Mission controller --> stop producers, drain messages, write final counters
```

Emergency processing runs at priority 5. The phase manager operates at priority 4, with telemetry and command workers typically at priority 2 or 3. The mission controller coordinates termination at priority 6. These are educational priority choices, not analytically proven optimal values.

## 4. Phase-dependent parameters

| Phase | Telemetry period | Command period | Dynamic telemetry priority | Dynamic command priority |
|---|---:|---:|---:|---:|
| Launch | 50 ms | 160 ms | 3 | 2 |
| Ascent | 100 ms | 60 ms | 2 | 3 |
| Orbit insertion | 40 ms | 100 ms | 3 | 2 |

Nominal deadlines are 100 kernel ticks for telemetry, 80 ticks for commands and 20 ticks for emergencies, at a nominal 1000 Hz tick rate. These are experiment design assumptions, not hardware requirements.

## 5. Methodology

The independent variables are priority policy, mission phase, synthetic CPU load, telemetry queue size, and emergency generation interval. The dependent measurements are processed count, median and 95th percentile latency, maximum latency, deadline-miss count and proportion, logged drop events, and maximum sampled queue depth.

Experiments E1–E9 are defined in [EXPERIMENTS.md](EXPERIMENTS.md). The target protocol uses a stable Linux host, 60-second missions, three repetitions per scenario, and preserved raw evidence. A shorter CI pilot tests that the pipeline executes correctly; it does not replace the controlled experiment matrix.

Measurements are captured by a separate logger task from a bounded FreeRTOS queue. At shutdown the simulator reports aggregate counters and remaining queue depths to stderr. If logged events are lost, the report must disclose incomplete instrumentation before computing comparisons.

## 6. Implementation and validation

Source: [src/main.c](../src/main.c)  
Build and host instructions: [MACOS_SETUP.md](MACOS_SETUP.md)  
Analysis: [scripts/analyze.py](../scripts/analyze.py)  
Matrix runner: [scripts/run_matrix.py](../scripts/run_matrix.py)

The first Linux GitHub Actions workflow completed its FreeRTOS CMake configuration, compilation, nine-second execution and CSV analysis with success. Verification reference: https://github.com/sunnatbek06/FreeRTOSproject/actions/runs/42571906618. This validates one smoke-test configuration, not all experimental scenarios or physical real-time behavior.

## 7. Findings

**Pending real E1–E9 experimental measurements.** This section must not contain fabricated latency values, miss rates or superiority claims.

When data are available, analyze the phase/channel samples and compare dynamic vs. static specifically in ascent, where their configured priorities differ. Compare emergency response separately from telemetry and commands. Include conditions and effect sizes, not just bar charts.

## 8. Validity and limitations

The GCC_POSIX FreeRTOS simulator runs on a general-purpose Linux host, subject to kernel scheduling jitter. Synthetic busy-work changes with CPU and compiler. Printing logs, queue operations, timer precision and host workload all influence results. Event latency captures application queue-to-completion time, not end-to-end radio propagation or hardware ISR latency. A high task priority does not by itself prove a hard deadline guarantee. This is not flight software, nor a safety-certified embedded system.

## 9. Collaboration and deliverables

Three-member roles and genuine work history should be documented in [CONTRIBUTIONS.md](CONTRIBUTIONS.md), with GitHub commit and review evidence and a real Notion cooperation-history link where the assignment requires it. An academic project should distinguish authored contributions from code generated through an assistant.

## 10. Conclusion (provisional)

The implemented architecture demonstrates a plausible method for examining phase-dependent FreeRTOS scheduling. CI proves that the initial simulator can build and complete a smoke run. The engineering claim—whether adaptive priorities materially improve mission-critical communication—remains unanswered until the controlled experiments have been collected, checked and analyzed.

## References

- FreeRTOS-Kernel official repository: https://github.com/FreeRTOS/FreeRTOS-Kernel
- FreeRTOS-Kernel CMake setup and port documentation: https://github.com/FreeRTOS/FreeRTOS-Kernel/blob/main/README.md
