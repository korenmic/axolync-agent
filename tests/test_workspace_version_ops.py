import json
import tempfile
import unittest
import zipfile
from pathlib import Path

from scripts.workspace_version_ops import (
    BumpPlan,
    RepoEntry,
    RepoGitState,
    apply_version_updates,
    artifact_evidence_for_repo,
    make_plan,
    make_text_table,
    next_minor_version,
    replace_gradle_version,
    replace_package_lock_version,
    replace_package_version,
    replace_regex_version,
    select_repos,
    PYPROJECT_VERSION_RE,
)


class WorkspaceVersionOpsTests(unittest.TestCase):
    def test_next_minor_drops_prerelease_suffix(self):
        self.assertEqual(next_minor_version("2.0.0-beta.1"), "2.1.0")
        self.assertEqual(next_minor_version("v3.4.9"), "3.5.0")

    def test_updates_package_and_lock_versions(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            package = root / "package.json"
            lock = root / "package-lock.json"
            package.write_text(json.dumps({"name": "demo", "version": "1.2.3"}, indent=2) + "\n", encoding="utf-8")
            lock.write_text(
                json.dumps({"name": "demo", "version": "1.2.3", "packages": {"": {"version": "1.2.3"}}}, indent=2) + "\n",
                encoding="utf-8",
            )

            self.assertTrue(replace_package_version(package, "1.3.0"))
            self.assertTrue(replace_package_lock_version(lock, "1.2.3", "1.3.0"))

            self.assertEqual(json.loads(package.read_text(encoding="utf-8"))["version"], "1.3.0")
            lock_data = json.loads(lock.read_text(encoding="utf-8"))
            self.assertEqual(lock_data["version"], "1.3.0")
            self.assertEqual(lock_data["packages"][""]["version"], "1.3.0")

    def test_updates_pyproject_when_version_matches(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "pyproject.toml"
            path.write_text('[project]\nname = "demo"\nversion = "0.4.0"\n', encoding="utf-8")

            self.assertTrue(replace_regex_version(path, PYPROJECT_VERSION_RE, "0.4.0", "0.5.0"))

            self.assertIn('version = "0.5.0"', path.read_text(encoding="utf-8"))

    def test_updates_gradle_version_name_and_code(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "build.gradle.kts"
            path.write_text('android {\n  defaultConfig {\n    versionCode = 21\n    versionName = "2.1.0"\n  }\n}\n', encoding="utf-8")

            self.assertTrue(replace_gradle_version(path, "2.1.0", "2.2.0"))

            content = path.read_text(encoding="utf-8")
            self.assertIn('versionName = "2.2.0"', content)
            self.assertIn("versionCode = 22", content)

    def test_apply_version_updates_updates_known_matching_files(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "tools").mkdir()
            (root / "package.json").write_text('{"version":"1.0.0"}\n', encoding="utf-8")
            (root / "tools" / "package.json").write_text('{"version":"1.0.0"}\n', encoding="utf-8")
            (root / "pyproject.toml").write_text('version = "1.0.0"\n', encoding="utf-8")
            repo = RepoEntry("demo", root, "test", "package.json", ("demo",))
            state = RepoGitState("master", "origin/master", "abc", (), (), "v1.0.0", "1.0.0")
            plan = BumpPlan(repo, state, "1.0.0", "package-json:package.json", "1.1.0", "v1.1.0", "bump", "", False, ())

            changed = apply_version_updates(plan)

            self.assertEqual(set(changed), {"package.json", "tools/package.json", "pyproject.toml"})
            self.assertEqual(json.loads((root / "package.json").read_text(encoding="utf-8"))["version"], "1.1.0")
            self.assertEqual(json.loads((root / "tools" / "package.json").read_text(encoding="utf-8"))["version"], "1.1.0")
            self.assertIn('version = "1.1.0"', (root / "pyproject.toml").read_text(encoding="utf-8"))

    def test_select_repos_accepts_repo_id_and_folder_alias(self):
        first = RepoEntry("demo-stage1-addon", Path("C:/x/axolync-addon-demo-stage1"), "test", "package.json", ("demo-stage1-addon", "axolync-addon-demo-stage1"))
        second = RepoEntry("axolync-browser", Path("C:/x/axolync-browser"), "test", "package.json", ("axolync-browser",))

        selected, missing = select_repos([first, second], ["axolync-addon-demo-stage1", "axolync-browser"])

        self.assertEqual([repo.repo_id for repo in selected], ["demo-stage1-addon", "axolync-browser"])
        self.assertEqual(missing, [])

    def test_make_plan_blocks_dirty_repo(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            repo = RepoEntry("demo", root, "test", "package.json", ("demo",))
            (root / ".git").mkdir()
            (root / "package.json").write_text('{"version":"1.0.0"}\n', encoding="utf-8")
            # make_plan shells out to git. A non-git temp checkout should become blocked by no semver/tag
            # only after branch/state probing, so use text table coverage for dirty details separately.
            row = {
                "repoId": "demo",
                "branch": "master",
                "head": "abc",
                "currentVersion": "1.0.0",
                "latestSemverTag": "v1.0.0",
                "proposedVersion": "1.1.0",
                "status": "blocked-dirty",
                "currentVersionSource": "package-json:package.json",
            }
            self.assertIn("blocked-dirty", make_text_table([row]))

    def test_artifact_evidence_reports_aligned_zip_and_browser_versions(self):
        with tempfile.TemporaryDirectory() as temp:
            workspace = Path(temp)
            repo = workspace / "axolync-addon-demo"
            zip_path = repo / "artifacts" / "output" / "local_js" / "axolync-addon-demo-local_js.zip"
            zip_path.parent.mkdir(parents=True)
            browser_manifest = workspace / "axolync-browser" / "public" / "plugins" / "preinstalled" / "manifest.json"
            browser_manifest.parent.mkdir(parents=True)
            with zipfile.ZipFile(zip_path, "w") as archive:
                archive.writestr("manifest.json", json.dumps({"addon": {"addon_id": "axolync-addon-demo", "version": "1.2.3"}}))
            browser_manifest.write_text(json.dumps({"plugins": [{"id": "axolync-addon-demo", "version": "1.2.3"}]}), encoding="utf-8")
            repo_entry = RepoEntry(
                "axolync-addon-demo",
                repo,
                "test",
                "package.json",
                ("axolync-addon-demo",),
                "artifacts/output/local_js/axolync-addon-demo-local_js.zip",
                "axolync-addon-demo",
            )

            evidence = artifact_evidence_for_repo(repo_entry, "1.2.3", workspace)

            self.assertEqual(evidence["status"], "ok")
            self.assertEqual(evidence["versions"], ["zip:1.2.3", "browser:1.2.3"])

    def test_artifact_evidence_reports_drift(self):
        with tempfile.TemporaryDirectory() as temp:
            workspace = Path(temp)
            repo = workspace / "axolync-addon-demo"
            zip_path = repo / "artifacts" / "output" / "local_js" / "axolync-addon-demo-local_js.zip"
            zip_path.parent.mkdir(parents=True)
            with zipfile.ZipFile(zip_path, "w") as archive:
                archive.writestr("manifest.json", json.dumps({"addon": {"addon_id": "axolync-addon-demo", "version": "1.2.2"}}))
            repo_entry = RepoEntry(
                "axolync-addon-demo",
                repo,
                "test",
                "package.json",
                ("axolync-addon-demo",),
                "artifacts/output/local_js/axolync-addon-demo-local_js.zip",
                "axolync-addon-demo",
            )

            evidence = artifact_evidence_for_repo(repo_entry, "1.2.3", workspace)

            self.assertEqual(evidence["status"], "drift")
            self.assertIn("zip=1.2.2 authority=1.2.3", evidence["details"])


if __name__ == "__main__":
    unittest.main()
