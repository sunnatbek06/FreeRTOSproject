# Presentation speaker notes

13 slides, approximately 8-10 minutes plus a short demonstration. Team: Esonov Sunnatbek Saydulla Ugli (202412372), Singla Vaidant (202608452), Rajbhandari Kusum (202512310). Agree on speaking roles after each member reviews the material; these notes do not claim individual development ownership.

## 1. Spacecraft communication with FreeRTOS

Introduce the project as a host scheduling experiment inspired by spacecraft mission phases. It uses the real FreeRTOS kernel, but no spacecraft or radio hardware. Explain that the purpose is to investigate how communication tasks compete for processing time.

## 2. Research question

Explain why telemetry and command demand change across phases. The goal is to compare deadline behavior, queue congestion and throughput, while keeping emergency processing responsive. A policy that completes fewer generated messages can look fast, so latency must be interpreted with traffic counts.

## 3. Communication architecture

Follow the arrows from sources to independent queues to workers. A full input queue rejects a new message and counts the drop. Workers emit records to the event queue; a single logger writes CSV. A phase manager changes worker priorities, a monitor samples queues and a mission controller coordinates shutdown. The slide is a simplified editable view; the design document includes the full control roles.

## 4. Mission phases

For a 60-second experiment each phase lasts nominally 20 seconds. During ascent, command generation becomes more frequent and dynamic priorities favor the command worker. During orbit insertion telemetry becomes more frequent and its work increases. Actual phase observation can lag the boundary because the manager polls every 10 ticks.

## 5. Scheduling and measurement

Higher numeric FreeRTOS priorities run before lower ones when ready. The emergency worker remains at 5. The inverted policy is an unfavorable priority assignment, not a mutex-priority-inversion demonstration. Latency begins at actual message creation and ends at worker completion. Deadline equality passes. A missed message still counts as processed.

## 6. Evidence checks

Describe the 27-run revised matrix and the separate 18-run contention suite. The older 27-run suite is preserved too. Each trace is reconciled with final accepted, completed and dropped counters; logger loss and remaining queues must be zero. Unit tests exercise deliberate invalid traces. A passed consistency check does not mean all experiment deadlines were met.

## 7. Original workload

The original loop-only cases all have pooled p95 zero ticks. That means observations fall within a tick, not that processing consumes no time. Even the loop stress multiplier of 50 produces little pressure on these hosts. This is an honest negative result: the original workload cannot establish a policy advantage.

## 8. Added CPU demand

The supplementary cases add thread CPU-time demand: 40,000 us per base telemetry/command job, doubled for orbit telemetry. Lower demand uses 20,000 us. Equal and inverted priorities produce telemetry p95 above 1,700 nominal ticks. Explain the different clocks: host thread CPU microseconds are not identical to simulated kernel tick timing.

## 9. Misses and drops

Across three repetitions, equal priorities produce 171 telemetry misses, 48 command misses and 196 telemetry drops. Inverted priorities produce 192 telemetry misses and 137 drops. Static priorities produce 48 command misses. Dynamic priorities show no misses or drops in these cases. These are observed results for this implementation, not universal policy guarantees.

## 10. Traffic tradeoff

Dynamic priorities complete 453 telemetry messages and 369 commands across the three runs, while equal priorities complete 621 and 489, plus dropped telemetry attempts. Relative-delay sources have priority 2, so high-priority ready workers can postpone message generation. This changes offered traffic. Explain why the absence of misses alone does not establish global superiority.

## 11. Emergency handling and limits

Emergency completion maxima are zero or one nominal tick under contention, without measured emergency misses or input drops. However, the fault source is a schedulable task; if it runs late, that delay occurs before creation and is absent from the latency metric. Also disclose sampled queue peaks, host jitter and the absence of hardware validation.

## 12. Demonstration

Build in Linux, show the unit-test output and run a 9-second smoke mission. Display phase transition/priority rows and final COUNTS. Run the trace validator. Then run a 15-second CPU-demand case and show the distinction between input drops, completed messages and deadline misses. The implementation guide contains exact commands and expected interpretation.

## 13. Conclusion

State what was demonstrated: a real-kernel simulator and reproducible, independently checked evidence. Original demand is too small to resolve policy effects. Additional CPU demand reveals queueing and producer delays. Dynamic priorities help measured deadlines in these cases with a throughput tradeoff. Finish with the scope: descriptive host results, team review and individual contributions still require confirmation.

## Evidence references

- Tested code: https://github.com/sunnatbek06/FreeRTOSproject/tree/1abe724835a4779390df2b0b9cc7e73e281a413e
- Full rerun: https://github.com/sunnatbek06/FreeRTOSproject/actions/runs/43622890428
- Contention suite: https://github.com/sunnatbek06/FreeRTOSproject/actions/runs/43622890473
- Technical report and raw analysis: `docs/TECHNICAL_REPORT.md` and `evidence/analysis/`.
- Collaboration home: https://app.notion.com/p/4188c3a60ac581cb90f6cc8691c96392
