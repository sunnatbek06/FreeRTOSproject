import csv
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from analyze import percentile, summarize


class SummaryTests(unittest.TestCase):
    def test_percentile(self):
        self.assertEqual(percentile([], .95), "")
        self.assertEqual(percentile([1, 2, 3, 4, 5], .95), 4.8)

    def test_summary(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "events.csv"
            with path.open("w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow(["run_id", "tick", "phase", "channel", "event",
                                 "queue_depth", "latency_ticks", "deadline_ticks"])
                writer.writerow(["test", 1, "LAUNCH", "telemetry", "completed", 1, 8, 100])
                writer.writerow(["test", 2, "LAUNCH", "telemetry", "deadline_miss", 3, 120, 100])
                writer.writerow(["test", 3, "LAUNCH", "telemetry", "dropped", 4, 0, 100])
            result = summarize(path)[0]
            self.assertEqual(result["processed"], 2)
            self.assertEqual(result["deadline_misses"], 1)
            self.assertEqual(result["deadline_miss_percent"], 50.0)
            self.assertEqual(result["median_latency_ticks"], 64.0)
            self.assertEqual(result["drop_events_logged"], 1)
            self.assertEqual(result["max_queue_depth"], 4)

    def test_missing_columns(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bad.csv"
            path.write_text("run_id,phase\ntest,LAUNCH\n")
            with self.assertRaisesRegex(ValueError, "Missing required"):
                summarize(path)


if __name__ == "__main__":
    unittest.main()
