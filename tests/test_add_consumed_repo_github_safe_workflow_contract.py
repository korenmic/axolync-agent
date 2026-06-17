from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills-workspace" / "axolync-add-consumed-repo" / "SKILL.md"


class AddConsumedRepoGithubSafeWorkflowContractTests(unittest.TestCase):
    def test_skill_documents_github_safe_workflow_contract(self):
        text = SKILL.read_text(encoding="utf-8")

        self.assertIn("workflow_dispatch", text)
        self.assertIn("push", text)
        self.assertIn("pull_request", text)
        self.assertIn("GitHub-safe", text)
        self.assertIn("exact repo HEAD SHA", text)
        self.assertIn("Do not create one repo workflow that clones and tests every other Axolync sibling repo", text)


if __name__ == "__main__":
    unittest.main()
