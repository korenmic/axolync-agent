#!/usr/bin/env python3
"""Resolve whether the local workspace may use primary Axolync dispatch routing."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


PRIMARY_IDENTITIES = {"sinq", "sinq1"}


def normalize_extended_windows_path(value: str) -> str:
    if value.startswith("\\\\?\\"):
        return value[4:]
    return value


def normalize_identity(value: str | None) -> str | None:
    if value is None:
        return None
    stripped = value.strip()
    if not stripped:
        return None
    return re.sub(r"[^a-z0-9]+", "", stripped.lower())


def identity_from_workspace(workspace: str | None) -> str | None:
    if workspace is None:
        return None
    stripped = normalize_extended_windows_path(workspace.strip())
    if not stripped:
        return None
    name = Path(stripped).name
    return normalize_identity(name)


def resolve_dispatch_authority(workspace: str | None, identity: str | None = None) -> dict[str, Any]:
    normalized_identity = normalize_identity(identity)
    workspace_identity = identity_from_workspace(workspace)
    identity_conflict = (
        normalized_identity is not None
        and workspace_identity is not None
        and normalized_identity != workspace_identity
        and not (
            normalized_identity in PRIMARY_IDENTITIES
            and workspace_identity in PRIMARY_IDENTITIES
        )
    )
    effective_identity = normalized_identity or workspace_identity
    primary = not identity_conflict and effective_identity in PRIMARY_IDENTITIES
    if identity_conflict:
        reason = "identity-workspace-mismatch"
    elif primary:
        reason = "primary-identity"
    else:
        reason = "non-primary-or-unknown-identity"
    return {
        "workspace": workspace,
        "inputIdentity": identity,
        "workspaceIdentity": workspace_identity,
        "effectiveIdentity": effective_identity,
        "identityConflict": identity_conflict,
        "primary": primary,
        "mode": "route" if primary else "pass-through",
        "reason": reason,
        "primaryIdentities": sorted(PRIMARY_IDENTITIES),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", default=None, help="Target/current workspace path.")
    parser.add_argument("--identity", default=None, help="Target/current agent identity or alias.")
    args = parser.parse_args()
    print(json.dumps(resolve_dispatch_authority(args.workspace, args.identity), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
