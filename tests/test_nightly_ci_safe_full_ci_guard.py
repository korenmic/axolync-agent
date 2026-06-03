import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_PATH = ROOT / "skills-workspace" / "nightly-ci-safe" / "SKILL.md"


class NightlyCiSafeFullCiGuardTests(unittest.TestCase):
    def test_skill_requires_builder_full_ci_and_inventory_proof(self):
        text = SKILL_PATH.read_text(encoding="utf-8")

        self.assertIn("npm run full-ci", text)
        self.assertIn("npm run full-ci -- --dry-run", text)
        self.assertIn("FULL CI PROOF NOT VALID", text)
        self.assertIn("workflow=local-full", text)
        self.assertIn("source=local-authoritative", text)
        self.assertIn("candidate/executed counts cannot be reconciled", text)
        self.assertIn("Browser rows are collapsed", text)

    def test_skill_forbids_reduced_mode_substitution(self):
        text = SKILL_PATH.read_text(encoding="utf-8")

        for forbidden in [
            "report:generate",
            "report:noci",
            "report:generate:dry",
            "sanity",
            "inventory-only",
            "mostly `not_run`",
        ]:
            with self.subTest(forbidden=forbidden):
                self.assertIn(forbidden, text)

    def test_skill_does_not_teach_legacy_builder_full_ci_commands(self):
        text = SKILL_PATH.read_text(encoding="utf-8")

        self.assertNotIn("full-ci:inventory", text)
        self.assertNotIn("full-ci:dry-run", text)


if __name__ == "__main__":
    unittest.main()
