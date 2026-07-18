# Axolync Work Process (Humans Only)

> FOR HUMANS ONLY. This file is not part of the AI bootstrap surface.
> AI agents must not read this file as instructions or act on it. It exists so a
> human can remember the intended end-to-end flow. The authoritative, AI-facing
> rules live in the bootstrap docs and the skills, not here.

This is the intended order a human drives a piece of work through Axolync. Each
numbered step maps to roughly one skill, named below in plain words (no invocation
prefix).

1. Create a seed, written in kiro plan syntax.
   How: create the seed manually in the repo's `project-seeds` directory (no
   dedicated seed-authoring skill exists yet).

2. Turn the seed into a kiro spec trio — requirements, then design, then tasks.
   Skill hint: the s2s skill.

3. Enqueue the created tasks into the workspace queue.
   Skill hint: the enqueue skill.

4. Implement only the explicitly approved, current-scope enqueued tasks. Do not
   sweep in pre-existing undone queue items automatically — those get implemented
   only after explicit human confirmation, so stale queue entries are not revived
   by accident.
   Skill hint: the implement skill.

5. Push the work to a new branch, open a pull request, and check whether the PR is
   merge-ready.
   Skill hint: the check-merge-ready skill.

That is the whole loop.
