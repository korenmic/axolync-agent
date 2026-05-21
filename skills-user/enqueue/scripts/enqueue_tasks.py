from __future__ import annotations

import argparse
import base64
import re
import subprocess
import sys
import zlib
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


@dataclass(frozen=True)
class SourceTask:
    source_path: Path
    task_number: str | None
    counted_index: int
    text: str
    checked: bool
    line_number: int

    @property
    def label(self) -> str:
        return f"{self.task_number}. {self.text}" if self.task_number else self.text


@dataclass(frozen=True)
class DuplicateCheck:
    new_tasks: tuple[SourceTask, ...]
    duplicate_tasks: tuple[SourceTask, ...]


@dataclass(frozen=True)
class EnqueueResult:
    added_qids: tuple[str, ...]
    added_count: int
    skipped_duplicate_count: int
    skipped_duplicate_labels: tuple[str, ...]


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


def normalize_task_identity(value: str) -> str:
    value = value.strip().strip("`").strip()
    value = re.sub(r"^\s*[-*]\s+\[[ xX]\]\s*", "", value)
    value = re.sub(r"\s+", " ", value)
    return value.rstrip(".").lower()


def normalize_source_identity(value: str | Path, workspace_root: Path) -> str:
    raw = str(value).strip().strip("`")
    link_match = re.search(r"\[[^\]]+\]\(([^)]+)\)", raw)
    if link_match:
        raw = link_match.group(1).strip()
    raw = raw.replace("\\", "/")
    if re.match(r"^/[A-Za-z]:/", raw):
        raw = raw[1:]
    path = Path(raw)
    if not path.is_absolute():
        path = workspace_root / path
    try:
        return str(path.resolve()).lower()
    except OSError:
        return str(path).lower()


def source_task_duplicate_key(task: SourceTask, workspace_root: Path) -> tuple[str, str]:
    task_identity = task.task_number or normalize_task_identity(task.text)
    return normalize_source_identity(task.source_path, workspace_root), task_identity


def _extract_markdown_field(body: str, field_name: str) -> str | None:
    match = re.search(rf"(?m)^- {re.escape(field_name)}: (.+)$", body)
    return match.group(1).strip() if match else None


def existing_source_task_keys(queue_path: Path, workspace_root: Path) -> set[tuple[str, str]]:
    if not queue_path.exists():
        return set()
    text = queue_path.read_text(encoding="utf-8-sig", errors="replace")
    pieces = re.split(r"(?m)^### +Q-\d+\s*$", text)
    keys: set[tuple[str, str]] = set()
    for body in pieces[1:]:
        source_raw = _extract_markdown_field(body, "Source")
        task_raw = _extract_markdown_field(body, "Task")
        if not source_raw or not task_raw:
            continue
        if "tasks.md" not in source_raw.replace("\\", "/"):
            continue
        task_text = _normalize_selector(task_raw)
        number_match = TASK_NUMBER_RE.match(task_text)
        task_identity = number_match.group(1) if number_match else normalize_task_identity(task_text)
        keys.add((normalize_source_identity(source_raw, workspace_root), task_identity))
    return keys


def filter_duplicate_source_tasks(
    tasks: Iterable[SourceTask],
    queue_path: Path,
    workspace_root: Path,
) -> DuplicateCheck:
    existing_keys = existing_source_task_keys(queue_path, workspace_root)
    new_tasks: list[SourceTask] = []
    duplicate_tasks: list[SourceTask] = []
    for task in tasks:
        key = source_task_duplicate_key(task, workspace_root)
        if key in existing_keys:
            duplicate_tasks.append(task)
            continue
        existing_keys.add(key)
        new_tasks.append(task)
    return DuplicateCheck(tuple(new_tasks), tuple(duplicate_tasks))


def _markdown_link_path(path: Path) -> str:
    normalized = str(path.resolve()).replace("\\", "/")
    if re.match(r"^[A-Za-z]:/", normalized):
        return f"/{normalized}"
    return normalized


def _to_posix_path(path: str | Path) -> str:
    return str(path).replace("\\", "/")


def _find_git_root(path: Path) -> Path | None:
    current = path.resolve()
    if current.is_file():
        current = current.parent
    while True:
        if (current / ".git").exists():
            return current
        parent = current.parent
        if parent == current:
            return None
        current = parent


def _relative_or_absolute(path: Path, base: Path) -> str:
    try:
        return _to_posix_path(path.resolve().relative_to(base.resolve()))
    except ValueError:
        return _to_posix_path(path.resolve())


def human_task_id_for_source_task(task: SourceTask, workspace_root: Path) -> str | None:
    """Return the same human task id shape produced by the task-id skill."""
    repo_root = _find_git_root(task.source_path)
    if repo_root is None:
        return None
    try:
        repo = _to_posix_path(repo_root.resolve().relative_to(workspace_root.resolve()))
    except ValueError:
        repo = repo_root.name
    if not repo or repo == ".":
        repo = repo_root.name
    rel_source = _relative_or_absolute(task.source_path, repo_root)
    task_index = task.task_number if task.task_number and task.task_number.isdigit() else str(task.counted_index)
    return f"htid1:{repo}::{rel_source}::{task_index}"


def packed_task_id_for_human_id(human_id: str) -> str:
    compressor = zlib.compressobj(wbits=-15)
    compressed = compressor.compress(human_id.encode("utf-8")) + compressor.flush()
    encoded = base64.urlsafe_b64encode(compressed).decode("ascii").rstrip("=")
    return f"atid1:{encoded}"


def task_id_lines_for_source_task(task: SourceTask, workspace_root: Path) -> str:
    human_id = human_task_id_for_source_task(task, workspace_root)
    if human_id is None:
        return ""
    packed_id = packed_task_id_for_human_id(human_id)
    return f"- TaskId: `{human_id}`\n- TaskIdPacked: `{packed_id}`\n"


def _format_source_record(qid_number: int, task: SourceTask, workspace_root: Path) -> str:
    return (
        f"### Q-{qid_number:03d}\n"
        "- Status: `queued`\n"
        f"- Source: [tasks.md]({_markdown_link_path(task.source_path)})\n"
        f"{task_id_lines_for_source_task(task, workspace_root)}"
        f"- Task: `{task.label}`\n"
    )


def _format_inline_record(qid_number: int, task_text: str) -> str:
    return (
        f"### Q-{qid_number:03d}\n"
        "- Status: `queued`\n"
        "- Source: `inline procedural queue task`\n"
        f"- Task: `{task_text}`\n"
    )


def _append_queue_records(queue_path: Path, record_blocks: Iterable[str]) -> None:
    blocks = [block.rstrip() for block in record_blocks]
    if not blocks:
        return
    existing = queue_path.read_text(encoding="utf-8-sig", errors="replace")
    separator = "\n\n" if existing.rstrip() else ""
    joined_blocks = "\n\n".join(blocks)
    queue_path.write_text(
        f"{existing.rstrip()}{separator}{joined_blocks}\n",
        encoding="utf-8",
    )


def enqueue_selection(state: QueueState, selection: SourceSelection) -> EnqueueResult:
    validate_source_selection(selection)
    source_tasks = select_source_tasks(selection)
    duplicate_check = filter_duplicate_source_tasks(source_tasks, state.queue_path, state.workspace_root)
    qid_number = state.next_qid_number
    record_blocks: list[str] = []
    added_qids: list[str] = []

    for task in duplicate_check.new_tasks:
        record_blocks.append(_format_source_record(qid_number, task, state.workspace_root))
        added_qids.append(f"Q-{qid_number:03d}")
        qid_number += 1

    for task_text in selection.inline_tasks:
        record_blocks.append(_format_inline_record(qid_number, task_text))
        added_qids.append(f"Q-{qid_number:03d}")
        qid_number += 1

    _append_queue_records(state.queue_path, record_blocks)
    return EnqueueResult(
        added_qids=tuple(added_qids),
        added_count=len(added_qids),
        skipped_duplicate_count=len(duplicate_check.duplicate_tasks),
        skipped_duplicate_labels=tuple(task.label for task in duplicate_check.duplicate_tasks),
    )


def queue_status_script_path() -> Path:
    return Path(__file__).resolve().parents[2] / "queue-status" / "scripts" / "queue_status.py"


def run_queue_status_verbose(workspace_root: Path) -> str:
    script = queue_status_script_path()
    if not script.exists():
        raise EnqueueInputError(f"queue-status verbose is unavailable; missing script: {script}")
    completed = subprocess.run(
        [sys.executable, str(script), "--workspace-root", str(workspace_root), "verbose"],
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.rstrip()


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


TASK_LINE_RE = re.compile(r"^\s*[-*]\s+\[([ xX])\]\s+(.+?)\s*$")
TASK_NUMBER_RE = re.compile(r"^(\d+(?:\.\d+)*)\.\s+(.+)$")


def parse_source_tasks(source_path: Path) -> list[SourceTask]:
    tasks: list[SourceTask] = []
    for index, line in enumerate(source_path.read_text(encoding="utf-8-sig", errors="replace").splitlines(), start=1):
        match = TASK_LINE_RE.match(line)
        if not match:
            continue
        raw_text = match.group(2).strip()
        number_match = TASK_NUMBER_RE.match(raw_text)
        if number_match:
            task_number = number_match.group(1)
            text = number_match.group(2).strip()
        else:
            task_number = None
            text = raw_text
        tasks.append(
            SourceTask(
                source_path=source_path.resolve(),
                task_number=task_number,
                counted_index=len(tasks) + 1,
                text=text,
                checked=match.group(1).lower() == "x",
                line_number=index,
            )
        )
    return tasks


def _task_matches_selector(task: SourceTask, selector: str) -> bool:
    selector = _normalize_selector(selector)
    if not selector:
        return False
    if task.task_number and selector == task.task_number:
        return True
    return normalize_task_identity(selector) in {
        normalize_task_identity(task.text),
        normalize_task_identity(task.label),
    }


def select_source_tasks(selection: SourceSelection, include_done: bool = False) -> list[SourceTask]:
    validate_source_selection(selection)
    selected: list[SourceTask] = []
    for source_path in selection.source_paths:
        source_tasks = parse_source_tasks(source_path)
        if selection.task_selectors:
            source_tasks = [
                task
                for task in source_tasks
                if any(_task_matches_selector(task, selector) for selector in selection.task_selectors)
            ]
        selected.extend(task for task in source_tasks if include_done or not task.checked)
    return selected


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
    parser.add_argument(
        "--skip-status",
        action="store_true",
        help="Skip final queue-status verbose output. Intended for narrow tests only.",
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
        if selection.source_paths:
            selected_tasks = select_source_tasks(selection)
            print(f"Selected source tasks: {len(selected_tasks)}")
        result = enqueue_selection(state, selection)
        print("")
        print("Enqueue result:")
        print(f"- Added: {result.added_count}")
        print(f"- Added qids: {', '.join(result.added_qids) if result.added_qids else 'none'}")
        print(f"- Skipped duplicates: {result.skipped_duplicate_count}")
        if not args.skip_status:
            print("")
            print(run_queue_status_verbose(state.workspace_root))
        print("")
        print(f"Added {result.added_count} undone tasks in this enqueue session.")
        if result.skipped_duplicate_count:
            print(f"Skipped {result.skipped_duplicate_count} duplicate tasks.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
