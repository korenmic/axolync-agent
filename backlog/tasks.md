# Axolync Agent Backlog

- [x] Harden dispatch build/CR handoff skills with delayed checkout restoration.
  - Dispatch-driven PR branch checkouts in the primary workspace must be recorded as temporary dispatch state, including the previous branch/commit per affected repo.
  - Do not restore immediately at dispatch completion because follow-up dispatches may continue the same PR group.
  - At the start of the next unrelated request, restore repos touched only for the previous dispatch back to their prior branch, normally `master`, after confirming there are no uncommitted source changes to preserve.
  - Generated build residue must be stashed or cleaned according to repo policy before restoration, never silently discarded.
  - The handoff flow should report any restoration it performs and any repo it refuses to restore because local changes require operator attention.
