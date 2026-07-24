#!/usr/bin/env python3
"""Cross-platform Axolync notify CLI (stdlib only).

Positional contract (parity with the retired notify.ps1):

    notify.py <message> [channel|@botName] [taskNumber] [duration] [botName]

Behavior:
- Empty message exits 0 silently.
- A second arg starting with '@' sets the bot name instead of the channel.
- AXOLYNC_TASK_NUMBER supplies taskNumber when omitted; 'starting'/'finished'
  messages get a ' [task N]' suffix.
- AXOLYNC_NOTIFY_DURATION supplies duration when omitted; integer seconds are
  formatted as 'Xh Ym' / 'Xm' / 'Xs'.
- The message is prefixed with '<Bot>: ' unless it already carries a prefix.
- Plain-text UTF-8 POST to <baseUrl>/<channel>; unresolvable channel exits 0.

Per-setting resolution order (channel, baseUrl, botName):
  explicit CLI arg
  -> process env (AXOLYNC_NOTIFY_*)
  -> nearest ancestor .env (walking up from cwd)
  -> legacy notify-config.json (script dir, then ~/bin/notify-config.json)
  -> repo .env.template defaults (<script_dir>/../../.env.template)
  -> built-in defaults (https://ntfy.sh, bot 'Codex').
"""
from __future__ import annotations

import json
import os
import re
import sys
import urllib.request
from pathlib import Path

BUILTIN_BASE_URL = "https://ntfy.sh"
BUILTIN_BOT_NAME = "Codex"

ENV_KEYS = {
    "channel": "AXOLYNC_NOTIFY_CHANNEL",
    "baseUrl": "AXOLYNC_NOTIFY_BASE_URL",
    "botName": "AXOLYNC_NOTIFY_BOT_NAME",
}

_ENV_LINE = re.compile(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=(.*)$")
_PREFIX_GUARD = re.compile(r"^\s*[^:]{1,80}:\s")


def parse_dotenv_value(path: Path, key: str):
    """Return key's value from a .env-style file, or None (blank = unset)."""
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return None
    for line in lines:
        trimmed = line.strip()
        if not trimmed or trimmed.startswith("#"):
            continue
        m = _ENV_LINE.match(trimmed)
        if not m or m.group(1) != key:
            continue
        value = m.group(2).strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        return value or None
    return None


def ancestor_dotenv_value(start: Path, key: str):
    """Nearest-ancestor .env value for key, walking up from start."""
    current = start.resolve()
    while True:
        candidate = current / ".env"
        if candidate.is_file():
            value = parse_dotenv_value(candidate, key)
            if value:
                return value
        if current.parent == current:
            return None
        current = current.parent


def legacy_config_value(script_dir: Path, name: str):
    """Legacy notify-config.json lookup: script dir first, then ~/bin."""
    for candidate in (
        script_dir / "notify-config.json",
        Path.home() / "bin" / "notify-config.json",
    ):
        try:
            config = json.loads(candidate.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        value = str(config.get(name) or "").strip()
        if value:
            return value
    return None


def template_value(script_dir: Path, key: str):
    """Repo-root .env.template default (absent in deployed skill copies)."""
    template = script_dir.parent.parent / ".env.template"
    if template.is_file():
        return parse_dotenv_value(template, key)
    return None


def resolve_setting(name: str, explicit, script_dir: Path, cwd: Path):
    """Apply the full per-setting resolution chain."""
    if explicit and explicit.strip():
        return explicit.strip()
    env_key = ENV_KEYS[name]
    process = os.environ.get(env_key, "").strip()
    if process:
        return process
    dotenv = ancestor_dotenv_value(cwd, env_key)
    if dotenv:
        return dotenv
    legacy = legacy_config_value(script_dir, name)
    if legacy:
        return legacy
    template = template_value(script_dir, env_key)
    if template:
        return template
    return None


def format_duration(raw):
    if raw is None or not str(raw).strip():
        return None
    raw = str(raw).strip()
    if raw.isdigit():
        total = int(raw)
        hours, minutes, seconds = total // 3600, (total % 3600) // 60, total % 60
        if hours > 0:
            return f"{hours}h {minutes}m"
        if minutes > 0:
            return f"{minutes}m"
        return f"{seconds}s"
    return raw


def ensure_bot_prefix(body: str, bot: str) -> str:
    if _PREFIX_GUARD.match(body):
        return body
    return f"{bot}: {body}"


def post(url: str, body: str) -> None:
    """Isolated network call; tests stub this."""
    request = urllib.request.Request(
        url,
        data=body.encode("utf-8"),
        headers={"Content-Type": "text/plain; charset=utf-8"},
        method="POST",
    )
    with urllib.request.urlopen(request) as response:
        response.read()


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    message = argv[0] if len(argv) > 0 else ""
    channel = argv[1] if len(argv) > 1 else ""
    task_number = argv[2] if len(argv) > 2 else ""
    duration = argv[3] if len(argv) > 3 else ""
    bot_name = argv[4] if len(argv) > 4 else ""

    if not message.strip():
        return 0

    script_dir = Path(__file__).resolve().parent
    cwd = Path.cwd()

    if channel.startswith("@") and not bot_name.strip():
        bot_name = channel[1:].strip()
        channel = ""

    if not task_number.strip():
        task_number = os.environ.get("AXOLYNC_TASK_NUMBER", "")
    if task_number.strip() and message in ("starting", "finished"):
        message = f"{message} [task {task_number.strip()}]"

    if not duration.strip():
        duration = os.environ.get("AXOLYNC_NOTIFY_DURATION", "")
    duration_text = format_duration(duration)
    if duration_text:
        message = f"{message} | {duration_text}"

    resolved_channel = resolve_setting("channel", channel, script_dir, cwd)
    if not resolved_channel:
        return 0

    base_url = resolve_setting("baseUrl", "", script_dir, cwd) or BUILTIN_BASE_URL
    resolved_bot = resolve_setting("botName", bot_name, script_dir, cwd) or BUILTIN_BOT_NAME

    message = ensure_bot_prefix(message, resolved_bot)
    post(f"{base_url.rstrip('/')}/{resolved_channel}", message)
    return 0


if __name__ == "__main__":
    sys.exit(main())
