# Assessment deliverables

Final technical review package - 15 November 2026. Team identities are included in the report and presentation. Individual-credit claims and rubric compliance remain pending confirmation.

## Main files

| Deliverable | File | Purpose |
|---|---|---|
| Technical report | [Technical_Report.pdf](Technical_Report.pdf) | Questions, methods, measured findings, limitations and references |
| High-level design | [High_Level_Design.pdf](High_Level_Design.pdf) | System boundary, architecture, mission lifecycle and policies |
| Low-level design | [Low_Level_Design.pdf](Low_Level_Design.pdf) | Records, tasks, queue ownership, algorithms, shutdown and interfaces |
| Test evidence | [Test_Evidence.pdf](Test_Evidence.pdf) | Executed checks, provenance, reconciliation and unverified items |
| Implementation guide | [Implementation_Guide.pdf](Implementation_Guide.pdf) | Linux build, smoke test, experiments, analysis and demonstration |
| Final presentation | [Spacecraft_Final_Presentation.pptx](Spacecraft_Final_Presentation.pptx) | 13 editable slides with native diagrams/charts and embedded chart-data snapshots |
| Speaker notes | [Speaker_Notes.md](Speaker_Notes.md) | Slide-by-slide talking points and demonstration guidance |

Editable document sources are in [docs](../docs): TECHNICAL_REPORT.md, HIGH_LEVEL_DESIGN.md, LOW_LEVEL_DESIGN.md, TEST_EVIDENCE.md and IMPLEMENTATION_GUIDE.md. [EXPERIMENTS.md](../docs/EXPERIMENTS.md) records the complete protocols. [CONTRIBUTIONS.md](../docs/CONTRIBUTIONS.md) records the team and confirmation gaps.

## Diagram images and editable sources

- [Architecture PNG](../docs/figures/architecture.png) and [SVG](../docs/figures/architecture.svg).
- [Mission phases/shutdown PNG](../docs/figures/mission_states.png) and [SVG](../docs/figures/mission_states.svg).
- [Queue/record ownership PNG](../docs/figures/queue_records.png) and [SVG](../docs/figures/queue_records.svg).

Diagrams were generated from explicit source definitions and checked against the implementation. The presentation architecture is also editable as native slide objects. The standalone SVGs preserve editable labels and shapes.

## Evidence and reproduction

- [Original 27-run archive](../evidence/full-27-runs.zip).
- [Revised repetition 1](../evidence/freertos-full-repetition-1.zip), [repetition 2](../evidence/freertos-full-repetition-2.zip), [repetition 3](../evidence/freertos-full-repetition-3.zip).
- [18 contention runs](../evidence/contention-18-runs.zip).
- [Independent validation](../evidence/analysis/validation.json), [run metrics](../evidence/analysis/run_metrics.csv), [phase metrics](../evidence/analysis/phase_metrics.csv), [pooled metrics](../evidence/analysis/pooled_metrics.csv).
- [Provenance](../evidence/provenance.json), [SHA256 digests](../evidence/analysis/SHA256SUMS.json), [local unit-test output](../evidence/local-unit-tests.txt).
- Rebuild derived tables with `python3 tools/review_results.py`; it extracts preserved archives when needed. Original raw files remain unchanged.

## Verified and unverified

Verified: Linux build/smoke, 12 unit tests, 12 CLI rejection cases, 27 revised full runs, 18 contention runs and independent audit of all 72 preserved traces. These results apply to the tested C source revision documented in the report. Native Mac simulator execution, physical hardware timing and opening the presentation in native PowerPoint were not verified. Slide previews, document pages and presentation package/chart structure were checked.

Original course rubric, individual member contributions and final team signoff remain unverified. This package is ready for technical assessment; it does not invent those missing approvals or historical records.

## Project links

- [Draft PR #1](https://github.com/sunnatbek06/FreeRTOSproject/pull/1).
- [Full rerun CI](https://github.com/sunnatbek06/FreeRTOSproject/actions/runs/43622890428).
- [Contention CI](https://github.com/sunnatbek06/FreeRTOSproject/actions/runs/43622890473).
- [Notion project and collaboration home](https://app.notion.com/p/4188c3a60ac581cb90f6cc8691c96392). The page is private until the user shares it with teammates. It contains a dated automated-work log, verified results and contribution-confirmation steps.
