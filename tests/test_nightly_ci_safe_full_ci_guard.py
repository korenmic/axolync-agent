import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_PATH = ROOT / "skills-workspace" / "nightly-ci-safe" / "SKILL.md"


class NightlyCiSafeFullCiGuardTests(unittest.TestCase):
    def test_skill_requires_builder_full_ci_and_inventory_proof(self):
        text = SKILL_PATH.read_text(encoding="utf-8")

        self.assertIn("npm run full-ci", text)
        self.assertIn("npm run full-ci:inventory", text)
        self.assertIn("FULL CI PROOF NOT VALID", text)
        self.assertIn("workflow=local-full", text)
        self.assertIn("source=local-authoritative", text)

    def test_skill_forbids_reduced_mode_substitution(self):
        text = SKILL_PATH.read_text(encoding="utf-8")

        for forbidden in [
            "report:generate",
            "report:noci",
            "report:generate:dry",
            "sanity",
            "dry-run",
            "inventory-only",
            "mostly `not_run`",
        ]:
            with self.subTest(forbidden=forbidden):
                self.assertIn(forbidden, text)


if __name__ == "__main__":
    unittest.main()
