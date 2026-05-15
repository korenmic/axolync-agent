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


if __name__ == "__main__":
    unittest.main()

