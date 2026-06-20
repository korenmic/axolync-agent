from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills-workspace" / "axolync-build-mirror-handoff" / "SKILL.md"


class BuildMirrorHandoffCiModeTests(unittest.TestCase):
    def test_handoff_distinguishes_maximal_full_ci_from_core_only(self):
        text = SKILL.read_text(encoding="utf-8")

        self.assertIn("`full-ci`: run Builder's maximal descriptor-aware validation flow", text)
        self.assertIn("`full-ci-core`: run Builder's reduced/core-only validation flow", text)
        self.assertIn("only when the dispatch explicitly asks for reduced/core validation", text)
        self.assertIn("do not satisfy it with report-only, no-ci, dry-run, sanity", text)


if __name__ == "__main__":
    unittest.main()
