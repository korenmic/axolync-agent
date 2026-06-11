from __future__ import annotations

import argparse
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


DEFAULT_QUEUE_TARGET = "current workspace undone enqueued tasks"
IMPLEMENT_NOTIFY_EVENTS = (
    "implementation-start",
    "tactic-task-start",
    "tactic-task-progress",
    "tactic-task-done",
    "tactic-blocked",
    "tactic-finished",
    "push-complete",
)
PASSING_CHECK_CONCLUSIONS = frozenset({"success", "neutral", "skipped"})
UNKNOWN_CHECK_CONCLUSIONS = frozenset({"", "unknown", "pending", "queued", "in_progress", "requested", "waiting"})
PR_CI_GATE_PASS = "pass"
PR_CI_GATE_REGRESSION = "pr-regression"
PR_CI_GATE_PRE_EXISTING = "pre-existing-failure"
PR_CI_GATE_UNKNOWN = "unknown"


@dataclass(frozen=True)
class ImplementPlan:
    task_source: str
    tactic_arguments: tuple[str, ...]
    uses_default_queue: bool


@dataclass(frozen=True)
class WorktreeWarning:
    repo_path: Path
    dirty: bool
    status_lines: tuple[str, ...]

    @property
    def message(self) -> str:
        if not self.dirty:
            return f"Worktree clean: {self.repo_path}"
        return (
            f"Warning: worktree is not clean: {self.repo_path}. "
            "Proceeding leaves dirty-state handling to $tactic."
        )


@dataclass(frozen=True)
class PushPlan:
    branch: str | None
    source: str
    requires_clarification: bool
    reason: str


@dataclass(frozen=True)
class CheckSnapshot:
    name: str
    conclusion: str | None
    cause: str | None = None


@dataclass(frozen=True)
class PrCiGateResult:
    status: str
    blockers: tuple[str, ...]
    details: tuple[str, ...]
    baseline_available: bool
    post_push_available: bool

    @property
    def passed(self) -> bool:
        return self.status == PR_CI_GATE_PASS


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


def notify_event_sequence() -> tuple[str, ...]:
    return IMPLEMENT_NOTIFY_EVENTS


def format_notify_plan() -> str:
    return "Notify events: " + ", ".join(IMPLEMENT_NOTIFY_EVENTS)


def resolve_push_plan(
    explicit_branch: str | None = None,
    current_branch: str | None = None,
    default_to_master: bool = False,
) -> PushPlan:
    if explicit_branch:
        return PushPlan(explicit_branch, "explicit", False, "using explicitly agreed branch")
    if current_branch:
        return PushPlan(current_branch, "current-context", False, "using current context branch")
    if default_to_master:
        return PushPlan("master", "master-default", False, "using master because context indicates normal master work")
    return PushPlan(None, "ambiguous", True, "branch inference is unsafe; ask for clarification before pushing")


def format_push_plan(plan: PushPlan) -> str:
    if plan.requires_clarification:
        return f"Push blocked: {plan.reason}"
    return f"Push target: {plan.branch} ({plan.source})"


def format_no_undone_tasks_message(undone_count: int) -> str:
    if undone_count == 0:
        return "No undone enqueued tasks found; nothing to implement and no push will be attempted."
    return f"Undone enqueued tasks: {undone_count}"


def can_push_after_tactic(all_runnable_complete: bool, committed_work: bool, blockers: Iterable[str] = ()) -> bool:
    return all_runnable_complete and committed_work and not tuple(blockers)


def format_push_failure(command: str, error_text: str) -> str:
    return f"Push failed while running {command!r}: {error_text.strip()}"


def normalize_check_conclusion(conclusion: str | None) -> str:
    return (conclusion or "").strip().lower().replace(" ", "_")


def is_check_passing(snapshot: CheckSnapshot) -> bool:
    return normalize_check_conclusion(snapshot.conclusion) in PASSING_CHECK_CONCLUSIONS


def is_check_unknown(snapshot: CheckSnapshot) -> bool:
    return normalize_check_conclusion(snapshot.conclusion) in UNKNOWN_CHECK_CONCLUSIONS


def is_check_failing(snapshot: CheckSnapshot) -> bool:
    return not is_check_passing(snapshot) and not is_check_unknown(snapshot)


def classify_pr_ci_gate(
    baseline_checks: Iterable[CheckSnapshot] | None,
    post_push_checks: Iterable[CheckSnapshot] | None,
    *,
    pr_context_available: bool = True,
) -> PrCiGateResult:
    if not pr_context_available:
        return PrCiGateResult(
            status=PR_CI_GATE_UNKNOWN,
            blockers=(),
            details=("PR context unavailable; cannot verify GitHub checks.",),
            baseline_available=baseline_checks is not None,
            post_push_available=post_push_checks is not None,
        )

    baseline_available = baseline_checks is not None
    post_push_available = post_push_checks is not None
    post_push = tuple(post_push_checks or ())
    if not post_push:
        return PrCiGateResult(
            status=PR_CI_GATE_UNKNOWN,
            blockers=(),
            details=("Post-push GitHub check data unavailable.",),
            baseline_available=baseline_available,
            post_push_available=post_push_available,
        )

    unknown_checks = tuple(check.name for check in post_push if is_check_unknown(check))
    if unknown_checks:
        return PrCiGateResult(
            status=PR_CI_GATE_UNKNOWN,
            blockers=unknown_checks,
            details=("One or more post-push checks have unknown or incomplete status.",),
            baseline_available=baseline_available,
            post_push_available=post_push_available,
        )

    failing_checks = tuple(check for check in post_push if is_check_failing(check))
    if not failing_checks:
        return PrCiGateResult(
            status=PR_CI_GATE_PASS,
            blockers=(),
            details=("All observed post-push PR checks passed or were neutral.",),
            baseline_available=baseline_available,
            post_push_available=post_push_available,
        )

    baseline_by_name = {check.name: check for check in (baseline_checks or ())}
    regressions: list[str] = []
    pre_existing: list[str] = []
    unknown_failures: list[str] = []

    for check in failing_checks:
        cause = (check.cause or "").strip().lower()
        if cause == "pr-caused":
            regressions.append(check.name)
            continue
        if cause in {"pre-existing", "unrelated", "environment"}:
            pre_existing.append(check.name)
            continue

        baseline = baseline_by_name.get(check.name)
        if baseline and is_check_passing(baseline):
            regressions.append(check.name)
        elif baseline and is_check_failing(baseline):
            pre_existing.append(check.name)
        elif baseline_available:
            regressions.append(check.name)
        else:
            unknown_failures.append(check.name)

    if regressions:
        return PrCiGateResult(
            status=PR_CI_GATE_REGRESSION,
            blockers=tuple(regressions),
            details=("Previously passing or newly observed checks failed after the PR push.",),
            baseline_available=baseline_available,
            post_push_available=post_push_available,
        )
    if unknown_failures:
        return PrCiGateResult(
            status=PR_CI_GATE_UNKNOWN,
            blockers=tuple(unknown_failures),
            details=("Post-push checks failed, but no baseline was available to prove whether they are new.",),
            baseline_available=baseline_available,
            post_push_available=post_push_available,
        )
    return PrCiGateResult(
        status=PR_CI_GATE_PRE_EXISTING,
        blockers=tuple(pre_existing),
        details=("Observed failures were already failing or marked non-PR-caused.",),
        baseline_available=baseline_available,
        post_push_available=post_push_available,
    )


def format_pr_ci_gate_result(result: PrCiGateResult) -> str:
    blockers = ", ".join(result.blockers) if result.blockers else "none"
    details = " ".join(result.details)
    return f"PR CI gate {result.status}: blockers={blockers}. {details}"


def build_worktree_warning(repo_path: Path, status_output: str) -> WorktreeWarning:
    status_lines = tuple(line for line in status_output.splitlines() if line.strip())
    return WorktreeWarning(repo_path=repo_path, dirty=bool(status_lines), status_lines=status_lines)


def inspect_worktree(repo_path: Path) -> WorktreeWarning:
    completed = subprocess.run(
        ["git", "-C", str(repo_path), "status", "--short"],
        check=True,
        capture_output=True,
        text=True,
    )
    return build_worktree_warning(repo_path, completed.stdout)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Describe an $implement wrapper handoff to $tactic.")
    parser.add_argument(
        "tactic_arguments",
        nargs="*",
        help="Arguments to forward unchanged to $tactic. Omit to use undone enqueued tasks.",
    )
    parser.add_argument(
        "--repo-root",
        default=".",
        help="Repo path to inspect for the non-blocking dirty-worktree warning.",
    )
    parser.add_argument("--branch", default=None, help="Explicit agreed branch to push.")
    parser.add_argument("--current-branch", default=None, help="Current context branch for push inference.")
    parser.add_argument(
        "--default-master",
        action="store_true",
        help="Allow master as the inferred push branch when no explicit/current branch is supplied.",
    )
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    plan = resolve_implement_plan(args.tactic_arguments)
    print(inspect_worktree(Path(args.repo_root)).message)
    print(format_tactic_handoff(plan))
    print(format_notify_plan())
    print(format_push_plan(resolve_push_plan(args.branch, args.current_branch, args.default_master)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
