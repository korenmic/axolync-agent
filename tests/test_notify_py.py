import importlib.util
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

REPO_ROOT = Path(__file__).resolve().parents[1]
NOTIFY_PY = REPO_ROOT / "skills-user" / "notify" / "notify.py"


def load_notify():
    spec = importlib.util.spec_from_file_location("notify_py", NOTIFY_PY)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class NotifyPyTests(unittest.TestCase):
    def setUp(self):
        self.m = load_notify()
        self.sent = []
        self.m.post = lambda url, body: self.sent.append((url, body))

    # --- pure helpers ---

    def test_format_duration(self):
        self.assertEqual(self.m.format_duration("3700"), "1h 1m")
        self.assertEqual(self.m.format_duration("90"), "1m")
        self.assertEqual(self.m.format_duration("5"), "5s")
        self.assertEqual(self.m.format_duration("2m"), "2m")
        self.assertIsNone(self.m.format_duration(""))
        self.assertIsNone(self.m.format_duration(None))

    def test_bot_prefix_guard(self):
        self.assertEqual(self.m.ensure_bot_prefix("hello", "Sinq1"), "Sinq1: hello")
        self.assertEqual(self.m.ensure_bot_prefix("Sinq2: hi", "X"), "Sinq2: hi")

    def test_dotenv_parsing(self):
        with tempfile.TemporaryDirectory() as td:
            env = Path(td) / ".env"
            env.write_text(
                "# comment\nAXOLYNC_NOTIFY_BOT_NAME='Quoted'\nEMPTY=\nPLAIN=v\n",
                encoding="utf-8",
            )
            self.assertEqual(
                self.m.parse_dotenv_value(env, "AXOLYNC_NOTIFY_BOT_NAME"), "Quoted"
            )
            self.assertIsNone(self.m.parse_dotenv_value(env, "EMPTY"))
            self.assertEqual(self.m.parse_dotenv_value(env, "PLAIN"), "v")
            self.assertIsNone(self.m.parse_dotenv_value(env, "MISSING"))

    def test_ancestor_dotenv_nearest_wins_and_skips_undefined(self):
        with tempfile.TemporaryDirectory() as td:
            top, mid = Path(td), Path(td) / "mid"
            leaf = mid / "leaf"
            leaf.mkdir(parents=True)
            (top / ".env").write_text("AXOLYNC_NOTIFY_BOT_NAME=Top\n", encoding="utf-8")
            (mid / ".env").write_text("OTHER=x\n", encoding="utf-8")
            # mid .env lacks the key -> resolution continues to top
            self.assertEqual(
                self.m.ancestor_dotenv_value(leaf, "AXOLYNC_NOTIFY_BOT_NAME"), "Top"
            )

    # --- main() behavior (post stubbed) ---

    def _clean_env(self):
        cleaned = {
            k: v
            for k, v in os.environ.items()
            if not k.startswith("AXOLYNC_")
        }
        return mock.patch.dict(os.environ, cleaned, clear=True)

    def test_empty_message_silent_exit(self):
        self.assertEqual(self.m.main([]), 0)
        self.assertEqual(self.m.main([""]), 0)
        self.assertEqual(self.sent, [])

    def test_missing_channel_silent_exit(self):
        with self._clean_env():
            # Force every fallback empty: stub the resolver chain pieces.
            self.m.legacy_config_value = lambda *a: None
            self.m.template_value = lambda *a: None
            self.m.ancestor_dotenv_value = lambda *a: None
            self.assertEqual(self.m.main(["body"]), 0)
            self.assertEqual(self.sent, [])

    def test_at_name_channel_and_precedence(self):
        with self._clean_env():
            self.m.legacy_config_value = lambda *a: None
            self.m.template_value = lambda *a: None
            self.m.ancestor_dotenv_value = lambda *a: None
            os.environ["AXOLYNC_NOTIFY_CHANNEL"] = "chan-env"
            rc = self.m.main(["body", "@Sinq3", "", "90"])
            self.assertEqual(rc, 0)
            self.assertEqual(len(self.sent), 1)
            url, body = self.sent[0]
            self.assertEqual(url, "https://ntfy.sh/chan-env")
            self.assertEqual(body, "Sinq3: body | 1m")

    def test_explicit_channel_beats_env(self):
        with self._clean_env():
            self.m.legacy_config_value = lambda *a: None
            self.m.template_value = lambda *a: None
            self.m.ancestor_dotenv_value = lambda *a: None
            os.environ["AXOLYNC_NOTIFY_CHANNEL"] = "chan-env"
            os.environ["AXOLYNC_NOTIFY_BOT_NAME"] = "EnvBot"
            self.m.main(["body", "chan-arg"])
            url, body = self.sent[0]
            self.assertEqual(url, "https://ntfy.sh/chan-arg")
            self.assertEqual(body, "EnvBot: body")

    def test_task_number_suffix_for_starting(self):
        with self._clean_env():
            self.m.legacy_config_value = lambda *a: None
            self.m.template_value = lambda *a: None
            self.m.ancestor_dotenv_value = lambda *a: None
            os.environ["AXOLYNC_NOTIFY_CHANNEL"] = "c"
            self.m.main(["starting", "", "7"])
            _, body = self.sent[0]
            self.assertIn("starting [task 7]", body)


if __name__ == "__main__":
    unittest.main()
