from __future__ import annotations

import argparse
import re
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
class QueueRecord:
    qid: str
    status_raw: str
    classification: str
    task_label: str
    source_raw: str
    source_path: Path | None = None
    record_index: int = 0
    raw_excerpt: str = ""
    warnings: list[str] = field(default_factory=list)


@dataclass
class QueueParseResult:
    records: list[QueueRecord] = field(default_factory=list)
    parser_gaps: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


@dataclass
class QueueReport:
    workspace_root: Path
    active_queue: QueueArtifact | None
    additional_artifacts: list[QueueArtifact] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    parse_result: QueueParseResult | None = None


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


def _strip_markdown_ticks(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == "`" and value[-1] == "`":
        return value[1:-1].strip()
    return value


def _extract_markdown_link_target(value: str) -> str | None:
    match = re.search(r"\[[^\]]+\]\(([^)]+)\)", value)
    if match:
        return match.group(1).strip()
    return None


def _normalize_possible_path(raw: str, workspace_root: Path) -> Path:
    raw = _strip_markdown_ticks(raw)
    raw = raw.replace("\\", "/")
    if re.match(r"^/[A-Za-z]:/", raw):
        raw = raw[1:]
    path = Path(raw)
    if not path.is_absolute():
        path = workspace_root / path
    return path


def _classify_source(source_raw: str, workspace_root: Path) -> tuple[str, Path | None, str | None]:
    normalized_source = _strip_markdown_ticks(source_raw)
    link_target = _extract_markdown_link_target(source_raw)
    path_candidate = link_target or normalized_source
    if "tasks.md" in path_candidate.replace("\\", "/"):
        return "by-reference", _normalize_possible_path(path_candidate, workspace_root), None
    if normalized_source in {"inline procedural queue task", "by-value review task"}:
        return "by-value", None, None
    return "unrecognized", None, f"unrecognized source shape: {source_raw}"


def _extract_field(body: str, field_name: str) -> str | None:
    match = re.search(rf"(?m)^- {re.escape(field_name)}: (.+)$", body)
    return match.group(1).strip() if match else None


def _split_active_markdown_sections(text: str) -> tuple[str, str]:
    queued_match = re.search(r"(?m)^## Queued Items\s*$", text)
    if not queued_match:
        return "", text
    active_start = queued_match.end()
    next_section = re.search(r"(?m)^## (?!Queued Items\b).+$", text[active_start:])
    if not next_section:
        return text[active_start:], ""
    active_end = active_start + next_section.start()
    return text[active_start:active_end], text[active_end:]


def _parse_markdown_records(section_text: str, workspace_root: Path) -> tuple[list[QueueRecord], list[str]]:
    pieces = re.split(r"(?m)^### +(Q-\d+)\s*$", section_text)
    records: list[QueueRecord] = []
    gaps: list[str] = []
    for index in range(1, len(pieces), 2):
        qid = pieces[index].strip()
        body = pieces[index + 1]
        status_raw = _extract_field(body, "Status")
        source_raw = _extract_field(body, "Source")
        task_raw = _extract_field(body, "Task")
        record_gaps = []
        if not status_raw:
            record_gaps.append("missing status")
        if not source_raw:
            record_gaps.append("missing source")
        if not task_raw:
            record_gaps.append("missing task")
        classification = "unrecognized"
        source_path = None
        if source_raw:
            classification, source_path, source_gap = _classify_source(source_raw, workspace_root)
            if source_gap:
                record_gaps.append(source_gap)
        task_label = _strip_markdown_ticks(task_raw or "")
        records.append(
            QueueRecord(
                qid=qid,
                status_raw=_strip_markdown_ticks(status_raw or ""),
                classification=classification,
                task_label=task_label,
                source_raw=source_raw or "",
                source_path=source_path,
                record_index=len(records),
                raw_excerpt=body.strip()[:240],
                warnings=record_gaps,
            )
        )
        for gap in record_gaps:
            gaps.append(f"{qid}: {gap}")
    return records, gaps


def parse_markdown_queue(path: Path, workspace_root: Path) -> QueueParseResult:
    text = path.read_text(encoding="utf-8-sig", errors="replace")
    active_section, history_section = _split_active_markdown_sections(text)
    if not active_section:
        return QueueParseResult(parser_gaps=["missing active ## Queued Items section"])
    records, gaps = _parse_markdown_records(active_section, workspace_root)
    active_qids = {record.qid for record in records}
    history_qids = set(re.findall(r"(?m)^### +(Q-\d+)\s*$", history_section))
    duplicate_history_qids = sorted(active_qids.intersection(history_qids))
    warnings = [
        f"duplicate qids in non-active sections ignored for counts: {', '.join(duplicate_history_qids)}"
    ] if duplicate_history_qids else []
    return QueueParseResult(records=records, parser_gaps=gaps, warnings=warnings)


def parse_queue(artifact: QueueArtifact, workspace_root: Path) -> QueueParseResult:
    if artifact.path.suffix.lower() == ".md":
        return parse_markdown_queue(artifact.path, workspace_root)
    return QueueParseResult(parser_gaps=[f"unsupported queue format: {artifact.path.suffix or artifact.path.name}"])


def attach_parse_result(report: QueueReport) -> QueueReport:
    if report.active_queue is not None:
        report.parse_result = parse_queue(report.active_queue, report.workspace_root)
    return report


def _count_classifications(records: list[QueueRecord]) -> dict[str, int]:
    counts = {"by-reference": 0, "by-value": 0, "unrecognized": 0}
    for record in records:
        counts[record.classification] = counts.get(record.classification, 0) + 1
    return counts


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
    if report.parse_result is not None:
        records = report.parse_result.records
        class_counts = _count_classifications(records)
        lines.append("")
        lines.append("Counts:")
        lines.append(f"- Total records: {len(records)}")
        lines.append(f"- By-reference: {class_counts.get('by-reference', 0)}")
        lines.append(f"- By-value: {class_counts.get('by-value', 0)}")
        lines.append(f"- Unrecognized: {class_counts.get('unrecognized', 0)}")
        if report.parse_result.warnings:
            lines.append("")
            lines.append("Queue structure warnings:")
            for warning in report.parse_result.warnings:
                lines.append(f"- {warning}")
        if report.parse_result.parser_gaps:
            lines.append("")
            lines.append("Parser gaps:")
            for gap in report.parse_result.parser_gaps[:10]:
                lines.append(f"- {gap}")
            if len(report.parse_result.parser_gaps) > 10:
                lines.append(f"- ... {len(report.parse_result.parser_gaps) - 10} more")
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
    report = attach_parse_result(report)
    print(format_report(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
