import importlib.util
import os
import sys
import tempfile
import time
import unittest
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills-workspace" / "latest-debug-log" / "scripts" / "latest_debug_log.py"

spec = importlib.util.spec_from_file_location("latest_debug_log", SCRIPT)
latest_debug_log = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules["latest_debug_log"] = latest_debug_log
spec.loader.exec_module(latest_debug_log)


class LatestDebugLogTests(unittest.TestCase):
    def test_selects_newest_axolync_debug_zip_by_mtime(self):
        with tempfile.TemporaryDirectory() as tmp:
            downloads = Path(tmp)
            old_zip = downloads / "axolync-debug-old.zip"
            new_zip = downloads / "axolync-debug-new.zip"
            other_zip = downloads / "other-debug-newer.zip"

            for path in [old_zip, new_zip, other_zip]:
                with zipfile.ZipFile(path, "w") as archive:
                    archive.writestr("debug.txt", path.name)

            now = time.time()
            old_time = now - 20
            new_time = now - 10
            other_time = now
            for path, timestamp in [(old_zip, old_time), (new_zip, new_time), (other_zip, other_time)]:
                path.touch()
                path.chmod(0o644)
                os.utime(path, (timestamp, timestamp))

            self.assertEqual(
                latest_debug_log.latest_debug_zip(downloads),
                new_zip,
            )

    def test_text_output_includes_path_and_entry_preview(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "axolync-debug-sample.zip"
            with zipfile.ZipFile(path, "w") as archive:
                archive.writestr("logs/live-debug.json", "{}")

            payload = latest_debug_log.build_payload(path, entry_limit=5)
            output = latest_debug_log.format_text(payload)

            self.assertIn(str(path.resolve()), output)
            self.assertIn("logs/live-debug.json", output)


if __name__ == "__main__":
    unittest.main()
