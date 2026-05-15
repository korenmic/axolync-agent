from __future__ import annotations

import argparse
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable


MARKDOWN_QUEUE = Path(".codex") / "local-task-queue.md"
JSON_QUEUE = Path(".codex") / "tmp" / "execution-queue.json"


@dataclass(frozen=True)
class QueueArtifact:
    path: Path
    discovery_method: str
    active: bool


@dataclass
class QueueReport:
    workspace_root: Path
    active_queue: QueueArtifact | None
    additional_artifacts: list[QueueArtifact] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def _resolve_path(value: str | Path, base: Path | None = None) -> Path:
    path = Path(value).expanduser()
    if not path.is_absolute() and base is not None:
        path = base / path
    return path.resolve()


def discover_queue(workspace_root: Path, explicit_queue_path: Path | None = None) -> QueueReport:
    workspace_root = workspace_root.resolve()
    if explicit_queue_path is not None:
        queue_path = _resolve_path(explicit_queue_path, workspace_root)
        if queue_path.exists():
            return QueueReport(
                workspace_root=workspace_root,
                active_queue=QueueArtifact(queue_path, "context-fallback" if not Path(explicit_queue_path).is_absolute() else "explicit-path", True),
            )
        return QueueReport(
            workspace_root=workspace_root,
            active_queue=None,
            warnings=[f"explicit queue path does not exist: {queue_path}"],
        )

    markdown_path = workspace_root / MARKDOWN_QUEUE
    json_path = workspace_root / JSON_QUEUE
    markdown_exists = markdown_path.exists()
    json_exists = json_path.exists()

    if markdown_exists:
        additional = [
            QueueArtifact(json_path.resolve(), "script-discovery-secondary", False),
        ] if json_exists else []
        return QueueReport(
            workspace_root=workspace_root,
            active_queue=QueueArtifact(markdown_path.resolve(), "script-discovery", True),
            additional_artifacts=additional,
        )

    if json_exists:
        return QueueReport(
            workspace_root=workspace_root,
            active_queue=QueueArtifact(json_path.resolve(), "script-discovery", True),
        )

    return QueueReport(workspace_root=workspace_root, active_queue=None)


def format_report(report: QueueReport) -> str:
    lines = ["# Queue Status", ""]
    lines.append(f"Workspace: {report.workspace_root}")
    if report.active_queue is None:
        lines.append("Queue: no initiated queue found")
    else:
        lines.append(f"Queue: {report.active_queue.path}")
        lines.append(f"Discovery: {report.active_queue.discovery_method}")
    if report.additional_artifacts:
        lines.append("")
        lines.append("Additional discovered queue artifacts:")
        for artifact in report.additional_artifacts:
            lines.append(f"- {artifact.path} ({artifact.discovery_method})")
    if report.warnings:
        lines.append("")
        lines.append("Warnings:")
        for warning in report.warnings:
            lines.append(f"- {warning}")
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Report workspace queue status without mutating queue state.")
    parser.add_argument(
        "--workspace-root",
        default=".",
        help="Workspace root to inspect. Defaults to the current directory.",
    )
    parser.add_argument(
        "--queue-path",
        default=None,
        help="Explicit queue path from user/context fallback.",
    )
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    workspace_root = _resolve_path(args.workspace_root)
    explicit_path = Path(args.queue_path) if args.queue_path else None
    report = discover_queue(workspace_root, explicit_path)
    print(format_report(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
