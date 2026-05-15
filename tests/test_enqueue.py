import importlib.util
import io
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills-user" / "enqueue" / "scripts" / "enqueue_tasks.py"

spec = importlib.util.spec_from_file_location("enqueue_tasks", SCRIPT)
enqueue_tasks = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules["enqueue_tasks"] = enqueue_tasks
spec.loader.exec_module(enqueue_tasks)


class EnqueueTests(unittest.TestCase):
    def test_discover_queue_state_creates_missing_queue(self):
        with tempfile.TemporaryDirectory() as tmp:
            state = enqueue_tasks.discover_queue_state(Path(tmp))

            self.assertTrue(state.created)
            self.assertTrue(state.queue_path.exists())
            self.assertEqual(state.next_qid_number, 1)
            self.assertIn("## Queued Items", state.queue_path.read_text(encoding="utf-8"))

    def test_discover_queue_state_continues_highest_qid(self):
        with tempfile.TemporaryDirectory() as tmp:
            queue_path = Path(tmp) / ".codex" / "local-task-queue.md"
            queue_path.parent.mkdir(parents=True)
            queue_path.write_text(
                "# Local Task Queue\n\n## Queued Items\n\n"
                "### Q-002\n- Status: `done`\n- Source: `inline procedural queue task`\n- Task: `old`\n\n"
                "### Q-011\n- Status: `queued`\n- Source: `inline procedural queue task`\n- Task: `new`\n",
                encoding="utf-8",
            )

            state = enqueue_tasks.discover_queue_state(Path(tmp))

            self.assertFalse(state.created)
            self.assertEqual(state.next_qid_number, 12)

    def test_resolve_source_selection_scopes_explicit_sources_and_tasks(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "spec" / "tasks.md"
            source.parent.mkdir(parents=True)
            source.write_text("- [ ] 1. Ship task\n", encoding="utf-8")

            selection = enqueue_tasks.resolve_source_selection(
                root,
                source_paths=["spec/tasks.md"],
                task_selectors=["  `1. Ship task`  "],
                inline_tasks=[" context-only task "],
            )

            self.assertEqual(selection.source_paths, (source.resolve(),))
            self.assertEqual(selection.task_selectors, ("1. Ship task",))
            self.assertEqual(selection.inline_tasks, ("context-only task",))

    def test_validate_source_selection_rejects_missing_scope(self):
        with tempfile.TemporaryDirectory() as tmp:
            selection = enqueue_tasks.resolve_source_selection(Path(tmp))

            with self.assertRaises(enqueue_tasks.EnqueueInputError):
                enqueue_tasks.validate_source_selection(selection)

    def test_parse_source_tasks_captures_checked_state_and_numbers(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "tasks.md"
            source.write_text(
                "- [x] 1. Finished task\n"
                "- [ ] 2. Runnable task\n"
                "- [ ] Backlog item without number\n",
                encoding="utf-8",
            )

            tasks = enqueue_tasks.parse_source_tasks(source)

            self.assertEqual([task.label for task in tasks], [
                "1. Finished task",
                "2. Runnable task",
                "Backlog item without number",
            ])
            self.assertEqual([task.checked for task in tasks], [True, False, False])

    def test_select_source_tasks_filters_done_and_specific_selectors(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "tasks.md"
            source.write_text(
                "- [x] 1. Finished task\n"
                "- [ ] 2. Runnable task\n"
                "- [ ] 3. Other task\n",
                encoding="utf-8",
            )
            selection = enqueue_tasks.resolve_source_selection(
                Path(tmp),
                source_paths=[source],
                task_selectors=["2"],
            )

            selected = enqueue_tasks.select_source_tasks(selection)

            self.assertEqual([task.label for task in selected], ["2. Runnable task"])

    def test_duplicate_prevention_skips_already_queued_source_task(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "spec" / "tasks.md"
            source.parent.mkdir(parents=True)
            source.write_text("- [ ] 1. Runnable task\n- [ ] 2. Other task\n", encoding="utf-8")
            queue_path = root / ".codex" / "local-task-queue.md"
            queue_path.parent.mkdir(parents=True)
            queue_path.write_text(
                "# Local Task Queue\n\n## Queued Items\n\n"
                "### Q-001\n"
                "- Status: `queued`\n"
                "- Source: [tasks.md](spec/tasks.md)\n"
                "- Task: `1. Runnable task`\n",
                encoding="utf-8",
            )
            tasks = enqueue_tasks.parse_source_tasks(source)

            check = enqueue_tasks.filter_duplicate_source_tasks(tasks, queue_path, root)

            self.assertEqual([task.label for task in check.duplicate_tasks], ["1. Runnable task"])
            self.assertEqual([task.label for task in check.new_tasks], ["2. Other task"])

    def test_enqueue_selection_appends_source_and_inline_records(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            state = enqueue_tasks.discover_queue_state(root)
            source = root / "spec" / "tasks.md"
            source.parent.mkdir(parents=True)
            source.write_text("- [ ] 1. Runnable task\n", encoding="utf-8")
            selection = enqueue_tasks.resolve_source_selection(
                root,
                source_paths=[source],
                inline_tasks=["context-only task"],
            )

            result = enqueue_tasks.enqueue_selection(state, selection)
            queue_text = state.queue_path.read_text(encoding="utf-8")

            self.assertEqual(result.added_qids, ("Q-001", "Q-002"))
            self.assertIn("- Source: [tasks.md](/", queue_text)
            self.assertIn("- Task: `1. Runnable task`", queue_text)
            self.assertIn("- Source: `inline procedural queue task`", queue_text)
            self.assertIn("- Task: `context-only task`", queue_text)

    def test_main_prints_queue_status_and_manual_added_note(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "tasks.md"
            source.write_text("- [ ] 1. Runnable task\n", encoding="utf-8")
            output = io.StringIO()

            with redirect_stdout(output):
                exit_code = enqueue_tasks.main([
                    "--workspace-root",
                    str(root),
                    "--task-source",
                    str(source),
                ])

            rendered = output.getvalue()
            self.assertEqual(exit_code, 0)
            self.assertIn("# Queue Status", rendered)
            self.assertIn("Undone records:", rendered)
            self.assertIn("Added 1 undone tasks in this enqueue session.", rendered)

    def test_enqueue_selection_supports_multiple_specs_in_source_order(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            first = root / "spec-a" / "tasks.md"
            second = root / "spec-b" / "tasks.md"
            first.parent.mkdir(parents=True)
            second.parent.mkdir(parents=True)
            first.write_text("- [ ] 1. First task\n", encoding="utf-8")
            second.write_text("- [ ] 1. Second task\n", encoding="utf-8")
            state = enqueue_tasks.discover_queue_state(root)
            selection = enqueue_tasks.resolve_source_selection(root, source_paths=[first, second])

            result = enqueue_tasks.enqueue_selection(state, selection)
            queue_text = state.queue_path.read_text(encoding="utf-8")

            self.assertEqual(result.added_qids, ("Q-001", "Q-002"))
            self.assertLess(queue_text.index("First task"), queue_text.index("Second task"))

    def test_backlog_tasks_are_enqueued_like_spec_tasks(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            backlog = root / "backlog" / "tasks.md"
            backlog.parent.mkdir(parents=True)
            backlog.write_text("- [ ] Add backlog-driven feature\n", encoding="utf-8")
            state = enqueue_tasks.discover_queue_state(root)
            selection = enqueue_tasks.resolve_source_selection(root, source_paths=[backlog])

            result = enqueue_tasks.enqueue_selection(state, selection)

            self.assertEqual(result.added_count, 1)
            self.assertIn("Add backlog-driven feature", state.queue_path.read_text(encoding="utf-8"))

    def test_checked_source_tasks_are_skipped_by_default(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "tasks.md"
            source.write_text("- [x] 1. Finished task\n- [ ] 2. Runnable task\n", encoding="utf-8")
            selection = enqueue_tasks.resolve_source_selection(root, source_paths=[source])

            selected = enqueue_tasks.select_source_tasks(selection)

            self.assertEqual([task.label for task in selected], ["2. Runnable task"])


if __name__ == "__main__":
    unittest.main()
