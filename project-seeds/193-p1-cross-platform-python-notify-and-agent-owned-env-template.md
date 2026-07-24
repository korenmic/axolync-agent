# Seed 193: Unify notify CLI Into Agent-Owned Cross-Platform `notify.py` + `.env.template`

Priority: P1
Repo: axolync-agent

## Summary

Unify the two divergent notify CLI implementations (`~/bin/notify.ps1` for Windows, `~/bin/notify.sh` for POSIX) into a single cross-platform Python `notify.py` owned by this repo at `skills-user/notify/`, deployed ONLY into the agent userspace skill folders (`~/.codex/skills/notify/`, `~/.claude/skills/notify/`) — no `~/bin` involvement at all. Callers (TACTIC included) invoke it by full path, composed from a new small helper skill (`agent-home`) that returns the running agent's home directory (`~/.codex` or `~/.claude`). Also add a single `.env.template` in the agent repo holding the notify default settings. Parked: approved as a seed, not scheduled for implementation yet.

## Product Context

Today the notify CLI is owned by `~/bin` (its own git repo) and resolves through PATH (`notify` -> `notify.cmd` -> `notify.ps1`; plus a separate `notify.sh`). The skill folders carry only instructions, except stale vestigial `notify.ps1` copies: the agent-repo copy is a month behind the live `~/bin` one (Apr 11 vs May 8) — proof the duplication drifts. Cross-platform coverage exists only by maintaining two parallel implementations that can and do diverge.

After this seed, the agent repo is the single source of truth and the userspace skill folders are the only deployment target. There is no PATH shim and no `~/bin` copy: the one script ships inside the notify skill folder, and every caller resolves it as `<agent-home>/skills/notify/notify.py`, where `<agent-home>` comes from the `agent-home` helper skill. Both agents run the same script from their own skill copy; copies are overwritten idempotently from the one source on redeploy (seed 194 deploy flow), so duplication carries no drift risk.

## Technical Constraints

- `notify.py` lives at `skills-user/notify/notify.py`, Python standard library only (Windows/macOS/Linux), preserving the existing positional CLI contract: message, channel or `@name`, taskNumber, duration, botName; bot-name prefixing; ntfy POST to the resolved base URL/channel.
- Deployment target is ONLY the agent userspace skill folders: `~/.codex/skills/notify/notify.py` and `~/.claude/skills/notify/notify.py`, installed by copying the notify skill folder (seed 194 deploy flow). No `~/bin` shim, no PATH-name dependency; `~/bin/notify.ps1`, `~/bin/notify.cmd`, and `~/bin/notify.sh` are retired after parity.
- Add a new helper skill `agent-home` (Codex-first `$agent-home`, claudified `/agent-home`) whose single job is returning the running agent's home path: `~/.codex` when running under Codex, `~/.claude` when running under Claude. It performs no writes.
- Invocation contract for all callers: resolve `<agent-home>` via the `agent-home` skill, then run `python <agent-home>/skills/notify/notify.py <args>`. Update the notify `SKILL.md` and TACTIC's notify instructions (and any other skill text that invokes the bare `notify` PATH name) to use this composed full path.
- Config resolution order, with no `~/bin/notify-config.json` requirement: explicit CLI arg -> process env (`AXOLYNC_NOTIFY_*`) -> nearest ancestor `.env` -> agent-repo `.env.template` defaults -> built-in defaults. Reading a legacy `~/bin/notify-config.json` if present is allowed for back-compat during transition.
- Add a single `.env.template` in the agent repo (root or `bootstrap/`) with `AXOLYNC_NOTIFY_BASE_URL`, `AXOLYNC_NOTIFY_CHANNEL`, `AXOLYNC_NOTIFY_BOT_NAME` defaults matching current builder/browser usage.
- Remove the stale vestigial `notify.ps1` copies from the skill folders as part of parity cleanup.
- Update the notify `SKILL.md` to document `notify.py` as the only implementation and the `agent-home` composition as the only invocation path.

## Non-Goals

- Retiring the notify `.env` values in other repos (builder/browser). That is a separate future seed once the agent-owned template is the single source of truth.
- Renaming the `AXOLYNC_NOTIFY_*` env prefix to a neutral one.

## Open Questions

None — resolved: stdlib `urllib` only (zero-dependency portability); `agent-home` is worded as a generic reusable primitive, not notify-scoped.
