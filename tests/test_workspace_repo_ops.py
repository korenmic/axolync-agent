import json
import tempfile
import unittest
from pathlib import Path

from scripts.workspace_repo_ops import discover_repos, find_workspace_root


def make_git_dir(path: Path) -> None:
    (path / ".git").mkdir(parents=True)


class WorkspaceRepoOpsTests(unittest.TestCase):
    def test_discovers_only_builder_declared_repos_with_matching_names(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            builder = root / "axolync-builder"
            (builder / "config").mkdir(parents=True)
            make_git_dir(builder)
            make_git_dir(root / "axolync-browser")
            make_git_dir(root / "temporary-cr-clone")
            make_git_dir(root / "wrong-folder")
            (builder / "config" / "repos.json").write_text(
                json.dumps({
                    "repos": [
                        {"id": "axolync-browser", "localPath": "../axolync-browser"},
                        {"id": "axolync-vibra", "localPath": "../wrong-folder"},
                        {"id": "axolync-missing", "localPath": "../axolync-missing"},
                    ]
                }),
                encoding="utf-8",
            )

            repos, notices = discover_repos(root)

            self.assertEqual([repo.repo_id for repo in repos], ["axolync-builder", "axolync-browser", "axolync-vibra"])
            self.assertNotIn("temporary-cr-clone", [repo.path.name for repo in repos])
            self.assertEqual(
                [(row["repoId"], row["reason"]) for row in notices],
                [
                    ("axolync-vibra", "path-basename-does-not-match-repo-id-but-builder-declared"),
                    ("axolync-missing", "missing-git-checkout"),
                ],
            )

    def test_finds_workspace_root_from_child_repo(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            builder = root / "axolync-builder"
            browser = root / "axolync-browser"
            (builder / "config").mkdir(parents=True)
            browser.mkdir()
            (builder / "config" / "repos.json").write_text('{"repos":[]}', encoding="utf-8")

            self.assertEqual(find_workspace_root(browser), root.resolve())


if __name__ == "__main__":
    unittest.main()
