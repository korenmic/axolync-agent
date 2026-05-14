import subprocess
import tempfile
import unittest
from pathlib import Path

from scripts.dispatch_checkout_state import main as dispatch_checkout_main, state_path


def run(command, cwd):
    completed = subprocess.run(command, cwd=cwd, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if completed.returncode != 0:
        raise AssertionError(completed.stdout)
    return completed.stdout.strip()


def make_repo(path: Path) -> None:
    path.mkdir(parents=True)
    run(["git", "init", "-b", "master"], path)
    run(["git", "config", "user.email", "test@example.invalid"], path)
    run(["git", "config", "user.name", "Test User"], path)
    (path / "README.md").write_text("initial\n", encoding="utf-8")
    run(["git", "add", "README.md"], path)
    run(["git", "commit", "-m", "initial"], path)


class DispatchCheckoutStateTests(unittest.TestCase):
    def test_restores_only_when_next_dispatch_group_is_unrelated(self):
        with tempfile.TemporaryDirectory() as temp:
            workspace = Path(temp)
            repo = workspace / "axolync-browser"
            make_repo(repo)

            self.assertEqual(
                dispatch_checkout_main([
                    "record",
                    "--workspace-root",
                    str(workspace),
                    "--dispatch-id",
                    "dispatch-1",
                    "--group-key",
                    "browser-pr-45",
                    "--repo-id",
                    "axolync-browser",
                    "--repo-path",
                    str(repo),
                ]),
                0,
            )
            run(["git", "checkout", "-b", "review-branch"], repo)

            self.assertEqual(
                dispatch_checkout_main([
                    "restore-stale",
                    "--workspace-root",
                    str(workspace),
                    "--group-key",
                    "browser-pr-45",
                ]),
                0,
            )
            self.assertEqual(run(["git", "rev-parse", "--abbrev-ref", "HEAD"], repo), "review-branch")

            self.assertEqual(
                dispatch_checkout_main([
                    "restore-stale",
                    "--workspace-root",
                    str(workspace),
                    "--group-key",
                    "browser-pr-99",
                ]),
                0,
            )
            self.assertEqual(run(["git", "rev-parse", "--abbrev-ref", "HEAD"], repo), "master")
            self.assertFalse(state_path(workspace).exists())


if __name__ == "__main__":
    unittest.main()
