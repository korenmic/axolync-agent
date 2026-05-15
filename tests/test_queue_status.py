import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills-user" / "queue-status" / "scripts" / "queue_status.py"
FIXTURES = ROOT / "skills-user" / "queue-status" / "tests" / "fixtures"
FIXTURE_WORKSPACE = FIXTURES.parent

spec = importlib.util.spec_from_file_location("queue_status", SCRIPT)
queue_status = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules["queue_status"] = queue_status
spec.loader.exec_module(queue_status)


class QueueStatusTests(unittest.TestCase):
    def test_discovery_reports_no_queue_gracefully(self):
        with tempfile.TemporaryDirectory() as tmp:
            report = queue_status.discover_queue(Path(tmp))
            self.assertIsNone(report.active_queue)
            self.assertIn("no initiated queue found", queue_status.format_report(report))

    def test_markdown_fixture_classifies_reference_and_by_value(self):
        queue_path = FIXTURES / "sinq-markdown" / "local-task-queue.md"
        result = queue_status.add_reference_diagnostics(
            queue_status.parse_markdown_queue(queue_path, FIXTURE_WORKSPACE)
        )

        self.assertEqual(len(result.records), 2)
        self.assertEqual(queue_status._count_statuses(result.records)["done"], 2)
        self.assertEqual(queue_status._count_classifications(result.records)["by-reference"], 1)
        self.assertEqual(queue_status._count_classifications(result.records)["by-value"], 1)
        self.assertEqual(result.records[0].source_exists, True)

    def test_markdown_fixture_counts_only_enqueued_tasks(self):
        queue_path = FIXTURES / "sinq2-markdown" / "local-task-queue.md"
        result = queue_status.add_reference_diagnostics(
            queue_status.parse_markdown_queue(queue_path, FIXTURE_WORKSPACE)
        )
        counts = queue_status._count_statuses(result.records)

        self.assertEqual(len(result.records), 2)
        self.assertEqual(counts["done"], 1)
        self.assertEqual(counts["undone_total"], 1)
        self.assertEqual(counts["ready"], 1)
        self.assertEqual(
            queue_status._count_classifications(result.records)["by-reference"],
            2,
        )

    def test_json_fixture_parses_reference_only_queue_and_missing_sources(self):
        queue_path = FIXTURES / "sinq3-json" / "execution-queue.json"
        result = queue_status.add_reference_diagnostics(
            queue_status.parse_json_queue(queue_path, FIXTURE_WORKSPACE)
        )
        counts = queue_status._count_statuses(result.records)
        missing, drift = queue_status._reference_diagnostics(result.records)

        self.assertEqual(len(result.records), 3)
        self.assertEqual(counts["done"], 2)
        self.assertEqual(counts["blocked"], 1)
        self.assertEqual(counts["undone_total"], 1)
        self.assertEqual(
            queue_status._count_classifications(result.records)["by-reference"],
            3,
        )
        self.assertEqual([record.qid for record in missing], ["Q0002"])
        self.assertEqual([record.qid for record in drift], ["Q0003"])

    def test_markdown_fixture_reports_history_duplicates_without_double_counting(self):
        queue_path = FIXTURES / "sinq4-markdown" / "local-task-queue.md"
        result = queue_status.add_reference_diagnostics(
            queue_status.parse_markdown_queue(queue_path, FIXTURE_WORKSPACE)
        )
        counts = queue_status._count_statuses(result.records)

        self.assertEqual(len(result.records), 3)
        self.assertEqual(counts["done"], 2)
        self.assertEqual(counts["active"], 1)
        self.assertEqual(counts["undone_total"], 1)
        self.assertEqual(queue_status._count_classifications(result.records)["by-value"], 1)
        self.assertEqual(
            result.warnings,
            ["duplicate qids in non-active sections ignored for counts: Q-279"],
        )


if __name__ == "__main__":
    unittest.main()
