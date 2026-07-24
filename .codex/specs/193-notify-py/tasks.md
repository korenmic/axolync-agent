# Tasks - Agent-Owned Cross-Platform notify.py

Derived from `requirements.md` and `design.md` in this spec folder.

- [ ] 1. Add `skills-user/notify/notify.py`: stdlib-only cross-platform CLI with full `notify.ps1` parity (positional contract, `@name`, task-number/duration handling, bot-prefix guard, silent exits) and the layered resolution chain (env -> ancestor `.env` -> legacy `notify-config.json` -> `.env.template` -> built-ins).
- [ ] 2. Add `skills-user/agent-home/SKILL.md`: generic read-only resolver of the running agent's home directory (`~/.codex` / `~/.claude`).
- [ ] 3. Add root `.env.template` with the three `AXOLYNC_NOTIFY_*` defaults.
- [ ] 4. Update `skills-user/notify/SKILL.md` to the notify.py + agent-home invocation model and remove the vestigial `skills-user/notify/notify.ps1`.
- [ ] 5. Update `skills-user/tactic/SKILL.md` notify references to drop `~/bin` as resolution authority.
- [ ] 6. Add `tests/test_notify_py.py` covering duration formatting, prefix guard, `@name` parsing, `.env` parsing/ancestors, precedence, and silent-exit cases (no network).
