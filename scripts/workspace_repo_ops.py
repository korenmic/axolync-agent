#!/usr/bin/env python3
"""Operate on Axolync workspace repos declared by builder config.

The script intentionally avoids scanning arbitrary sibling folders. Its repo set
comes from axolync-builder/config/repos.json plus axolync-builder itself.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class RepoRef:
    repo_id: str
    path: Path
    source: str


def find_workspace_root(start: Path) -> Path:
    current = start.resolve()
    candidates = [current, *current.parents]
    for candidate in candidates:
        if (candidate / "axolync-builder" / "config" / "repos.json").exists():
            return candidate
    script_root = Path(__file__).resolve().parents[2]
    if (script_root.parent / "axolync-builder" / "config" / "repos.json").exists():
        return script_root.parent
    raise SystemExit(
        "Unable to locate workspace root containing axolync-builder/config/repos.json. "
        "Pass --workspace-root explicitly."
    )


def read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def is_git_checkout(path: Path) -> bool:
    return (path / ".git").exists()


def discover_repos(workspace_root: Path, *, include_missing: bool = False) -> tuple[list[RepoRef], list[dict[str, str]]]:
    workspace_root = workspace_root.resolve()
    builder_root = workspace_root / "axolync-builder"
    repos_config_path = builder_root / "config" / "repos.json"
    if not repos_config_path.exists():
        raise SystemExit(f"Missing builder repo config: {repos_config_path}")

    repos: list[RepoRef] = []
    notices: list[dict[str, str]] = []

    def maybe_add(repo_id: str, path: Path, source: str) -> None:
        resolved = path.resolve()
        if not is_git_checkout(resolved):
            notices.append({
                "repoId": repo_id,
                "path": str(resolved),
                "reason": "missing-git-checkout",
            })
            if not include_missing:
                return
        if resolved.name != repo_id:
            notices.append({
                "repoId": repo_id,
                "path": str(resolved),
                "reason": "path-basename-does-not-match-repo-id-but-builder-declared",
            })
        repos.append(RepoRef(repo_id=repo_id, path=resolved, source=source))

    maybe_add("axolync-builder", builder_root, "builder-self")
    config = read_json(repos_config_path)
    for row in config.get("repos", []):
        repo_id = str(row.get("id") or "").strip()
        local_path = str(row.get("localPath") or "").strip()
        if not repo_id or not local_path:
            continue
        maybe_add(repo_id, builder_root / local_path, "builder-consumed-repo")

    deduped: list[RepoRef] = []
    seen: set[str] = set()
    for repo in repos:
        key = str(repo.path).casefold()
        if key in seen:
            continue
        seen.add(key)
        deduped.append(repo)
    return deduped, notices


def run_git(repo: RepoRef, args: list[str], *, dry_run: bool = False) -> tuple[int, str]:
    command = ["git", "-C", str(repo.path), *args]
    if dry_run:
        return 0, "DRY-RUN " + " ".join(command)
    completed = subprocess.run(command, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return completed.returncode, completed.stdout.strip()


def git_output(repo: RepoRef, args: list[str]) -> str:
    completed = subprocess.run(
        ["git", "-C", str(repo.path), *args],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
    )
    return completed.stdout.strip() if completed.returncode == 0 else ""


def inspect_repo(repo: RepoRef) -> dict[str, Any]:
    branch = git_output(repo, ["rev-parse", "--abbrev-ref", "HEAD"]) or "unknown"
    status = git_output(repo, ["status", "--porcelain=1", "--untracked-files=all"])
    upstream = git_output(repo, ["rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"])
    return {
        "repoId": repo.repo_id,
        "path": str(repo.path),
        "source": repo.source,
        "branch": branch,
        "upstream": upstream,
        "dirty": bool(status),
        "status": status.splitlines() if status else [],
    }


def print_text(rows: list[dict[str, Any]], notices: list[dict[str, str]]) -> None:
    for row in rows:
        dirty = "dirty" if row.get("dirty") else "clean"
        upstream = row.get("upstream") or "no-upstream"
        print(f"{row['repoId']}: {row['branch']} ({dirty}, {upstream}) {row['path']}")
        for status_line in row.get("status") or []:
            print(f"  {status_line}")
    for row in notices:
        print(f"NOTICE {row['repoId']}: {row['reason']} {row['path']}")


def execute_action(repos: list[RepoRef], action: str, *, dry_run: bool = False, continue_on_error: bool = False) -> int:
    exit_code = 0
    for repo in repos:
        state = inspect_repo(repo)
        if state["dirty"]:
            print(f"BLOCK {repo.repo_id}: dirty working tree at {repo.path}")
            for line in state["status"]:
                print(f"  {line}")
            exit_code = 2
            if not continue_on_error:
                return exit_code
            continue

        commands: list[list[str]]
        if action == "pull":
            commands = [["fetch", "--prune", "origin"]]
            if state["upstream"]:
                commands.append(["pull", "--rebase"])
            elif state["branch"] == "master":
                commands.append(["pull", "--rebase", "origin", "master"])
            else:
                print(f"SKIP {repo.repo_id}: branch {state['branch']} has no upstream; fetched only")
        elif action == "masterify":
            commands = [
                ["fetch", "--prune", "origin"],
                ["checkout", "master"],
                ["pull", "--rebase", "origin", "master"],
            ]
        else:
            raise AssertionError(f"unsupported action: {action}")

        for command in commands:
            code, output = run_git(repo, command, dry_run=dry_run)
            label = " ".join(["git", "-C", str(repo.path), *command])
            print(f"{repo.repo_id}> {label}")
            if output:
                print(output)
            if code != 0:
                print(f"FAIL {repo.repo_id}: command exited {code}")
                exit_code = code or 1
                if not continue_on_error:
                    return exit_code
                break
    return exit_code


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["list", "status", "pull", "masterify"])
    parser.add_argument("--workspace-root", default="", help="Workspace root containing axolync-builder.")
    parser.add_argument("--json", action="store_true", help="Emit JSON for list/status actions.")
    parser.add_argument("--include-missing", action="store_true", help="Include missing repos in discovery output.")
    parser.add_argument("--dry-run", action="store_true", help="Print git commands without executing them.")
    parser.add_argument("--continue-on-error", action="store_true", help="Continue after a repo-level failure.")
    args = parser.parse_args(argv)

    if args.workspace_root:
        requested_root = Path(args.workspace_root).resolve()
        workspace_root = requested_root if (requested_root / "axolync-builder" / "config" / "repos.json").exists() else find_workspace_root(requested_root)
    else:
        workspace_root = find_workspace_root(Path.cwd())
    repos, notices = discover_repos(workspace_root, include_missing=args.include_missing)
    rows = [inspect_repo(repo) for repo in repos]

    if args.action in {"list", "status"}:
        if args.json:
            print(json.dumps({"workspaceRoot": str(workspace_root), "repos": rows, "notices": notices}, indent=2))
        else:
            print_text(rows, notices)
        return 0

    return execute_action(repos, args.action, dry_run=args.dry_run, continue_on_error=args.continue_on_error)


if __name__ == "__main__":
    raise SystemExit(main())
