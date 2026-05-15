from __future__ import annotations

import argparse
import json
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
    status_bucket: str
    classification: str
    task_label: str
    source_raw: str
    source_path: Path | None = None
    source_exists: bool | None = None
    source_status_bucket: str | None = None
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


def normalize_status(value: str) -> str:
    normalized = value.strip().strip("`").strip().lower().replace("-", "_")
    if normalized in {"done", "completed"}:
        return "done"
    if normalized == "queued":
        return "ready"
    if normalized == "in_progress":
        return "active"
    if normalized == "blocked":
        return "blocked"
    if normalized == "skipped":
        return "skipped"
    return "unrecognized_status"


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


def _normalize_task_text(value: str) -> str:
    value = value.strip().strip("`").strip()
    value = re.sub(r"^\s*[-*]\s+\[[ xX]\]\s*", "", value)
    value = re.sub(r"^\s*\d+\.\s*", "", value)
    value = re.sub(r"\s+", " ", value)
    return value.rstrip(".").lower()


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
                status_bucket=normalize_status(status_raw or ""),
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


def _find_referenced_task_status(source_path: Path, task_label: str) -> str | None:
    if not source_path.exists():
        return None
    wanted = _normalize_task_text(task_label)
    if not wanted:
        return None
    try:
        lines = source_path.read_text(encoding="utf-8-sig", errors="replace").splitlines()
    except OSError:
        return None
    for line in lines:
        match = re.match(r"^\s*[-*]\s+\[([ xX])\]\s+(.+)$", line)
        if not match:
            continue
        line_text = _normalize_task_text(match.group(2))
        if line_text == wanted or wanted in line_text or line_text in wanted:
            return "done" if match.group(1).lower() == "x" else "ready"
    return None


def parse_json_queue(path: Path, workspace_root: Path) -> QueueParseResult:
    try:
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as error:
        return QueueParseResult(parser_gaps=[f"invalid JSON queue: {error}"])
    if not isinstance(payload, dict):
        return QueueParseResult(parser_gaps=["JSON queue root must be an object"])
    items = payload.get("items")
    if not isinstance(items, list):
        return QueueParseResult(parser_gaps=["JSON queue must contain an items array"])

    records: list[QueueRecord] = []
    gaps: list[str] = []
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            gaps.append(f"record {index}: item must be an object")
            records.append(
                QueueRecord(
                    qid=f"record-{index}",
                    status_raw="",
                    status_bucket="unrecognized_status",
                    classification="unrecognized",
                    task_label="",
                    source_raw="",
                    record_index=index,
                    raw_excerpt=str(item)[:240],
                    warnings=["item must be an object"],
                )
            )
            continue
        qid = str(item.get("queue_id") or f"record-{index}")
        status_raw = str(item.get("status") or "")
        source_raw = str(item.get("source_file_path") or "")
        task_label = str(item.get("referenced_task_title") or "")
        record_gaps = []
        if "queue_id" not in item:
            record_gaps.append("missing queue_id")
        if not status_raw:
            record_gaps.append("missing status")
        if not source_raw:
            record_gaps.append("missing source_file_path")
        if not task_label:
            record_gaps.append("missing referenced_task_title")
        classification = "by-reference" if not record_gaps else "unrecognized"
        source_path = _normalize_possible_path(source_raw, workspace_root) if source_raw else None
        records.append(
            QueueRecord(
                qid=qid,
                status_raw=_strip_markdown_ticks(status_raw),
                status_bucket=normalize_status(status_raw),
                classification=classification,
                task_label=task_label,
                source_raw=source_raw,
                source_path=source_path,
                record_index=index,
                raw_excerpt=json.dumps(item, ensure_ascii=False)[:240],
                warnings=record_gaps,
            )
        )
        for gap in record_gaps:
            gaps.append(f"{qid}: {gap}")
    return QueueParseResult(records=records, parser_gaps=gaps)


def parse_queue(artifact: QueueArtifact, workspace_root: Path) -> QueueParseResult:
    if artifact.path.suffix.lower() == ".md":
        return parse_markdown_queue(artifact.path, workspace_root)
    if artifact.path.suffix.lower() == ".json":
        return parse_json_queue(artifact.path, workspace_root)
    return QueueParseResult(parser_gaps=[f"unsupported queue format: {artifact.path.suffix or artifact.path.name}"])


def add_reference_diagnostics(parse_result: QueueParseResult) -> QueueParseResult:
    for record in parse_result.records:
        if record.classification != "by-reference" or record.source_path is None:
            continue
        record.source_exists = record.source_path.exists()
        if not record.source_exists:
            record.warnings.append(f"missing referenced source: {record.source_path}")
            continue
        record.source_status_bucket = _find_referenced_task_status(record.source_path, record.task_label)
        if record.source_status_bucket and record.source_status_bucket != record.status_bucket:
            record.warnings.append(
                f"queue/source status drift: queue={record.status_bucket} source={record.source_status_bucket}"
            )
    return parse_result


def attach_parse_result(report: QueueReport) -> QueueReport:
    if report.active_queue is not None:
        report.parse_result = add_reference_diagnostics(parse_queue(report.active_queue, report.workspace_root))
    return report


def _count_classifications(records: list[QueueRecord]) -> dict[str, int]:
    counts = {"by-reference": 0, "by-value": 0, "unrecognized": 0}
    for record in records:
        counts[record.classification] = counts.get(record.classification, 0) + 1
    return counts


def _count_statuses(records: list[QueueRecord]) -> dict[str, int]:
    counts = {
        "done": 0,
        "ready": 0,
        "active": 0,
        "blocked": 0,
        "skipped": 0,
        "unrecognized_status": 0,
        "undone_total": 0,
    }
    for record in records:
        counts[record.status_bucket] = counts.get(record.status_bucket, 0) + 1
        if record.status_bucket in {"ready", "active", "blocked", "unrecognized_status"}:
            counts["undone_total"] += 1
    return counts


def _unknown_status_gaps(records: list[QueueRecord]) -> list[str]:
    return [
        f"{record.qid}: unrecognized status {record.status_raw!r}"
        for record in records
        if record.status_bucket == "unrecognized_status"
    ]


def _reference_diagnostics(records: list[QueueRecord]) -> tuple[list[QueueRecord], list[QueueRecord]]:
    missing = [
        record
        for record in records
        if record.classification == "by-reference" and record.source_exists is False
    ]
    drift = [
        record
        for record in records
        if record.classification == "by-reference"
        and record.source_status_bucket is not None
        and record.source_status_bucket != record.status_bucket
    ]
    return missing, drift


def _record_warning_gaps(records: list[QueueRecord]) -> list[str]:
    gaps = []
    for record in records:
        for warning in record.warnings:
            if warning.startswith("missing referenced source:"):
                continue
            if warning.startswith("queue/source status drift:"):
                continue
            gaps.append(f"{record.qid}: {warning}; excerpt={record.raw_excerpt!r}")
    return gaps


def _undone_records(records: list[QueueRecord]) -> list[QueueRecord]:
    return [
        record
        for record in records
        if record.status_bucket in {"ready", "active", "blocked", "unrecognized_status"}
    ]


def _compact_task_label(value: str, max_length: int = 96) -> str:
    value = re.sub(r"\s+", " ", value).strip()
    if len(value) <= max_length:
        return value
    return f"{value[:max_length - 1].rstrip()}..."


def _format_undone_summary(record: QueueRecord) -> str:
    return (
        f"- {record.qid}: {record.status_bucket}; {record.classification}; "
        f"{_compact_task_label(record.task_label)}"
    )


def format_report(report: QueueReport, verbose: bool = False) -> str:
    lines = ["# Queue Status", ""]
    lines.append("Queue source:")
    lines.append(f"Workspace: {report.workspace_root}")
    if report.active_queue is None:
        lines.append("Queue: no initiated queue found")
        if report.warnings:
            lines.append("")
            lines.append("Warnings:")
            for warning in report.warnings:
                lines.append(f"- {warning}")
        return "\n".join(lines)
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
        status_counts = _count_statuses(records)
        lines.append("")
        lines.append("Status counts:")
        lines.append(f"- Total records: {len(records)}")
        lines.append(f"- Done: {status_counts.get('done', 0)}")
        lines.append(f"- Undone: {status_counts.get('undone_total', 0)}")
        lines.append(f"- Ready: {status_counts.get('ready', 0)}")
        lines.append(f"- Active: {status_counts.get('active', 0)}")
        lines.append(f"- Blocked: {status_counts.get('blocked', 0)}")
        lines.append(f"- Skipped: {status_counts.get('skipped', 0)}")
        lines.append(f"- Unknown status: {status_counts.get('unrecognized_status', 0)}")
        lines.append("")
        lines.append("Classification counts:")
        lines.append(f"- By-reference: {class_counts.get('by-reference', 0)}")
        lines.append(f"- By-value: {class_counts.get('by-value', 0)}")
        lines.append(f"- Unrecognized: {class_counts.get('unrecognized', 0)}")
        missing_refs, drift_refs = _reference_diagnostics(records)
        lines.append("")
        lines.append("Reference diagnostics:")
        lines.append(f"- Missing references: {len(missing_refs)}")
        lines.append(f"- Queue/source drift: {len(drift_refs)}")
        if missing_refs:
            sample = ", ".join(record.qid for record in missing_refs[:8])
            lines.append(f"- Missing reference sample: {sample}")
        if drift_refs:
            sample = ", ".join(record.qid for record in drift_refs[:8])
            lines.append(f"- Drift sample: {sample}")
        for gap in _unknown_status_gaps(records):
            if gap not in report.parse_result.parser_gaps:
                report.parse_result.parser_gaps.append(gap)
        for gap in _record_warning_gaps(records):
            if gap not in report.parse_result.parser_gaps:
                report.parse_result.parser_gaps.append(gap)
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
        lines.append("")
        lines.append(f"Undone: {status_counts.get('undone_total', 0)}")
        if verbose:
            lines.append("Undone records:")
            undone_records = _undone_records(records)
            if not undone_records:
                lines.append("- None")
            else:
                for record in undone_records:
                    lines.append(_format_undone_summary(record))
    if report.warnings:
        lines.append("")
        lines.append("Warnings:")
        for warning in report.warnings:
            lines.append(f"- {warning}")
    return "\n".join(lines)


def build_report(workspace_root: Path, explicit_path: Path | None = None) -> QueueReport:
    return attach_parse_result(discover_queue(workspace_root, explicit_path))


def known_sinq_roots(workspace_root: Path) -> list[Path]:
    parent = workspace_root.resolve().parent
    return [parent / name for name in ("Sinq", "Sinq2", "Sinq3", "Sinq4") if (parent / name).exists()]


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
    parser.add_argument(
        "--diagnose-known-sinq-roots",
        action="store_true",
        help="Read-only diagnostic mode for sibling Sinq/Sinq2/Sinq3/Sinq4 workspaces.",
    )
    parser.add_argument(
        "verbosity",
        nargs="?",
        choices=["verbose"],
        help="Print compact summaries for each enqueued undone record.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print compact summaries for each enqueued undone record.",
    )
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    workspace_root = _resolve_path(args.workspace_root)
    explicit_path = Path(args.queue_path) if args.queue_path else None
    if args.diagnose_known_sinq_roots:
        reports = [build_report(root) for root in known_sinq_roots(workspace_root)]
        if not reports:
            reports = [QueueReport(workspace_root=workspace_root, active_queue=None, warnings=["no known sibling Sinq roots found"])]
        print("\n\n---\n\n".join(format_report(report, verbose=args.verbose or args.verbosity == "verbose") for report in reports))
        return 0
    report = build_report(workspace_root, explicit_path)
    print(format_report(report, verbose=args.verbose or args.verbosity == "verbose"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
