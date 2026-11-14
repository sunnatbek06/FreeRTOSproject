# Test evidence and verification status

Review edition, 15 November 2026. All dates in prose use Korea time. Raw Actions timestamps are UTC.

## Verified code and build

Tested code revision: `1abe724835a4779390df2b0b9cc7e73e281a413e`.

`src/main.c` SHA256: `8d71aaec75cafeb4442112a6f7237af3df94c98d736b6cfbb0134f1faacde342`.

FreeRTOS V11.1.0 resolves to `dbf70559b27d39c1fdb68dfb9a32140b6a6777a0`.

[Linux build and smoke test, push](https://github.com/sunnatbek06/FreeRTOSproject/actions/runs/43622890402) and [PR check](https://github.com/sunnatbek06/FreeRTOSproject/actions/runs/43622895576) completed successfully. The workflow configures CMake Debug, compiles the real kernel/application, runs the 9-second simulator and analyzes its trace.

## Test inventory

| Check | Result | Evidence |
|---|---|---|
| Analyzer and evidence unit tests | 12 passed on Mac and Linux | `evidence/local-unit-tests.txt`, CI steps |
| Invalid CLI checks | 12 rejected with exit 2 | Contention workflow CLI step |
| Linux kernel and application build | Passed | Build/smoke and experiment workflows |
| Original E1-E9 suite | 27 / 27 passed | Original archive and workflow |
| Revised E1-E9 suite | 27 / 27 passed | Three repetition archives and workflow |
| CPU-demand C1-C6 suite | 18 / 18 passed | Contention archive and workflow |
| Independent archived-trace audit | 72 / 72 passed | `evidence/analysis/validation.json` |
| Native Mac simulator execution | Not performed | No Linux VM/container on development Mac |
| Target hardware timing | Not performed | Host simulation only |

A passed experiment means the process completed and evidence was consistent. It does not mean every message met its deadline. The contention suite deliberately records legitimate misses and input drops.

## Unit and negative tests

The three original analyzer tests cover linear-interpolated p95, a mixed completed/missed/dropped sample and missing CSV columns. Nine added tests cover valid inclusive deadline equality, lost logger events, undrained queues, counter disagreement, missing transition, deadline misclassification, early finish, channel-specific monitor-depth attribution and an accepted but unfinished message.

The twelve executable CLI cases reject unknown policy, too-short duration, negative duration, nonnumeric duration, zero queue capacity, excessive stress, excessive CPU demand, too-small emergency interval, a comma-containing run ID, an overlong run ID, a missing policy value and an unknown flag. These exercise real argument parsing before scheduler startup. Unit fixtures are synthetic test data and are separate from experimental evidence.

## Trace reconciliation

Each archived run has one ID, one final completion event and the transition sequence ASCENT then ORBIT_INSERTION. Final accepted counts equal final completed counts for every channel. Completed and dropped event counts agree with independent stderr counters. All input/event queues are empty and logger loss is zero. Numeric fields and deadline classifications pass validation. Every channel has actual completions.

These checks detect incomplete shutdown observations that process exit alone can miss. They do not measure periodic release jitter, exact queue high-water marks, hardware fault response or per-message sequence preservation.

## Artifact provenance

| Suite | Actions run | Archive |
|---|---|---|
| Original full matrix | 43341653550 | `evidence/full-27-runs.zip` |
| Revised full matrix | 43622890428 | `evidence/freertos-full-repetition-1.zip` through `-3.zip` |
| Supplementary contention | 43622890473 | `evidence/contention-18-runs.zip` |

The original archive SHA256 is `201e35ec4230123262909f9646f230180c9d3d0d8cbeaa12d6a91e0205d6cf92`.

The contention archive SHA256 is `37635efa7501a841d969f3c2368689e7a6053a31c6b0b455aac4f4b2f81dfe84`.

The three revised archive digests and all extracted-file digests are recorded in `evidence/analysis/SHA256SUMS.json` and `evidence/provenance.json`. Downloaded archive digests matched the GitHub artifact metadata. Raw files are preserved separately from recomputed analysis.

[Original full run](https://github.com/sunnatbek06/FreeRTOSproject/actions/runs/43341653550), [revised full run](https://github.com/sunnatbek06/FreeRTOSproject/actions/runs/43622890428), [contention run](https://github.com/sunnatbek06/FreeRTOSproject/actions/runs/43622890473).

## Host control and repeatability

The original 27 cases ran sequentially in one virtual-machine job. Revised repetitions each execute nine cases on an isolated runner, so within-repetition scenarios share a runner but between-repetition hosts can differ. Contention cases execute six scenarios in repetition-major order on one runner. Exact CPU and toolchain descriptions are retained beside the raw data. Virtual infrastructure is not a physically invariant laboratory host.

Measurements use nominal FreeRTOS ticks. CPU demand uses a thread CPU-time clock. A 40,000-us demand can be observed as fewer than 40 nominal ticks when the host's tick thread runs slower than nominal. This is another reason not to interpret ticks as calibrated physical milliseconds.

## Remaining unverified items

Original course-rubric compliance, individual student contributions, historical Notion activity, final team review and target hardware behavior remain unverified. Names and IDs are user-provided. Notion stores the present project record and asks the members to confirm their own contributions. There is no fabricated attendance or individual-credit claim.
