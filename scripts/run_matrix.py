#!/usr/bin/env python3
"""Run the experimental scenarios and preserve genuine raw simulator output."""
import argparse
import csv
import subprocess
import sys
from pathlib import Path
from analyze import summarize, COLUMNS

SCENARIOS = [
    ("E1_dynamic_baseline", "dynamic", 1, 16, 3000),
    ("E2_static", "static", 1, 16, 3000),
    ("E3_equal", "equal", 1, 16, 3000),
    ("E4_inverted", "inverted", 1, 16, 3000),
    ("E5_small_queue", "dynamic", 1, 2, 3000),
    ("E6_moderate_stress", "dynamic", 10, 16, 3000),
    ("E7_heavy_stress", "dynamic", 50, 16, 3000),
    ("E8_emergency_burst", "dynamic", 1, 16, 100),
    ("E9_transition_repeat", "dynamic", 1, 16, 3000),
]


def run(executable, destination, duration, repetitions):
    destination.mkdir(parents=True, exist_ok=True)
    summary_rows = []
    manifest_rows = []
    for scenario, policy, stress, depth, interval in SCENARIOS:
        for repetition in range(1, repetitions + 1):
            identifier = f"{scenario}_r{repetition}"
            events = destination / f"{identifier}.csv"
            diagnostics = destination / f"{identifier}.txt"
            command = [
                str(executable.resolve()), "--policy", policy,
                "--duration", str(duration), "--stress", str(stress),
                "--telemetry-queue", str(depth),
                "--emergency-interval", str(interval), "--run-id", identifier
            ]
            print(f"Running {identifier}", flush=True)
            with events.open("w", encoding="utf-8") as stdout, diagnostics.open("w", encoding="utf-8") as stderr:
                completed = subprocess.run(command, stdout=stdout, stderr=stderr,
                                           timeout=duration + interval / 1000 + 30, check=False)
            output = events.read_text(encoding="utf-8")
            diagnostic_text = diagnostics.read_text(encoding="utf-8")
            if completed.returncode != 0:
                raise RuntimeError(f"{identifier}: exit code {completed.returncode}; see {diagnostics}")
            if ",mission,finished," not in output or "COUNTS " not in diagnostic_text:
                raise RuntimeError(f"{identifier}: incomplete shutdown evidence")
            grouped = summarize(events)
            if not any(row["channel"] == "emergency" and row["processed"] > 0 for row in grouped):
                raise RuntimeError(f"{identifier}: no handled emergency in output")
            for row in grouped:
                summary_rows.append({
                    "scenario": scenario, "repetition": repetition,
                    "policy": policy, "stress": stress, "telemetry_queue": depth,
                    "emergency_interval_ms": interval, "duration_seconds": duration, **row
                })
            manifest_rows.append({
                "scenario": scenario, "repetition": repetition, "run_id": identifier,
                "exit_code": completed.returncode, "events_csv": events.name,
                "diagnostics_file": diagnostics.name, "final_counts": diagnostic_text.strip().splitlines()[-1]
            })
    with (destination / "matrix_summary.csv").open("w", newline="", encoding="utf-8") as output:
        columns = ["scenario", "repetition", "policy", "stress", "telemetry_queue",
                   "emergency_interval_ms", "duration_seconds", *COLUMNS]
        writer = csv.DictWriter(output, fieldnames=columns)
        writer.writeheader()
        writer.writerows(summary_rows)
    with (destination / "matrix_manifest.csv").open("w", newline="", encoding="utf-8") as output:
        writer = csv.DictWriter(output, fieldnames=list(manifest_rows[0]))
        writer.writeheader()
        writer.writerows(manifest_rows)
    print(f"Finished {len(manifest_rows)} real runs; {len(summary_rows)} grouped rows.", flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--executable", default="build/spacecraft_sim", type=Path)
    parser.add_argument("--output", default="results/matrix", type=Path)
    parser.add_argument("--duration", type=int, default=60)
    parser.add_argument("--repetitions", type=int, default=3)
    args = parser.parse_args()
    if not 9 <= args.duration <= 3600 or not 1 <= args.repetitions <= 20:
        parser.error("duration must be 9..3600 and repetitions 1..20")
    run(args.executable, args.output, args.duration, args.repetitions)


if __name__ == "__main__":
    main()
