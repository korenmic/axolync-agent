from __future__ import annotations

import argparse
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


DEFAULT_QUEUE_TARGET = "current workspace undone enqueued tasks"


@dataclass(frozen=True)
class ImplementPlan:
    task_source: str
    tactic_arguments: tuple[str, ...]
    uses_default_queue: bool


@dataclass(frozen=True)
class WorktreeWarning:
    repo_path: Path
    dirty: bool
    status_lines: tuple[str, ...]

    @property
    def message(self) -> str:
        if not self.dirty:
            return f"Worktree clean: {self.repo_path}"
        return (
            f"Warning: worktree is not clean: {self.repo_path}. "
            "Proceeding leaves dirty-state handling to $tactic."
        )


def resolve_implement_plan(tactic_arguments: Iterable[str] | None = None) -> ImplementPlan:
    arguments = tuple(arg for arg in (tactic_arguments or ()) if arg)
    return ImplementPlan(
        task_source=" ".join(arguments) if arguments else DEFAULT_QUEUE_TARGET,
        tactic_arguments=arguments,
        uses_default_queue=not arguments,
    )


def format_tactic_handoff(plan: ImplementPlan) -> str:
    if plan.uses_default_queue:
        return "Run $tactic over the current workspace undone enqueued tasks."
    return f"Run $tactic with forwarded arguments: {' '.join(plan.tactic_arguments)}"


def build_worktree_warning(repo_path: Path, status_output: str) -> WorktreeWarning:
    status_lines = tuple(line for line in status_output.splitlines() if line.strip())
    return WorktreeWarning(repo_path=repo_path, dirty=bool(status_lines), status_lines=status_lines)


def inspect_worktree(repo_path: Path) -> WorktreeWarning:
    completed = subprocess.run(
        ["git", "-C", str(repo_path), "status", "--short"],
        check=True,
        capture_output=True,
        text=True,
    )
    return build_worktree_warning(repo_path, completed.stdout)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Describe an $implement wrapper handoff to $tactic.")
    parser.add_argument(
        "tactic_arguments",
        nargs="*",
        help="Arguments to forward unchanged to $tactic. Omit to use undone enqueued tasks.",
    )
    parser.add_argument(
        "--repo-root",
        default=".",
        help="Repo path to inspect for the non-blocking dirty-worktree warning.",
    )
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    plan = resolve_implement_plan(args.tactic_arguments)
    print(inspect_worktree(Path(args.repo_root)).message)
    print(format_tactic_handoff(plan))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
