import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_PATH = ROOT / "skills-workspace" / "axolync-add-consumed-repo" / "SKILL.md"


class AddConsumedRepoDescriptorStandardTests(unittest.TestCase):
    def test_skill_requires_descriptor_owned_exports_for_new_repos(self):
        text = SKILL_PATH.read_text(encoding="utf-8")

        for required in [
            "axolync.repo.toml",
            "[exports.tests]",
            "[exports.packaging]",
            "[[exports.generated_outputs]]",
            "[[exports.inventories]]",
            "[exports.docs]",
            "[[consumes.repos]]",
        ]:
            with self.subTest(required=required):
                self.assertIn(required, text)

    def test_skill_forbids_new_legacy_builder_fallback_fields(self):
        text = SKILL_PATH.read_text(encoding="utf-8")

        self.assertIn("Do not add new repo-owned fallback authority to builder `config/repos.json`", text)
        for forbidden in [
            "buildCommands",
            "sanityCommands",
            "testCommands",
            "addonPackage",
            "themePackage",
            "addonPackPackage",
            "adapterCatalogManifestPath",
            "adapterCatalogManifestProfileId",
        ]:
            with self.subTest(forbidden=forbidden):
                self.assertIn(forbidden, text)

    def test_skill_requires_warning_proof_and_missing_checkout_distinction(self):
        text = SKILL_PATH.read_text(encoding="utf-8")

        self.assertIn("descriptor fallback warning regression", text)
        self.assertIn("managed-checkout/environment debt", text)
        self.assertIn("descriptor checkout is available", text)


if __name__ == "__main__":
    unittest.main()
