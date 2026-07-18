import importlib.util
import re
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "claudify.py"

spec = importlib.util.spec_from_file_location("claudify", SCRIPT)
claudify = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules["claudify"] = claudify
spec.loader.exec_module(claudify)


BUCKETS = ("skills-workspace", "skills-user")


def source_files():
    for bucket in BUCKETS:
        bucket_dir = ROOT / bucket
        for path in sorted(bucket_dir.rglob("*")):
            if path.is_file():
                yield bucket, path


class ClaudifyTransformUnitTests(unittest.TestCase):
    def setUp(self):
        self.names = claudify.known_skill_names(ROOT)

    def test_only_known_skills_are_converted(self):
        text = "Run `$queue-status` then `$enqueue`; keep $env:FOO, $true, $1 and $notarealskill."
        out = claudify.transform_text(text, self.names)
        self.assertIn("/queue-status", out)
        self.assertIn("/enqueue", out)
        self.assertIn("$env:FOO", out)
        self.assertIn("$true", out)
        self.assertIn("$1", out)
        self.assertIn("$notarealskill", out)

    def test_paths_are_not_treated_as_invocations(self):
        text = "See skills-user/queue-status/SKILL.md and /queue-status invocation."
        out = claudify.transform_text(text, self.names)
        # Path segment is untouched; only the standalone invocation form is n/a here
        self.assertIn("skills-user/queue-status/SKILL.md", out)

    def test_reverse_is_inverse_of_forward(self):
        text = "Use `$tactic` and `$implement`; path a/tactic stays; $env:X stays."
        forward = claudify.transform_text(text, self.names)
        self.assertEqual(claudify.reverse_text(forward, self.names), text)

    def test_partition_splits_candidates_and_only_inventoried_transform(self):
        text = "Run `$queue-status`; ignore $env, $true, $notaskill."
        inventoried, uninventoried = claudify.partition_candidates(text, self.names)
        self.assertIn("queue-status", inventoried)
        self.assertEqual(set(uninventoried), {"env", "true", "notaskill"})
        # The transform acts on exactly the inventoried group.
        out = claudify.transform_text(text, self.names)
        self.assertIn("/queue-status", out)
        for discarded in ("$env", "$true", "$notaskill"):
            self.assertIn(discarded, out)

    def test_partition_of_real_sources_is_consistent(self):
        for _bucket, src in source_files():
            if src.suffix.lower() not in claudify.TRANSFORM_SUFFIXES:
                continue
            text = src.read_text(encoding="utf-8")
            inventoried, uninventoried = claudify.partition_candidates(text, self.names)
            self.assertTrue(set(inventoried) <= self.names)
            self.assertEqual(set(uninventoried) & self.names, set())


class ClaudifyGenerationTests(unittest.TestCase):
    def setUp(self):
        self.names = claudify.known_skill_names(ROOT)
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.out = Path(self.tmp.name) / "out"
        claudify.generate(ROOT, self.out)

    def test_no_over_reach_reverse_reproduces_source(self):
        """The only changes are known-skill invocations: reversing output == source."""
        for bucket, src in source_files():
            rel = src.relative_to(ROOT / bucket)
            gen = self.out / bucket / rel
            self.assertTrue(gen.exists(), f"missing generated file: {gen}")
            if src.suffix.lower() in claudify.TRANSFORM_SUFFIXES:
                source_text = src.read_text(encoding="utf-8")
                gen_text = gen.read_text(encoding="utf-8")
                self.assertEqual(
                    claudify.reverse_text(gen_text, self.names),
                    source_text,
                    f"over-reach detected in {rel}",
                )
            else:
                self.assertEqual(gen.read_bytes(), src.read_bytes(), f"verbatim copy changed: {rel}")

    def test_known_invocation_actually_converted(self):
        gen = self.out / "skills-user" / "enqueue" / "SKILL.md"
        self.assertTrue(gen.exists())
        text = gen.read_text(encoding="utf-8")
        self.assertIn("/queue-status", text)
        self.assertNotIn("$queue-status", text)

    def test_every_skill_has_generated_output(self):
        for bucket in BUCKETS:
            for skill in sorted((ROOT / bucket).iterdir()):
                if skill.is_dir():
                    gen = self.out / bucket / skill.name
                    self.assertTrue(gen.is_dir(), f"no generated output for {bucket}/{skill.name}")


class ClaudifySourceGuardrailTests(unittest.TestCase):
    def test_sources_never_use_slash_invocations(self):
        names = claudify.known_skill_names(ROOT)
        alt = "|".join(re.escape(n) for n in sorted(names, key=len, reverse=True))
        # A Claude-style /name invocation would be preceded by start-of-line,
        # whitespace, or a backtick. Path segments (preceded by a path char) are
        # excluded, so markdown links and file paths do not false-positive.
        guard = re.compile(r"(?:^|[\s`])/(?:" + alt + r")(?![A-Za-z0-9-])", re.MULTILINE)
        offenders = []
        for bucket, src in source_files():
            if src.suffix.lower() not in claudify.TRANSFORM_SUFFIXES:
                continue
            text = src.read_text(encoding="utf-8")
            if guard.search(text):
                offenders.append(str(src.relative_to(ROOT)))
        self.assertEqual(offenders, [], f"tracked sources use /name invocations: {offenders}")


if __name__ == "__main__":
    unittest.main()
