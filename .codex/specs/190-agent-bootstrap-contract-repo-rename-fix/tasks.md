# Tasks - Contract Repo Rename (Docs)

Derived from `requirements.md` and `design.md` in this spec folder.

- [x] 1. Update `bootstrap/axolync.vocabulary.md`: heading `Plugins Contract` -> `Contract`, broaden the meaning line, `Repo:` -> `axolync-contract`, add one stale `Aliases / older wording: Plugins Contract` line.
- [x] 2. Update `bootstrap/repo-summaries.md`: section heading `## axolync-plugins-contract` -> `## axolync-contract`.
- [x] 3. Update `bootstrap/axolync-builder.bootstrap-prompt.md`: clone-list `axolync-plugins-contract` -> `axolync-contract`.
- [x] 4. Verify `git grep -l axolync-plugins-contract -- bootstrap/*.md` returns nothing; commit and open the PR.
