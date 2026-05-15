import importlib.util
import sys
import tempfile
import unittest
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


if __name__ == "__main__":
    unittest.main()

