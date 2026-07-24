# Requirements - Agent-Owned Cross-Platform notify.py

Derived from seed 193 (`project-seeds/193-p1-cross-platform-python-notify-and-agent-owned-env-template.md`).

## R1. Single cross-platform implementation
`skills-user/notify/notify.py` exists, Python 3 standard library only (urllib for the POST), runs on Windows/macOS/Linux, and is the only notify implementation in the repo (the vestigial `skills-user/notify/notify.ps1` is removed).

## R2. CLI contract preserved
Positional args exactly as today: `message [channel|@botName] [taskNumber] [duration] [botName]`. Behavior parity with `notify.ps1`: empty message exits 0 silently; `@name` second arg sets bot name; `AXOLYNC_TASK_NUMBER` fallback and `[task N]` suffix for `starting`/`finished`; `AXOLYNC_NOTIFY_DURATION` fallback with seconds formatted to `Xh Ym`/`Xm`/`Xs`; bot-name prefix added unless the message already starts with a `Name: ` prefix; plain-text UTF-8 POST to `<baseUrl>/<channel>`; missing channel exits 0 silently.

## R3. Config resolution order
Explicit CLI arg -> process env (`AXOLYNC_NOTIFY_*`) -> nearest ancestor `.env` (walking up from cwd) -> legacy `notify-config.json` (script dir, then `~/bin/notify-config.json`) -> repo `.env.template` defaults -> built-in defaults (`https://ntfy.sh`, `Codex`). No hard dependency on `~/bin`.

## R4. agent-home helper skill
`skills-user/agent-home/SKILL.md` exists as a generic read-only primitive: it resolves the running agent's home directory (`~/.codex` under Codex, `~/.claude` under Claude) for any skill needing per-agent paths. Notify invocation composes it: `python <agent-home>/skills/notify/notify.py <args>`.

## R5. Agent-owned .env.template
A single `.env.template` at the agent repo root documents `AXOLYNC_NOTIFY_BASE_URL`, `AXOLYNC_NOTIFY_CHANNEL`, `AXOLYNC_NOTIFY_BOT_NAME` with the current live defaults.

## R6. Skill texts updated
The notify `SKILL.md` documents `notify.py` as the only implementation and the agent-home composition as the invocation path; the tactic `SKILL.md` notify instructions no longer reference `~/bin` as the resolution authority.

## R7. Tested
`tests/test_notify_py.py` covers duration formatting, bot-prefix logic, `@name` parsing, `.env` parsing/ancestor resolution, resolution precedence, and silent-exit cases, without network access.
