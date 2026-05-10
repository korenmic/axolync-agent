import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class SkillFrontmatterTests(unittest.TestCase):
    def test_all_skill_frontmatter_is_loader_safe(self):
        skill_files = sorted(ROOT.glob("skills-*/*/SKILL.md"))
        self.assertGreater(len(skill_files), 0, "expected at least one workspace/user skill")

        for skill_file in skill_files:
            with self.subTest(skill=str(skill_file.relative_to(ROOT))):
                text = skill_file.read_text(encoding="utf-8")
                self.assertTrue(text.startswith("---\n"), "SKILL.md must start with YAML frontmatter")
                end = text.find("\n---", 4)
                self.assertGreater(end, 0, "SKILL.md must close YAML frontmatter")
                frontmatter = text[4:end].splitlines()
                parsed = {}

                for line in frontmatter:
                    self.assertNotRegex(line, r"\t", "frontmatter must not use tabs")
                    match = re.fullmatch(r"([A-Za-z][A-Za-z0-9_-]*):(?: (.*))?", line)
                    self.assertIsNotNone(match, f"invalid frontmatter line: {line!r}")
                    key, value = match.groups()
                    value = value or ""
                    if value and not (value.startswith('"') or value.startswith("'")):
                        self.assertNotIn(
                            ": ",
                            value,
                            "plain YAML scalar values must not contain ': '; quote the value",
                        )
                    parsed[key] = value

                self.assertIn("name", parsed)
                self.assertIn("description", parsed)
                self.assertRegex(parsed["name"], r"^[a-z0-9][a-z0-9-]*$")
                self.assertNotEqual(parsed["description"].strip(), "")


if __name__ == "__main__":
    unittest.main()
