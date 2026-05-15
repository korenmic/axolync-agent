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
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    state = discover_queue_state(resolve_path(args.workspace_root), create=not args.no_create)
    print(format_queue_state(state))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

