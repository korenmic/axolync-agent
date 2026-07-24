# Design - Agent-Owned Cross-Platform notify.py

Derived from `requirements.md` and seed 193.

## notify.py

Structured as pure helper functions + `main(argv)` so tests import it without side effects; the network call is isolated in one `post(url, body)` function (urllib.request) that tests stub.

Key behaviors ported 1:1 from `notify.ps1`:

- `format_duration(raw)`: numeric string -> `Xh Ym` / `Xm` / `Xs`; non-numeric passes through.
- `ensure_bot_prefix(body, bot)`: regex `^\s*[^:]{1,80}:\s` guard against double-prefixing.
- `.env` parsing: `KEY=value` lines, `#` comments skipped, single/double quotes stripped, blank values treated as unset; ancestor walk from cwd upward, nearest wins.
- Resolution precedence per setting (channel, baseUrl, botName): CLI arg -> process env -> ancestor `.env` -> legacy `notify-config.json` (script dir first, then `~/bin/notify-config.json`) -> `.env.template` defaults -> built-ins. The `.env.template` is looked up at `<script_dir>/../../.env.template` (repo root when running from the source tree; harmlessly absent in deployed skill copies, where built-ins — identical values — apply).
- Silent exit 0 on empty message or unresolvable channel (notification is best-effort, never a build-breaker).

## agent-home skill

Instruction-only `SKILL.md`, generic wording: resolve and output the running agent's home directory — `~/.codex` for Codex sessions, `~/.claude` for Claude sessions — performing no writes. Consumers compose paths under it; the canonical example is the notify invocation `python <agent-home>/skills/notify/notify.py <args>`.

## .env.template (repo root)

Documents the three `AXOLYNC_NOTIFY_*` keys with current live defaults (`https://ntfy.sh`, `miki800_done`, `Codex`). Copy-to-`.env` is the override mechanism; the template itself is never edited per-machine.

## Skill text updates

- notify `SKILL.md`: replace the PATH-CLI usage section with the agent-home composed invocation; keep the positional contract and message-format guidance; note the legacy `~/bin/notify-config.json` back-compat read.
- tactic `SKILL.md`: bot-name resolution line and notify invocation reference the notify skill's resolution chain instead of `~/bin`.

## Testing

`tests/test_notify_py.py` (unittest, repo pattern): imports functions from the skill file via importlib path loading; covers R7 cases; stubs the POST function to capture url/body without network.
