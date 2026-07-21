# Seed 193: Cross-Platform Python notify CLI + Agent-Owned notify .env.template

Priority: P1
Repo: axolync-agent

## Summary

Reimplement the `notify` skill's CLI as a cross-platform Python (`notify.py`) that replaces the Windows-only `notify.ps1`, and add a single `.env.template` in the agent repo holding the notify default settings currently duplicated across builder/browser. The notify concept is repo-agnostic, so the agent repo should own its one canonical config template.

## Product Context

The `notify` skill ships `notify.ps1` (PowerShell), which only runs on Windows and will not work on macOS/Linux (e.g. a new Mac). Its config is resolved from `~/bin/notify-config.json` and `AXOLYNC_NOTIFY_*` env vars spread across repos. Notify has nothing to do with browser or builder specifically; it is generic infrastructure. Consolidating a cross-platform implementation plus one config template into the agent repo makes the skill redeployable on any OS with just Python installed.

## Technical Constraints

- Add `skills-user/notify/notify.py` using only the Python standard library (cross-platform: Windows/macOS/Linux). It must match `notify.ps1` behavior: positional args (message, channel or `@name`, taskNumber, duration, botName), bot-name prefixing, and the ntfy POST to the resolved base URL/channel.
- Config resolution order, with no dependency on `~/bin`: explicit CLI arg -> process env (`AXOLYNC_NOTIFY_*`) -> nearest ancestor `.env` -> repo-local `.env.template` defaults -> built-in default (`Codex`, `ntfy.sh`, existing channel).
- Add a single `.env.template` at the agent repo (root or `bootstrap/`) with the notify default keys (`AXOLYNC_NOTIFY_BASE_URL`, `AXOLYNC_NOTIFY_CHANNEL`, `AXOLYNC_NOTIFY_BOT_NAME`) using the values currently used by builder/browser.
- Keep `notify.ps1` as an optional Windows shim during transition; do not break existing callers or the positional CLI contract.
- Update the notify `SKILL.md` to document `notify.py` as the cross-platform entry.

## Non-Goals

- Retiring the notify `.env`/config in other repos (builder/browser). That is a separate future seed once the agent-owned template is the single source of truth.
- Renaming the `AXOLYNC_NOTIFY_*` env prefix to a neutral one (tracked separately).

## Open Questions

- Retire `notify.ps1` immediately, or keep it as a Windows shim until `notify.py` parity is confirmed? Recommended: keep the shim, retire in a follow-up.
- Use stdlib `urllib` only for the POST, or allow `requests` if present? Recommended: stdlib `urllib` only, for zero-dependency portability.
