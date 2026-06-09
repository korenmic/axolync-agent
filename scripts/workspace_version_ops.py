#!/usr/bin/env python3
"""Inventory and bump Axolync workspace repo versions/tags.

Repo discovery is intentionally limited to axolync-builder/config/repos.json
plus axolync-builder itself. This mirrors the workspace repo ops skills and
avoids accidental edits to ad hoc sibling clones.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

try:
    from workspace_repo_ops import find_workspace_root, read_json
except ModuleNotFoundError:  # pragma: no cover - exercised by package imports.
    from scripts.workspace_repo_ops import find_workspace_root, read_json


SEMVER_RE = re.compile(
    r"^v?(?P<major>0|[1-9]\d*)\.(?P<minor>0|[1-9]\d*)\.(?P<patch>0|[1-9]\d*)"
    r"(?P<suffix>(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?)$"
)
PACKAGE_VERSION_RE = re.compile(r'(?P<prefix>"version"\s*:\s*")(?P<version>[^"]+)(?P<suffix>")')
PYPROJECT_VERSION_RE = re.compile(r'(?P<prefix>^\s*version\s*=\s*")(?P<version>[^"]+)(?P<suffix>")', re.MULTILINE)
GRADLE_VERSION_NAME_RE = re.compile(
    r'(?P<prefix>\bversionName\s*(?:=|\s)\s*")(?P<version>[^"]+)(?P<suffix>")'
)
GRADLE_VERSION_CODE_RE = re.compile(r"(?P<prefix>\bversionCode\s*(?:=|\s)\s*)(?P<code>\d+)")
README_VERSION_RE = re.compile(r"(?P<prefix>\b[Vv]ersion\s*[:=]\s*)(?P<version>v?\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?)")


KNOWN_PACKAGE_PATHS = (
    "package.json",
    "tools/package.json",
    "plugin-client-ts/package.json",
    "client-plugin/package.json",
)


@dataclass(frozen=True)
class RepoEntry:
    repo_id: str
    path: Path
    source: str
    version_file: str
    aliases: tuple[str, ...]


@dataclass(frozen=True)
class VersionSource:
    path: Path
    kind: str
    version: str
    primary: bool


@dataclass(frozen=True)
class RepoGitState:
    branch: str
    upstream: str
    head: str
    dirty_status: tuple[str, ...]
    exact_tags: tuple[str, ...]
    latest_semver_tag: str
    latest_semver_version: str


@dataclass(frozen=True)
class BumpPlan:
    repo: RepoEntry
    state: RepoGitState
    current_version: str
    current_version_source: str
    proposed_version: str
    tag_name: str
    status: str
    reason: str
    tag_only: bool
    dirty_status: tuple[str, ...]
    updated_paths: tuple[str, ...] = ()

    @property
    def actionable(self) -> bool:
        return self.status in {"bump", "tag-only-bump"}

    @property
    def blocked(self) -> bool:
        return self.status.startswith("blocked")


def run_git(repo_path: Path, args: list[str], *, check: bool = False) -> tuple[int, str]:
    completed = subprocess.run(
        ["git", "-C", str(repo_path), *args],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    output = completed.stdout.strip()
    if check and completed.returncode != 0:
        raise RuntimeError(f"git -C {repo_path} {' '.join(args)} failed: {output}")
    return completed.returncode, output


def git_output(repo_path: Path, args: list[str]) -> str:
    code, output = run_git(repo_path, args)
    return output if code == 0 else ""


def parse_semver(value: str) -> tuple[int, int, int, str] | None:
    match = SEMVER_RE.match(value.strip())
    if not match:
        return None
    return (
        int(match.group("major")),
        int(match.group("minor")),
        int(match.group("patch")),
        match.group("suffix") or "",
    )


def normalize_version(value: str) -> str:
    return value.strip().removeprefix("v")


def semver_sort_key(value: str) -> tuple[int, int, int, int, str]:
    parsed = parse_semver(value)
    if not parsed:
        return (-1, -1, -1, -1, value)
    major, minor, patch, suffix = parsed
    stable_rank = 1 if not suffix or suffix.startswith("+") else 0
    return (major, minor, patch, stable_rank, suffix)


def next_minor_version(value: str) -> str:
    parsed = parse_semver(value)
    if not parsed:
        raise ValueError(f"not a semver version: {value}")
    major, minor, _patch, _suffix = parsed
    return f"{major}.{minor + 1}.0"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text_if_changed(path: Path, content: str) -> bool:
    old = path.read_text(encoding="utf-8") if path.exists() else ""
    if old == content:
        return False
    path.write_text(content, encoding="utf-8")
    return True


def read_package_version(path: Path) -> str:
    try:
        data = json.loads(read_text(path))
    except (OSError, json.JSONDecodeError):
        return ""
    version = data.get("version")
    return str(version) if isinstance(version, str) else ""


def read_regex_version(path: Path, pattern: re.Pattern[str]) -> str:
    if not path.exists():
        return ""
    match = pattern.search(read_text(path))
    return match.group("version") if match else ""


def detect_version_source(repo: RepoEntry) -> VersionSource | None:
    version_path = repo.path / repo.version_file if repo.version_file else None
    candidates: list[tuple[Path, str, bool]] = []
    if version_path:
        suffix = version_path.name.lower()
        if suffix == "package.json":
            candidates.append((version_path, "package-json", True))
        elif suffix == "pyproject.toml":
            candidates.append((version_path, "pyproject", True))
        elif suffix.endswith(".gradle") or suffix.endswith(".kts"):
            candidates.append((version_path, "gradle", True))
        elif suffix in {"readme.md", "readme"}:
            candidates.append((version_path, "readme", True))

    for path, kind, primary in candidates:
        version = read_version_from_path(path, kind)
        if version:
            return VersionSource(path=path, kind=kind, version=normalize_version(version), primary=primary)
    return None


def read_version_from_path(path: Path, kind: str) -> str:
    if not path.exists():
        return ""
    if kind == "package-json":
        return read_package_version(path)
    if kind == "pyproject":
        return read_regex_version(path, PYPROJECT_VERSION_RE)
    if kind == "gradle":
        return read_regex_version(path, GRADLE_VERSION_NAME_RE)
    if kind == "readme":
        return read_regex_version(path, README_VERSION_RE)
    return ""


def discover_repos(workspace_root: Path, *, include_missing: bool = False) -> tuple[list[RepoEntry], list[dict[str, str]]]:
    workspace_root = workspace_root.resolve()
    builder_root = workspace_root / "axolync-builder"
    repos_config_path = builder_root / "config" / "repos.json"
    if not repos_config_path.exists():
        raise SystemExit(f"Missing builder repo config: {repos_config_path}")

    config = read_json(repos_config_path)
    rows = [
        {
            "id": "axolync-builder",
            "localPath": ".",
            "versionFile": "package.json",
            "source": "builder-self",
            "submoduleUrl": "https://github.com/korenmic/axolync-builder.git",
        },
        *config.get("repos", []),
    ]

    repos: list[RepoEntry] = []
    notices: list[dict[str, str]] = []
    seen_paths: set[str] = set()

    for row in rows:
        repo_id = str(row.get("id") or "").strip()
        local_path = str(row.get("localPath") or "").strip()
        if not repo_id or not local_path:
            continue
        path = (builder_root / local_path).resolve()
        if not (path / ".git").exists():
            notices.append({"repoId": repo_id, "path": str(path), "reason": "missing-git-checkout"})
            if not include_missing:
                continue
        key = str(path).casefold()
        if key in seen_paths:
            continue
        seen_paths.add(key)
        submodule_url = str(row.get("submoduleUrl") or "")
        github_name = Path(submodule_url.removesuffix(".git")).name if submodule_url else ""
        aliases = tuple(dict.fromkeys(value for value in (repo_id, path.name, github_name) if value))
        repos.append(
            RepoEntry(
                repo_id=repo_id,
                path=path,
                source=str(row.get("source") or "builder-consumed-repo"),
                version_file=str(row.get("versionFile") or ""),
                aliases=aliases,
            )
        )
    return repos, notices


def select_repos(repos: list[RepoEntry], selectors: Iterable[str]) -> tuple[list[RepoEntry], list[str]]:
    requested = [selector.strip() for selector in selectors if selector and selector.strip()]
    if not requested:
        return repos, []
    by_alias: dict[str, RepoEntry] = {}
    for repo in repos:
        for alias in repo.aliases:
            by_alias[alias] = repo
    selected: list[RepoEntry] = []
    missing: list[str] = []
    seen: set[str] = set()
    for selector in requested:
        repo = by_alias.get(selector)
        if not repo:
            missing.append(selector)
            continue
        key = str(repo.path).casefold()
        if key not in seen:
            seen.add(key)
            selected.append(repo)
    return selected, missing


def read_selectors(values: list[str], repo_file: str) -> list[str]:
    selectors: list[str] = []
    for value in values:
        selectors.extend(part.strip() for part in value.split(",") if part.strip())
    if repo_file:
        path = Path(repo_file)
        for line in path.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            selectors.append(stripped)
    return selectors


def inspect_git_state(repo: RepoEntry) -> RepoGitState:
    branch = git_output(repo.path, ["rev-parse", "--abbrev-ref", "HEAD"]) or "unknown"
    upstream = git_output(repo.path, ["rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"])
    head = git_output(repo.path, ["rev-parse", "--short=12", "HEAD"]) or "unknown"
    status = git_output(repo.path, ["status", "--porcelain=1", "--untracked-files=all"])
    exact_tags = tuple(line for line in git_output(repo.path, ["tag", "--points-at", "HEAD"]).splitlines() if line)
    tags = [line.strip() for line in git_output(repo.path, ["tag", "--list"]).splitlines() if line.strip()]
    semver_tags = [tag for tag in tags if parse_semver(tag)]
    latest_tag = max(semver_tags, key=semver_sort_key) if semver_tags else ""
    latest_version = normalize_version(latest_tag) if latest_tag else ""
    return RepoGitState(
        branch=branch,
        upstream=upstream,
        head=head,
        dirty_status=tuple(status.splitlines()) if status else (),
        exact_tags=exact_tags,
        latest_semver_tag=latest_tag,
        latest_semver_version=latest_version,
    )


def tag_exists(repo: RepoEntry, tag_name: str) -> bool:
    return bool(git_output(repo.path, ["rev-parse", "--verify", "--quiet", f"refs/tags/{tag_name}"]))


def make_plan(
    repo: RepoEntry,
    *,
    include_tagged_head: bool = False,
    require_branch: str = "master",
) -> BumpPlan:
    state = inspect_git_state(repo)
    version_source = detect_version_source(repo)
    current_version = version_source.version if version_source else state.latest_semver_version
    current_source = (
        f"{version_source.kind}:{version_source.path.relative_to(repo.path).as_posix()}"
        if version_source
        else ("tag-only:latest-semver-tag" if state.latest_semver_tag else "none")
    )
    tag_only = version_source is None

    if require_branch and state.branch != require_branch:
        return BumpPlan(repo, state, current_version, current_source, "", "", "blocked-branch", f"expected {require_branch}, found {state.branch}", tag_only, state.dirty_status)
    if state.dirty_status:
        return BumpPlan(repo, state, current_version, current_source, "", "", "blocked-dirty", "working tree has uncommitted changes", tag_only, state.dirty_status)
    if state.exact_tags and not include_tagged_head:
        return BumpPlan(repo, state, current_version, current_source, "", "", "skipped-tagged-head", ",".join(state.exact_tags), tag_only, ())
    if not current_version or not parse_semver(current_version):
        return BumpPlan(repo, state, current_version, current_source, "", "", "blocked-no-semver", "no semver version source and no semver tag", tag_only, ())

    next_version = next_minor_version(current_version)
    tag_name = f"v{next_version}"
    if tag_exists(repo, tag_name):
        return BumpPlan(repo, state, current_version, current_source, next_version, tag_name, "blocked-tag-collision", f"tag already exists: {tag_name}", tag_only, ())

    return BumpPlan(
        repo=repo,
        state=state,
        current_version=current_version,
        current_version_source=current_source,
        proposed_version=next_version,
        tag_name=tag_name,
        status="tag-only-bump" if tag_only else "bump",
        reason="minor bump planned",
        tag_only=tag_only,
        dirty_status=(),
    )


def replace_package_version(path: Path, new_version: str) -> bool:
    data = json.loads(read_text(path))
    data["version"] = new_version
    content = json.dumps(data, indent=2, ensure_ascii=False) + "\n"
    return write_text_if_changed(path, content)


def replace_package_lock_version(path: Path, old_version: str, new_version: str) -> bool:
    if not path.exists():
        return False
    data = json.loads(read_text(path))
    changed = False
    if data.get("version") == old_version:
        data["version"] = new_version
        changed = True
    packages = data.get("packages")
    if isinstance(packages, dict):
        root_package = packages.get("")
        if isinstance(root_package, dict) and root_package.get("version") == old_version:
            root_package["version"] = new_version
            changed = True
    if not changed:
        return False
    return write_text_if_changed(path, json.dumps(data, indent=2, ensure_ascii=False) + "\n")


def replace_regex_version(path: Path, pattern: re.Pattern[str], old_version: str, new_version: str) -> bool:
    if not path.exists():
        return False
    content = read_text(path)

    def replacement(match: re.Match[str]) -> str:
        if normalize_version(match.group("version")) != normalize_version(old_version):
            return match.group(0)
        return f"{match.group('prefix')}{new_version}{match.group('suffix') if 'suffix' in match.groupdict() else ''}"

    updated = pattern.sub(replacement, content, count=1)
    return write_text_if_changed(path, updated)


def replace_gradle_version(path: Path, old_version: str, new_version: str) -> bool:
    content = read_text(path)

    def name_replacement(match: re.Match[str]) -> str:
        if normalize_version(match.group("version")) != normalize_version(old_version):
            return match.group(0)
        return f"{match.group('prefix')}{new_version}{match.group('suffix')}"

    updated = GRADLE_VERSION_NAME_RE.sub(name_replacement, content, count=1)

    def code_replacement(match: re.Match[str]) -> str:
        return f"{match.group('prefix')}{int(match.group('code')) + 1}"

    updated = GRADLE_VERSION_CODE_RE.sub(code_replacement, updated, count=1)
    return write_text_if_changed(path, updated)


def apply_version_updates(plan: BumpPlan) -> tuple[str, ...]:
    if plan.tag_only:
        return ()
    repo = plan.repo
    old_version = plan.current_version
    new_version = plan.proposed_version
    changed: list[str] = []

    candidates: list[tuple[Path, str]] = []
    primary = detect_version_source(repo)
    if primary:
        candidates.append((primary.path, primary.kind))
    for relative in KNOWN_PACKAGE_PATHS:
        path = repo.path / relative
        if path.exists() and all(path != existing for existing, _kind in candidates):
            candidates.append((path, "package-json"))
    pyproject = repo.path / "pyproject.toml"
    if pyproject.exists() and all(pyproject != existing for existing, _kind in candidates):
        candidates.append((pyproject, "pyproject"))

    for path, kind in candidates:
        existing = normalize_version(read_version_from_path(path, kind))
        if existing != normalize_version(old_version):
            continue
        did_change = False
        if kind == "package-json":
            did_change = replace_package_version(path, new_version)
            lock_path = path.parent / "package-lock.json"
            if replace_package_lock_version(lock_path, old_version, new_version):
                changed.append(lock_path.relative_to(repo.path).as_posix())
        elif kind == "pyproject":
            did_change = replace_regex_version(path, PYPROJECT_VERSION_RE, old_version, new_version)
        elif kind == "gradle":
            did_change = replace_gradle_version(path, old_version, new_version)
        elif kind == "readme":
            did_change = replace_regex_version(path, README_VERSION_RE, old_version, new_version)
        if did_change:
            changed.append(path.relative_to(repo.path).as_posix())
    return tuple(dict.fromkeys(changed))


def pull_repo(repo: RepoEntry) -> None:
    run_git(repo.path, ["fetch", "--prune", "origin"], check=True)
    branch = git_output(repo.path, ["rev-parse", "--abbrev-ref", "HEAD"])
    upstream = git_output(repo.path, ["rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"])
    if upstream:
        run_git(repo.path, ["pull", "--rebase"], check=True)
    elif branch == "master":
        run_git(repo.path, ["pull", "--rebase", "origin", "master"], check=True)


def apply_plan(plan: BumpPlan, *, push: bool = False) -> BumpPlan:
    repo = plan.repo
    changed_paths = apply_version_updates(plan)
    if not plan.tag_only and not changed_paths:
        raise RuntimeError(f"{repo.repo_id}: no version files changed for planned bump")

    if changed_paths:
        run_git(repo.path, ["add", *changed_paths], check=True)
        run_git(repo.path, ["commit", "-m", f"chore: bump version to {plan.proposed_version}"], check=True)

    run_git(repo.path, ["tag", "-a", plan.tag_name, "-m", plan.tag_name], check=True)
    if push:
        branch = git_output(repo.path, ["rev-parse", "--abbrev-ref", "HEAD"]) or "master"
        run_git(repo.path, ["push", "origin", branch], check=True)
        run_git(repo.path, ["push", "origin", plan.tag_name], check=True)

    new_state = inspect_git_state(repo)
    return BumpPlan(
        repo=repo,
        state=new_state,
        current_version=plan.current_version,
        current_version_source=plan.current_version_source,
        proposed_version=plan.proposed_version,
        tag_name=plan.tag_name,
        status="applied",
        reason="minor bump applied",
        tag_only=plan.tag_only,
        dirty_status=(),
        updated_paths=changed_paths,
    )


def plan_rows(plans: list[BumpPlan]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for plan in plans:
        rows.append(
            {
                "repoId": plan.repo.repo_id,
                "aliases": list(plan.repo.aliases),
                "path": str(plan.repo.path),
                "branch": plan.state.branch,
                "head": plan.state.head,
                "exactTags": list(plan.state.exact_tags),
                "latestSemverTag": plan.state.latest_semver_tag,
                "currentVersion": plan.current_version,
                "currentVersionSource": plan.current_version_source,
                "proposedVersion": plan.proposed_version,
                "proposedTag": plan.tag_name,
                "status": plan.status,
                "reason": plan.reason,
                "tagOnly": plan.tag_only,
                "dirtyStatus": list(plan.dirty_status),
                "updatedPaths": list(plan.updated_paths),
            }
        )
    return rows


def make_text_table(rows: list[dict[str, Any]], notices: list[dict[str, str]] | None = None) -> str:
    headers = ["repo", "branch", "head", "current", "latest_tag", "next", "status", "source"]
    table_rows = []
    for row in rows:
        table_rows.append(
            [
                str(row["repoId"]),
                str(row["branch"]),
                str(row["head"]),
                str(row["currentVersion"] or "-"),
                str(row["latestSemverTag"] or "-"),
                str(row["proposedVersion"] or "-"),
                str(row["status"]),
                str(row["currentVersionSource"] or "-"),
            ]
        )
    widths = [len(header) for header in headers]
    for row in table_rows:
        widths = [max(width, len(value)) for width, value in zip(widths, row)]

    lines = ["  ".join(header.ljust(width) for header, width in zip(headers, widths))]
    lines.append("  ".join("-" * width for width in widths))
    for row in table_rows:
        lines.append("  ".join(value.ljust(width) for value, width in zip(row, widths)))
    for notice in notices or []:
        lines.append(f"NOTICE {notice['repoId']}: {notice['reason']} {notice['path']}")
    return "\n".join(lines) + "\n"


def make_markdown_table(rows: list[dict[str, Any]], notices: list[dict[str, str]] | None = None) -> str:
    headers = ["repo", "branch", "head", "current", "latest tag", "next", "status", "source"]
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"]
    for row in rows:
        values = [
            row["repoId"],
            row["branch"],
            row["head"],
            row["currentVersion"] or "-",
            row["latestSemverTag"] or "-",
            row["proposedVersion"] or "-",
            row["status"],
            row["currentVersionSource"] or "-",
        ]
        lines.append("| " + " | ".join(str(value).replace("|", "\\|") for value in values) + " |")
    for notice in notices or []:
        lines.append(f"\nNOTICE {notice['repoId']}: {notice['reason']} {notice['path']}")
    return "\n".join(lines) + "\n"


def default_output_path(workspace_root: Path, prefix: str, fmt: str) -> Path:
    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    suffix = "md" if fmt == "md" else "txt"
    return workspace_root / f"{prefix}_{stamp}.{suffix}"


def emit_outputs(
    payload: dict[str, Any],
    rows: list[dict[str, Any]],
    notices: list[dict[str, str]],
    *,
    workspace_root: Path,
    output: str,
    json_output: str,
    fmt: str,
    prefix: str,
) -> Path | None:
    table = make_markdown_table(rows, notices) if fmt == "md" else make_text_table(rows, notices)
    output_path: Path | None = None
    if output == "-":
        print(table, end="")
    else:
        output_path = Path(output) if output else default_output_path(workspace_root, prefix, fmt)
        output_path.write_text(table, encoding="utf-8")
        print(f"Wrote {output_path}")
    if json_output:
        json_path = Path(json_output)
        json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        print(f"Wrote {json_path}")
    return output_path


def build_plans(
    repos: list[RepoEntry],
    *,
    include_tagged_head: bool,
    require_branch: str,
) -> list[BumpPlan]:
    return [make_plan(repo, include_tagged_head=include_tagged_head, require_branch=require_branch) for repo in repos]


def command_inventory(args: argparse.Namespace) -> int:
    workspace_root, repos, notices = load_requested_repos(args)
    plans = build_plans(repos, include_tagged_head=args.include_tagged_head, require_branch=args.require_branch)
    rows = plan_rows(plans)
    payload = {"workspaceRoot": str(workspace_root), "mode": "inventory", "repos": rows, "notices": notices}
    emit_outputs(
        payload,
        rows,
        notices,
        workspace_root=workspace_root,
        output=args.output,
        json_output=args.json_output,
        fmt=args.format,
        prefix="VERSION_TAGS",
    )
    return 2 if args.fail_on_blocked and any(plan.blocked for plan in plans) else 0


def command_plan_bump(args: argparse.Namespace) -> int:
    workspace_root, repos, notices = load_requested_repos(args)
    if args.pull_first:
        for repo in repos:
            if inspect_git_state(repo).dirty_status:
                raise SystemExit(f"Cannot pull dirty repo: {repo.repo_id}")
            pull_repo(repo)
    plans = build_plans(repos, include_tagged_head=args.include_tagged_head, require_branch=args.require_branch)
    rows = plan_rows(plans)
    payload = {"workspaceRoot": str(workspace_root), "mode": "plan-bump", "repos": rows, "notices": notices}
    emit_outputs(
        payload,
        rows,
        notices,
        workspace_root=workspace_root,
        output=args.output,
        json_output=args.json_output,
        fmt=args.format,
        prefix="VERSION_BUMP_PLAN",
    )
    return 2 if any(plan.blocked for plan in plans) else 0


def command_apply_bump(args: argparse.Namespace) -> int:
    workspace_root, repos, notices = load_requested_repos(args)
    if not args.yes:
        raise SystemExit("apply-bump requires --yes after reviewing plan output")
    if args.pull_first:
        for repo in repos:
            if inspect_git_state(repo).dirty_status:
                raise SystemExit(f"Cannot pull dirty repo: {repo.repo_id}")
            pull_repo(repo)

    plans = build_plans(repos, include_tagged_head=args.include_tagged_head, require_branch=args.require_branch)
    blocked = [plan for plan in plans if plan.blocked]
    if blocked:
        rows = plan_rows(plans)
        payload = {"workspaceRoot": str(workspace_root), "mode": "apply-bump", "repos": rows, "notices": notices}
        emit_outputs(
            payload,
            rows,
            notices,
            workspace_root=workspace_root,
            output=args.output,
            json_output=args.json_output,
            fmt=args.format,
            prefix="VERSION_BUMP_BLOCKED",
        )
        return 2

    applied: list[BumpPlan] = []
    for plan in plans:
        if not plan.actionable:
            applied.append(plan)
            continue
        print(f"Applying {plan.repo.repo_id}: {plan.current_version} -> {plan.proposed_version} ({plan.tag_name})")
        applied.append(apply_plan(plan, push=args.push))

    rows = plan_rows(applied)
    payload = {"workspaceRoot": str(workspace_root), "mode": "apply-bump", "repos": rows, "notices": notices}
    emit_outputs(
        payload,
        rows,
        notices,
        workspace_root=workspace_root,
        output=args.output,
        json_output=args.json_output,
        fmt=args.format,
        prefix="VERSION_BUMP_APPLIED",
    )
    return 0


def command_verify(args: argparse.Namespace) -> int:
    workspace_root, repos, notices = load_requested_repos(args)
    rows = []
    failed = False
    for repo in repos:
        state = inspect_git_state(repo)
        source = detect_version_source(repo)
        current_version = source.version if source else state.latest_semver_version
        expected_tag = f"v{current_version}" if current_version else ""
        has_expected_tag = expected_tag in state.exact_tags if expected_tag else False
        if not has_expected_tag:
            failed = True
        rows.append(
            {
                "repoId": repo.repo_id,
                "aliases": list(repo.aliases),
                "path": str(repo.path),
                "branch": state.branch,
                "head": state.head,
                "exactTags": list(state.exact_tags),
                "latestSemverTag": state.latest_semver_tag,
                "currentVersion": current_version,
                "currentVersionSource": (
                    f"{source.kind}:{source.path.relative_to(repo.path).as_posix()}" if source else "tag-only:latest-semver-tag"
                ),
                "proposedVersion": "",
                "proposedTag": expected_tag,
                "status": "verified" if has_expected_tag else "blocked-missing-head-tag",
                "reason": "" if has_expected_tag else f"expected tag at HEAD: {expected_tag}",
                "tagOnly": source is None,
                "dirtyStatus": list(state.dirty_status),
                "updatedPaths": [],
            }
        )
    payload = {"workspaceRoot": str(workspace_root), "mode": "verify", "repos": rows, "notices": notices}
    emit_outputs(
        payload,
        rows,
        notices,
        workspace_root=workspace_root,
        output=args.output,
        json_output=args.json_output,
        fmt=args.format,
        prefix="VERSION_TAG_VERIFY",
    )
    return 1 if failed else 0


def load_requested_repos(args: argparse.Namespace) -> tuple[Path, list[RepoEntry], list[dict[str, str]]]:
    workspace_root = Path(args.workspace_root).resolve() if args.workspace_root else find_workspace_root(Path.cwd())
    repos, notices = discover_repos(workspace_root, include_missing=args.include_missing)
    selectors = read_selectors(args.repo, args.repo_file)
    selected, missing = select_repos(repos, selectors)
    if missing:
        raise SystemExit(f"Unknown repo selector(s): {', '.join(missing)}")
    return workspace_root, selected, notices


def add_common_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--workspace-root", default="", help="Workspace root containing axolync-builder.")
    parser.add_argument("--repo", action="append", default=[], help="Repo id/folder/GitHub name. Repeatable or comma-separated.")
    parser.add_argument("--repo-file", default="", help="File containing repo selectors, one per line.")
    parser.add_argument("--include-missing", action="store_true", help="Include missing declared repos in notices.")
    parser.add_argument("--include-tagged-head", action="store_true", help="Plan a new bump even when HEAD already has a tag.")
    parser.add_argument("--require-branch", default="master", help="Required branch for bump planning. Empty disables the guard.")
    parser.add_argument("--format", choices=["txt", "md"], default="txt", help="Human table format.")
    parser.add_argument("--output", default="", help="Human table output path. Use '-' for stdout.")
    parser.add_argument("--json-output", default="", help="Optional JSON output path.")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    inventory = subparsers.add_parser("inventory", help="List repo version/tag state without mutation.")
    add_common_arguments(inventory)
    inventory.add_argument("--fail-on-blocked", action="store_true", help="Exit non-zero if inventory detects blocked bump rows.")
    inventory.set_defaults(func=command_inventory)

    plan = subparsers.add_parser("plan-bump", help="Plan a controlled minor version/tag bump.")
    add_common_arguments(plan)
    plan.add_argument("--pull-first", action="store_true", help="Fetch/pull each clean repo before planning.")
    plan.set_defaults(func=command_plan_bump)

    apply = subparsers.add_parser("apply-bump", help="Apply a reviewed minor version/tag bump.")
    add_common_arguments(apply)
    apply.add_argument("--yes", action="store_true", help="Required acknowledgement that plan was reviewed.")
    apply.add_argument("--push", action="store_true", help="Push commits and tags after applying.")
    apply.add_argument("--pull-first", action="store_true", help="Fetch/pull each clean repo before applying.")
    apply.set_defaults(func=command_apply_bump)

    verify = subparsers.add_parser("verify", help="Verify current versions have matching tags at HEAD.")
    add_common_arguments(verify)
    verify.set_defaults(func=command_verify)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
