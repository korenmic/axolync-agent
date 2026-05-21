from __future__ import annotations

import argparse
import json
import sys
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Any


DEFAULT_PATTERN = "axolync-debug-*.zip"


def default_downloads_dir() -> Path:
    return Path.home() / "Downloads"


def find_candidates(downloads_dir: Path, pattern: str = DEFAULT_PATTERN) -> list[Path]:
    if not downloads_dir.exists() or not downloads_dir.is_dir():
        return []
    return sorted(path for path in downloads_dir.glob(pattern) if path.is_file())


def latest_debug_zip(downloads_dir: Path, pattern: str = DEFAULT_PATTERN) -> Path | None:
    candidates = find_candidates(downloads_dir, pattern)
    if not candidates:
        return None
    return max(candidates, key=lambda path: (path.stat().st_mtime_ns, path.name))


def _iso_from_timestamp(timestamp: float) -> str:
    return datetime.fromtimestamp(timestamp).astimezone().isoformat(timespec="seconds")


def summarize_zip(path: Path, entry_limit: int) -> dict[str, Any]:
    with zipfile.ZipFile(path) as archive:
        entries = archive.infolist()
        preview = [
            {
                "path": entry.filename,
                "compressed_size": entry.compress_size,
                "size": entry.file_size,
            }
            for entry in entries[:entry_limit]
        ]
        return {
            "entry_count": len(entries),
            "uncompressed_size": sum(entry.file_size for entry in entries),
            "preview": preview,
        }


def build_payload(path: Path, entry_limit: int) -> dict[str, Any]:
    stat = path.stat()
    payload: dict[str, Any] = {
        "path": str(path.resolve()),
        "name": path.name,
        "size": stat.st_size,
        "modified": _iso_from_timestamp(stat.st_mtime),
    }
    try:
        payload["zip"] = summarize_zip(path, entry_limit)
    except zipfile.BadZipFile as error:
        payload["zip_error"] = f"bad zip file: {error}"
    return payload


def format_text(payload: dict[str, Any]) -> str:
    lines = [
        "Latest Axolync debug ZIP:",
        f"path: {payload['path']}",
        f"name: {payload['name']}",
        f"size_bytes: {payload['size']}",
        f"modified: {payload['modified']}",
    ]
    zip_summary = payload.get("zip")
    if isinstance(zip_summary, dict):
        lines.extend(
            [
                f"zip_entries: {zip_summary['entry_count']}",
                f"zip_uncompressed_size_bytes: {zip_summary['uncompressed_size']}",
            ]
        )
        preview = zip_summary.get("preview") or []
        if preview:
            lines.append("entry_preview:")
            lines.extend(f"- {entry['path']} ({entry['size']} bytes)" for entry in preview)
    elif payload.get("zip_error"):
        lines.append(f"zip_error: {payload['zip_error']}")
    return "\n".join(lines)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Find the latest ~/Downloads/axolync-debug-*.zip file.")
    parser.add_argument("--downloads-dir", default=str(default_downloads_dir()))
    parser.add_argument("--pattern", default=DEFAULT_PATTERN)
    parser.add_argument("--entry-limit", type=int, default=25)
    parser.add_argument("--json", action="store_true", dest="as_json")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    downloads_dir = Path(args.downloads_dir).expanduser()
    latest = latest_debug_zip(downloads_dir, args.pattern)
    if latest is None:
        message = f"No {args.pattern} files found in {downloads_dir.resolve()}."
        if args.as_json:
            print(json.dumps({"found": False, "downloads_dir": str(downloads_dir.resolve()), "pattern": args.pattern}))
        else:
            print(message)
        return 1

    payload = build_payload(latest, max(0, args.entry_limit))
    payload["found"] = True
    if args.as_json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(format_text(payload))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
