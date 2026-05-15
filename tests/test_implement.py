import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills-user" / "implement" / "scripts" / "implement_tasks.py"

spec = importlib.util.spec_from_file_location("implement_tasks", SCRIPT)
implement_tasks = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules["implement_tasks"] = implement_tasks
spec.loader.exec_module(implement_tasks)


class ImplementTests(unittest.TestCase):
    def test_default_plan_uses_current_workspace_undone_queue(self):
        plan = implement_tasks.resolve_implement_plan([])

        self.assertTrue(plan.uses_default_queue)
        self.assertEqual(plan.task_source, implement_tasks.DEFAULT_QUEUE_TARGET)
        self.assertEqual(plan.tactic_arguments, ())

    def test_extra_arguments_are_forwarded_to_tactic(self):
        plan = implement_tasks.resolve_implement_plan(["autonomous", "--only", "Q-100"])

        self.assertFalse(plan.uses_default_queue)
        self.assertEqual(plan.tactic_arguments, ("autonomous", "--only", "Q-100"))
        self.assertIn("autonomous --only Q-100", implement_tasks.format_tactic_handoff(plan))

    def test_dirty_worktree_warning_is_non_blocking(self):
        warning = implement_tasks.build_worktree_warning(Path("repo"), " M file.txt\n?? new.txt\n")

        self.assertTrue(warning.dirty)
        self.assertIn("Warning: worktree is not clean", warning.message)
        self.assertIn("leaves dirty-state handling to $tactic", warning.message)

    def test_clean_worktree_warning_reports_clean(self):
        warning = implement_tasks.build_worktree_warning(Path("repo"), "")

        self.assertFalse(warning.dirty)
        self.assertIn("Worktree clean", warning.message)

    def test_notify_sequence_includes_tactic_and_push_boundaries(self):
        events = implement_tasks.notify_event_sequence()

        self.assertIn("implementation-start", events)
        self.assertIn("tactic-task-start", events)
        self.assertIn("tactic-task-progress", events)
        self.assertIn("tactic-task-done", events)
        self.assertIn("push-complete", events)
        self.assertGreater(events.index("tactic-finished"), events.index("tactic-task-done"))
        self.assertGreater(events.index("push-complete"), events.index("tactic-finished"))

    def test_push_plan_prefers_explicit_branch(self):
        plan = implement_tasks.resolve_push_plan(
            explicit_branch="feature",
            current_branch="master",
            default_to_master=True,
        )

        self.assertEqual(plan.branch, "feature")
        self.assertEqual(plan.source, "explicit")
        self.assertFalse(plan.requires_clarification)

    def test_push_plan_blocks_unsafe_inference(self):
        plan = implement_tasks.resolve_push_plan()

        self.assertIsNone(plan.branch)
        self.assertTrue(plan.requires_clarification)
        self.assertIn("Push blocked", implement_tasks.format_push_plan(plan))

    def test_no_undone_task_message_blocks_push_attempt(self):
        message = implement_tasks.format_no_undone_tasks_message(0)

        self.assertIn("nothing to implement", message)
        self.assertIn("no push", message)

    def test_can_push_requires_completion_commit_and_no_blockers(self):
        self.assertTrue(implement_tasks.can_push_after_tactic(True, True, []))
        self.assertFalse(implement_tasks.can_push_after_tactic(False, True, []))
        self.assertFalse(implement_tasks.can_push_after_tactic(True, False, []))
        self.assertFalse(implement_tasks.can_push_after_tactic(True, True, ["blocked task"]))

    def test_push_failure_report_keeps_exact_blocker_visible(self):
        message = implement_tasks.format_push_failure("git push origin master", "non-fast-forward")

        self.assertIn("git push origin master", message)
        self.assertIn("non-fast-forward", message)


if __name__ == "__main__":
    unittest.main()
