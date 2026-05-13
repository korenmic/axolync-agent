---
name: seed-to-spec
description: "Convert one project seed or a group of seeds into Kiro-style requirements.md, design.md, and tasks.md. Use when the user invokes seed-to-spec, s2s, $s2s, asks for seed group to spec, open questions first, or deduplicated seed-question answering before spec generation."
---

# Seed To Spec

## Purpose

Turn one seed or a group of related seeds into polished spec files while preserving an explicit user-answering checkpoint for Open Questions.

Do not implement generated tasks. Stop after `tasks.md` is created and self-reviewed for the selected seed or seed group.

## Workflow

1. Resolve the seed or seed group from the user request.
2. Read each seed's Summary, Product Context, Technical Constraints, Open Questions, and any existing spec files.
3. Extract all Open Questions from all selected seeds.
4. Deduplicate repeated or equivalent questions across the selected seeds.
5. Analyze only the final questions that will be shown to the user. Identify question-local vocabulary that is defined only inside the seed/generated prompt context or is otherwise opaque without reading that context.
6. Before showing the first question, show a `Question Vocabulary` section explaining only those opaque terms or phrases used in the displayed questions.
7. Present each deduplicated question with recommended answers. Put the most recommended answer first, mark it clearly, and give every answer option a stable letter label.
8. For grouped seeds, show which seed(s) each question applies to.
9. Wait for user answers. Do not generate requirements/design/tasks until answers are provided or the user explicitly says to use recommended answers.
10. Apply each answer only to the relevant seed/question contexts where it matches. Do not broadcast an answer to unrelated seeds just because the wording is similar.
11. Harden the seed(s) with the resolved answers before generating spec files.
12. Generate `requirements.md`, then self-review it against the seed(s), resolved answers, and project constraints. Fix gaps and repeat review/fix cycles until no material gaps remain.
13. Generate `design.md`, then self-review it against the seed(s), resolved answers, and final `requirements.md`. Fix gaps and repeat review/fix cycles until no material gaps remain.
14. Generate `tasks.md`, then self-review it against the seed(s), resolved answers, final `requirements.md`, and final `design.md`. Fix gaps and repeat review/fix cycles until no material gaps remain.
15. Pause after all requested `tasks.md` files are created. Do not implement tasks unless the user gives a separate implementation request.

## Question Vocabulary Rules

Include a term in `Question Vocabulary` only when all are true:

- The term or phrase appears in one or more Open Questions shown to the user.
- The term is seed-local, project-local, newly coined, or likely opaque without reading the seed.
- The term can be defined from the seed context or clearly labeled as inferred.

Do not include generic words, obvious repo names, or terms not used in the displayed questions.

Use this format:

```markdown
## Question Vocabulary

- `term`: Short definition. Source: seed section or inferred from seed context. Used in Q1/Q3.
- `ambiguous term`: Undefined or ambiguous in the seed. Treat this as part of the question before answering. Used in Q2.
```

Do not invent a definition when the seed is ambiguous. State the ambiguity clearly.

## Question Format

Use this format for the interactive question pass:

```markdown
## Open Questions

### Q1. Question text
Applies to: `seed-a`, `seed-b`

Recommended answers:
A. Recommended: concise answer and why it is preferred.
B. Alternative: concise answer and tradeoff.
C. Alternative: concise answer and tradeoff.
```

Answer-option labels must be persistent within the pass:

- Use `A.`, `B.`, `C.` and continue alphabetically when more options are needed.
- Put each answer option on its own line.
- Do not renumber or relabel options after the user answers.
- Accept user replies by letter, exact answer text, or free form.

When the user answers in free form, normalize the answer into concrete seed/spec decisions before hardening files.

## Spec Generation Rules

- Keep generated specs grounded in the seed and resolved answers.
- Preserve product intent over literal wording when prior seed wording conflicts with explicit user answers.
- Keep requirements behavioral and testable.
- Keep design technical enough to implement without guessing ownership boundaries.
- Keep tasks implementation-ready, ordered, and scoped so a coding agent can execute them.
- If a group of seeds shares answers, duplicate or specialize the answer only where it is contextually relevant.
- If an answer creates a new open question, pause and ask before generating downstream spec files.

## Completion Response

Report the created or updated spec file paths and state that execution is paused after `tasks.md`.
