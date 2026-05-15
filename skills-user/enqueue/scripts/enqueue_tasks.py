from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


QUEUE_RELATIVE_PATH = Path(".codex") / "local-task-queue.md"

QUEUE_HEADER = """# Local Task Queue

Purpose:
- Local execution queue for work we want to batch later with `play the queue`.
- Stored outside tracked repos so it does not create repo churn.

Queue rules:
- Status starts as `queued`.
- Source points to the authoritative task item in the spec file when one exists.
- Queue order is the append order below.
- When we later `play the queue`, execution may be reordered pragmatically by prerequisites, but every queued item remains in scope unless catastrophically blocked.

## Queued Items
"""


@dataclass(frozen=True)
class QueueState:
    workspace_root: Path
    queue_path: Path
    created: bool
    next_qid_number: int


@dataclass(frozen=True)
class SourceSelection:
    source_paths: tuple[Path, ...]
    task_selectors: tuple[str, ...]
    inline_tasks: tuple[str, ...]


class EnqueueInputError(ValueError):
    pass


def resolve_path(value: str | Path) -> Path:
    return Path(value).expanduser().resolve()


def queue_path_for_workspace(workspace_root: Path) -> Path:
    return workspace_root.resolve() / QUEUE_RELATIVE_PATH


def ensure_queue_file(workspace_root: Path) -> tuple[Path, bool]:
    queue_path = queue_path_for_workspace(workspace_root)
    if queue_path.exists():
        return queue_path, False
    queue_path.parent.mkdir(parents=True, exist_ok=True)
    queue_path.write_text(f"{QUEUE_HEADER}\n", encoding="utf-8")
    return queue_path, True


def highest_qid_number(queue_text: str) -> int:
    numbers = [
        int(match.group(1))
        for match in re.finditer(r"(?m)^### Q-(\d+)\s*$", queue_text)
    ]
    return max(numbers, default=0)


def discover_queue_state(workspace_root: Path, create: bool = True) -> QueueState:
    workspace_root = workspace_root.resolve()
    if create:
        queue_path, created = ensure_queue_file(workspace_root)
    else:
        queue_path = queue_path_for_workspace(workspace_root)
        created = False
        if not queue_path.exists():
            raise FileNotFoundError(f"queue file does not exist: {queue_path}")
    queue_text = queue_path.read_text(encoding="utf-8-sig", errors="replace")
    return QueueState(
        workspace_root=workspace_root,
        queue_path=queue_path,
        created=created,
        next_qid_number=highest_qid_number(queue_text) + 1,
    )


def format_queue_state(state: QueueState) -> str:
    created = "yes" if state.created else "no"
    return "\n".join([
        "# Enqueue Queue State",
        "",
        f"Workspace: {state.workspace_root}",
        f"Queue: {state.queue_path}",
        f"Created: {created}",
        f"Next qid: Q-{state.next_qid_number:03d}",
    ])


def _normalize_selector(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip().strip("`")).strip()


def resolve_source_selection(
    workspace_root: Path,
    source_paths: Iterable[str | Path] | None = None,
    task_selectors: Iterable[str] | None = None,
    inline_tasks: Iterable[str] | None = None,
) -> SourceSelection:
    workspace_root = workspace_root.resolve()
    resolved_paths = []
    for source_path in source_paths or ():
        path = Path(source_path).expanduser()
        if not path.is_absolute():
            path = workspace_root / path
        resolved_paths.append(path.resolve())
    selectors = tuple(
        selector
        for selector in (_normalize_selector(value) for value in (task_selectors or ()))
        if selector
    )
    inline = tuple(
        task
        for task in (_normalize_selector(value) for value in (inline_tasks or ()))
        if task
    )
    return SourceSelection(
        source_paths=tuple(resolved_paths),
        task_selectors=selectors,
        inline_tasks=inline,
    )


def validate_source_selection(selection: SourceSelection) -> None:
    if not selection.source_paths and not selection.inline_tasks:
        raise EnqueueInputError(
            "no enqueue task source was provided; use conversation context, --task-source, or --inline-task"
        )
    missing_paths = [str(path) for path in selection.source_paths if not path.exists()]
    if missing_paths:
        raise EnqueueInputError(f"task source path does not exist: {', '.join(missing_paths)}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Append scoped tasks to a local task queue.")
    parser.add_argument(
        "--workspace-root",
        default=".",
        help="Workspace root containing .codex/local-task-queue.md.",
    )
    parser.add_argument(
        "--no-create",
        action="store_true",
        help="Fail instead of creating the queue file when it is missing.",
    )
    parser.add_argument(
        "--task-source",
        action="append",
        default=[],
        help="Specific spec/backlog tasks.md file to enqueue from. Repeat for groups.",
    )
    parser.add_argument(
        "--task",
        action="append",
        default=[],
        help="Specific task number/title selector within the supplied source files.",
    )
    parser.add_argument(
        "--inline-task",
        action="append",
        default=[],
        help="Context-only by-value task text with no authoritative source file.",
    )
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    state = discover_queue_state(resolve_path(args.workspace_root), create=not args.no_create)
    selection = resolve_source_selection(
        state.workspace_root,
        source_paths=args.task_source,
        task_selectors=args.task,
        inline_tasks=args.inline_task,
    )
    print(format_queue_state(state))
    if selection.source_paths or selection.task_selectors or selection.inline_tasks:
        print("")
        print("Resolved enqueue scope:")
        for path in selection.source_paths:
            print(f"- source: {path}")
        for selector in selection.task_selectors:
            print(f"- task selector: {selector}")
        for task in selection.inline_tasks:
            print(f"- inline task: {task}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
