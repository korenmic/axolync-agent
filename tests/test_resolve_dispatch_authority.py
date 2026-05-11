import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "resolve_dispatch_authority.py"


class DispatchAuthorityTests(unittest.TestCase):
    def test_primary_identities_route(self):
        from scripts.resolve_dispatch_authority import resolve_dispatch_authority

        self.assertEqual(
            resolve_dispatch_authority(r"C:\Users\koren\src\Sinq")["mode"],
            "route",
        )
        self.assertEqual(
            resolve_dispatch_authority(r"C:\Users\koren\src\Sinq", "Sinq1")["mode"],
            "route",
        )

    def test_non_primary_identities_pass_through(self):
        from scripts.resolve_dispatch_authority import resolve_dispatch_authority

        self.assertEqual(
            resolve_dispatch_authority(r"C:\Users\koren\src\Sinq2")["mode"],
            "pass-through",
        )
        self.assertEqual(
            resolve_dispatch_authority(r"\\?\C:\Users\koren\src\Sinq4")["effectiveIdentity"],
            "sinq4",
        )
        self.assertFalse(resolve_dispatch_authority(None)["primary"])

    def test_identity_workspace_conflict_passes_through(self):
        from scripts.resolve_dispatch_authority import resolve_dispatch_authority

        result = resolve_dispatch_authority(r"C:\Users\koren\src\Sinq4", "Sinq1")
        self.assertEqual(result["mode"], "pass-through")
        self.assertEqual(result["reason"], "identity-workspace-mismatch")
        self.assertTrue(result["identityConflict"])

    def test_cli_emits_json(self):
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--workspace",
                r"\\?\C:\Users\koren\src\Sinq",
            ],
            cwd=ROOT,
            text=True,
            check=True,
            capture_output=True,
        )
        parsed = json.loads(result.stdout)
        self.assertTrue(parsed["primary"])
        self.assertEqual(parsed["mode"], "route")


if __name__ == "__main__":
    unittest.main()
