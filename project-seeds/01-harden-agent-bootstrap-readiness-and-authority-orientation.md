# Harden Agent Bootstrap Readiness And Authority Orientation

## Summary

Improve the Axolync agent bootstrap surface so a fresh agent can become useful quickly without over-reading the repos, while still internalizing the critical operational boundaries before it acts.

The bootstrap is already useful, but it should be hardened with a checklist-oriented readiness pass and clearer authority wording. The goal is not to create rigid agent roles. Any agent may implement, review, or build inside its own workspace. The goal is to make all agents safer and faster by making the non-negotiable invariants explicit.

## Product Context

Axolync work commonly spans multiple sibling repos and multiple Sinq workspaces. A new agent needs enough orientation to:

- understand the repo authority model
- find the current product/runtime authority docs
- avoid reading the entire tree before acting
- avoid modifying or building in another agent's workspace
- discover machine-local artifact mirror destinations from builder env/config/report flow instead of assuming a fixed drive letter or sharing protocol
- know when dispatch/proxy handoff is required

The bootstrap docs should remain short enough to be read at session start and should not turn into a full duplicate of repo documentation.

## Technical Constraints

- Do not hard-code this machine's mirror drive or path in bootstrap authority docs. Mirror destinations are environment/config/report-flow authority, not Axolync product truth.
- Do not encode fixed roles such as "native author" or "build authority" as universal bootstrap tracks. Responsibilities are contextual and may emerge per task.
- Preserve the universal workspace boundary rule: agents may modify source and run builds only inside their own workspace; cross-workspace manipulation must happen through dispatch/proxy, except explicitly allowed root handoff files such as `CRPR.md` or result markdown files.
- Prefer a checklist over a script for readiness because environment/tooling drift can make a script stale. If a future script is added, it must be treated as maintained tooling with tests.
- Keep the bootstrap reading path concise and authority-based.

## Proposed Scope

1. Add an "Am I Ready?" checklist to the bootstrap docs.
   - Current workspace root confirmed.
   - Workspace `AGENTS.md` and command protocol read.
   - Shell/RTK/Git editor constraints understood.
   - Sibling repos present or bootstrap path known.
   - Active task source identified.
   - No foreign workspace writes/builds planned.
   - Mirror destination will be discovered from current builder env/config/report flow.
   - Minimal meaningful verification path identified before edits.

2. Clarify mirror destination authority.
   - Replace any wording that implies a fixed drive/path with wording that mirror targets are machine-local and must be discovered at runtime.

3. Strengthen universal workspace boundary guidance.
   - State that all source edits and builds happen in the receiving agent's own workspace.
   - State that another workspace is read-only evidence unless dispatch explicitly authorizes a root-level handoff file.

4. Add an optional reviewer quick path, not a role taxonomy.
   - How to locate PR branch context, specs/tasks, changed code, and tests.
   - How to write actionable CRPR without over-reading.

5. Add a compact product/repo authority map.
   - Browser owns orchestration/runtime behavior.
   - Contracts own API/schema compatibility.
   - Builder owns artifact/build/report truth.
   - Wrappers host packaged browser/addon payloads.
   - Addons own provider behavior and addon-owned native payload behavior.

6. Park a future investigation for repo knowledge RAG/MCP.
   - Explore a maintained local knowledge index that can answer "what owns this behavior?" and "where is the authority doc?" without each agent rediscovering repo topology.

## Open Questions

- Should the readiness checklist live in `axolync-builder.bootstrap.md`, `recommended-reading.md`, or a new short `readiness-checklist.md` linked from both?
- What is the smallest reviewer quick path that materially helps CRPR reviews without encouraging shallow review?
- Should the product/repo authority map be a new standalone bootstrap doc or a section inside `repo-summaries.md`?
- What source set should a future RAG/MCP repo knowledge index treat as authoritative, and how should it avoid stale indexed summaries?
