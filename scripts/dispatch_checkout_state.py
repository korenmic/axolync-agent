#!/usr/bin/env python3
"""Record and restore dispatch-owned temporary checkout state.

The helper is intentionally conservative: it never restores over a dirty worktree,
and it only treats a prior dispatch as stale when the caller supplies a different
group key for the next request.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def run_git(repo_path: Path, args: list[str], *, check: bool = False) -> tuple[int, str]:
    completed = subprocess.run(
        ["git", "-C", str(repo_path), *args],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    output = completed.stdout.strip()
    if check and completed.returncode != 0:
        raise SystemExit(output or f"git {' '.join(args)} failed with {completed.returncode}")
    return completed.returncode, output


def git_output(repo_path: Path, args: list[str]) -> str:
    code, output = run_git(repo_path, args)
    return output if code == 0 else ""


def state_path(workspace_root: Path) -> Path:
    return workspace_root.resolve() / ".codex" / "dispatch-checkout-state.json"


def read_state(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def write_state(path: Path, state: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def normalize_group_key(value: str) -> str:
    return " ".join(value.strip().split())


def inspect_repo(repo_path: Path) -> dict[str, Any]:
    resolved = repo_path.resolve()
    status = git_output(resolved, ["status", "--porcelain=1", "--untracked-files=all"])
    return {
        "path": str(resolved),
        "branch": git_output(resolved, ["rev-parse", "--abbrev-ref", "HEAD"]) or "unknown",
        "commit": git_output(resolved, ["rev-parse", "HEAD"]) or "unknown",
        "dirty": bool(status),
        "status": status.splitlines() if status else [],
    }


def record(args: argparse.Namespace) -> int:
    workspace_root = Path(args.workspace_root).resolve()
    repo_path = Path(args.repo_path).resolve()
    path = state_path(workspace_root)
    repo_state = inspect_repo(repo_path)
    if repo_state["dirty"] and not args.allow_dirty_record:
        print(f"REFUSE record {args.repo_id}: dirty worktree at {repo_path}")
        for line in repo_state["status"]:
            print(f"  {line}")
        return 2

    group_key = normalize_group_key(args.group_key)
    state = read_state(path)
    if state and normalize_group_key(str(state.get("groupKey", ""))) != group_key:
        print("REFUSE record: stale dispatch checkout state exists for a different group")
        print(str(path))
        return 3

    if not state:
        state = {
            "dispatchId": args.dispatch_id,
            "groupKey": group_key,
            "createdAt": datetime.now(timezone.utc).isoformat(),
            "repos": {},
        }

    repos = state.setdefault("repos", {})
    repos.setdefault(args.repo_id, repo_state)
    write_state(path, state)
    print(f"RECORDED {args.repo_id}: {repo_state['branch']} {repo_state['commit']}")
    return 0


def restore_stale(args: argparse.Namespace) -> int:
    workspace_root = Path(args.workspace_root).resolve()
    path = state_path(workspace_root)
    state = read_state(path)
    if not state:
        print("NOOP no dispatch checkout state")
        return 0

    current_group_key = normalize_group_key(args.group_key)
    stored_group_key = normalize_group_key(str(state.get("groupKey", "")))
    if stored_group_key == current_group_key:
        print("NOOP dispatch checkout state belongs to the same group")
        return 0

    exit_code = 0
    for repo_id, recorded in sorted((state.get("repos") or {}).items()):
        repo_path = Path(str(recorded.get("path", ""))).resolve()
        current = inspect_repo(repo_path)
        if current["dirty"]:
            print(f"REFUSE restore {repo_id}: dirty worktree at {repo_path}")
            for line in current["status"]:
                print(f"  {line}")
            exit_code = 2
            continue
        target_branch = str(recorded.get("branch") or "")
        target_commit = str(recorded.get("commit") or "")
        target = target_branch if target_branch and target_branch != "HEAD" else target_commit
        if not target:
            print(f"REFUSE restore {repo_id}: missing recorded target")
            exit_code = 2
            continue
        code, output = run_git(repo_path, ["checkout", target])
        print(f"RESTORE {repo_id}: {target}")
        if output:
            print(output)
        if code != 0:
            exit_code = code or 1

    if exit_code == 0:
        path.unlink(missing_ok=True)
        print("CLEARED dispatch checkout state")
    else:
        print(f"KEPT dispatch checkout state: {path}")
    return exit_code


def show(args: argparse.Namespace) -> int:
    path = state_path(Path(args.workspace_root))
    state = read_state(path)
    print(json.dumps(state or {}, indent=2, sort_keys=True))
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    def add_common(subparser: argparse.ArgumentParser) -> None:
        subparser.add_argument("--workspace-root", required=True)

    record_parser = subparsers.add_parser("record")
    add_common(record_parser)
    record_parser.add_argument("--dispatch-id", required=True)
    record_parser.add_argument("--group-key", required=True)
    record_parser.add_argument("--repo-id", required=True)
    record_parser.add_argument("--repo-path", required=True)
    record_parser.add_argument("--allow-dirty-record", action="store_true")
    record_parser.set_defaults(func=record)

    restore_parser = subparsers.add_parser("restore-stale")
    add_common(restore_parser)
    restore_parser.add_argument("--group-key", required=True)
    restore_parser.set_defaults(func=restore_stale)

    show_parser = subparsers.add_parser("show")
    add_common(show_parser)
    show_parser.set_defaults(func=show)

    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
