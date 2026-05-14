import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AUTHORITY_HELPER = "scripts\\resolve_dispatch_authority.py"
CHECKOUT_STATE_HELPER = "scripts\\dispatch_checkout_state.py"


class DispatchAuthorityGuardTests(unittest.TestCase):
    def test_primary_handoff_skills_reference_authority_helper(self):
        skill_paths = [
            ROOT / "skills-workspace" / "incoming-dispatch-router" / "SKILL.md",
            ROOT / "skills-workspace" / "axolync-build-mirror-handoff" / "SKILL.md",
            ROOT / "skills-workspace" / "axolync-crpr-handoff" / "SKILL.md",
        ]

        for skill_path in skill_paths:
            with self.subTest(skill=str(skill_path.relative_to(ROOT))):
                text = skill_path.read_text(encoding="utf-8")
                self.assertIn(AUTHORITY_HELPER, text)
                self.assertIn('mode: "route"', text)
                self.assertIn("pass-through", text)

    def test_primary_handoff_skills_reference_delayed_checkout_state_helper(self):
        skill_paths = [
            ROOT / "skills-workspace" / "incoming-dispatch-router" / "SKILL.md",
            ROOT / "skills-workspace" / "axolync-build-mirror-handoff" / "SKILL.md",
            ROOT / "skills-workspace" / "axolync-crpr-handoff" / "SKILL.md",
        ]

        for skill_path in skill_paths:
            with self.subTest(skill=str(skill_path.relative_to(ROOT))):
                text = skill_path.read_text(encoding="utf-8")
                self.assertIn(CHECKOUT_STATE_HELPER, text)
                self.assertIn("restore-stale", text)
                self.assertIn("group-key", text)


if __name__ == "__main__":
    unittest.main()
