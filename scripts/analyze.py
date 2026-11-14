#!/usr/bin/env python3
"""Aggregate real FreeRTOS simulator CSV events. Never fabricates results."""
import argparse
import csv
from collections import defaultdict
from pathlib import Path

REQUIRED = {"run_id", "tick", "phase", "channel", "event",
            "queue_depth", "latency_ticks", "deadline_ticks"}


def percentile(data, p):
    ordered = sorted(data)
    if not ordered:
        return ""
    location = (len(ordered) - 1) * p
    a = int(location)
    b = min(a + 1, len(ordered) - 1)
    return round(ordered[a] + (ordered[b] - ordered[a]) * (location - a), 3)


def summarize(path):
    groups = defaultdict(lambda: {"latencies": [], "misses": 0, "drops": 0, "depth": 0})
    with Path(path).open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream)
        if not REQUIRED.issubset(reader.fieldnames or []):
            raise ValueError("Missing required CSV columns")
        for line, row in enumerate(reader, 2):
            try:
                depth = int(row["queue_depth"])
                latency = int(row["latency_ticks"])
            except (ValueError, TypeError) as exc:
                raise ValueError(f"Invalid numeric data on line {line}") from exc
            channel = row["channel"]
            if channel == "monitor" and row["event"].endswith("_depth"):
                channel = row["event"][:-6]
            key = (row["run_id"], row["phase"], channel)
            result = groups[key]
            result["depth"] = max(result["depth"], depth)
            if row["event"] in ("completed", "handled", "deadline_miss"):
                result["latencies"].append(latency)
                result["misses"] += row["event"] == "deadline_miss"
            if row["event"] == "dropped":
                result["drops"] += 1
    output = []
    for (run, phase, channel), result in sorted(groups.items()):
        latencies = result["latencies"]
        output.append({
            "run_id": run, "phase": phase, "channel": channel,
            "processed": len(latencies),
            "median_latency_ticks": percentile(latencies, .5),
            "p95_latency_ticks": percentile(latencies, .95),
            "max_latency_ticks": max(latencies) if latencies else "",
            "deadline_misses": result["misses"],
            "deadline_miss_percent": round(100 * result["misses"] / len(latencies), 2) if latencies else "",
            "drop_events_logged": result["drops"],
            "max_queue_depth": result["depth"],
        })
    return output


COLUMNS = [
    "run_id", "phase", "channel", "processed",
    "median_latency_ticks", "p95_latency_ticks", "max_latency_ticks",
    "deadline_misses", "deadline_miss_percent", "drop_events_logged", "max_queue_depth",
]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source")
    parser.add_argument("destination")
    args = parser.parse_args()
    rows = summarize(args.source)
    with Path(args.destination).open("w", newline="", encoding="utf-8") as out:
        writer = csv.DictWriter(out, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} summary groups")
    print("Compare with stderr COUNTS; lost log events can cause under-counting.")


if __name__ == "__main__":
    main()
