from __future__ import annotations

import argparse
from dataclasses import dataclass
from typing import Iterable


DEFAULT_QUEUE_TARGET = "current workspace undone enqueued tasks"


@dataclass(frozen=True)
class ImplementPlan:
    task_source: str
    tactic_arguments: tuple[str, ...]
    uses_default_queue: bool


def resolve_implement_plan(tactic_arguments: Iterable[str] | None = None) -> ImplementPlan:
    arguments = tuple(arg for arg in (tactic_arguments or ()) if arg)
    return ImplementPlan(
        task_source=" ".join(arguments) if arguments else DEFAULT_QUEUE_TARGET,
        tactic_arguments=arguments,
        uses_default_queue=not arguments,
    )


def format_tactic_handoff(plan: ImplementPlan) -> str:
    if plan.uses_default_queue:
        return "Run $tactic over the current workspace undone enqueued tasks."
    return f"Run $tactic with forwarded arguments: {' '.join(plan.tactic_arguments)}"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Describe an $implement wrapper handoff to $tactic.")
    parser.add_argument(
        "tactic_arguments",
        nargs="*",
        help="Arguments to forward unchanged to $tactic. Omit to use undone enqueued tasks.",
    )
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    plan = resolve_implement_plan(args.tactic_arguments)
    print(format_tactic_handoff(plan))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

