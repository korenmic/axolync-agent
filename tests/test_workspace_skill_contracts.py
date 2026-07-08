import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read_skill(name: str) -> str:
    return (ROOT / "skills-workspace" / name / "SKILL.md").read_text(encoding="utf-8")


class WorkspaceSkillContractTests(unittest.TestCase):
    def test_temp_headless_smoke_documents_required_guards(self):
        text = read_skill("temp-headless-smoke")

        required_phrases = [
            "$temp-headless-smoke",
            "Infer and design the relevant temporary headless checks yourself",
            "Do not require the user to provide exact scripts",
            "non-default port",
            "terminate it before finishing the turn",
            "throwaway headless scripts, screenshots, logs, and scratch data untracked",
            "the temporary port used",
            "each temporary headless test performed",
            "you may fix that bug in scope and rerun the relevant temporary test",
            "Temporary smoke tests are evidence, not a replacement",
        ]

        for phrase in required_phrases:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
