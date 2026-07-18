"""Claudify: generate Claude-compatible skill copies from canonical Codex skill sources.

The tracked skill sources under skills-workspace/ and skills-user/ stay the single
source of truth and use the Codex `$name` invocation prefix. This script produces
Claude-shaped hard copies where known-skill `$name` invocations become `/name`,
leaving every other `$` usage and every file path untouched.

Workspace-skill copies are auto-installed into the workspace `.claude/skills`.
User-skill copies are generated only; installing them globally is a manual step the
script offers on every run and never performs itself.
"""
from __future__ import annotations

import argparse
import re
import shutil
import sys
from pathlib import Path


TRANSFORM_SUFFIXES = {".md", ".yaml", ".yml"}
BUCKETS = ("skills-workspace", "skills-user")


def known_skill_names(agent_root: Path) -> set[str]:
    names: set[str] = set()
    for bucket in BUCKETS:
        bucket_dir = agent_root / bucket
        if not bucket_dir.is_dir():
            continue
        for child in bucket_dir.iterdir():
            if child.is_dir():
                names.add(child.name)
    return names


# A transformation candidate is any invocation-shaped token: a prefix character
# ($ in sources, / in generated copies) followed by an invocation-shaped name.
# The leading boundary excludes path/identifier characters, so a name inside a
# file path (e.g. skills-user/queue-status) is never treated as a candidate.
CANDIDATE_BODY = r"([A-Za-z0-9][A-Za-z0-9_-]*)"
DOLLAR_CANDIDATE_RE = re.compile(r"(?<![A-Za-z0-9._/-])\$" + CANDIDATE_BODY)
SLASH_CANDIDATE_RE = re.compile(r"(?<![A-Za-z0-9._/-])/" + CANDIDATE_BODY)
# The escaped (neutralized) form of a rogue invocation: "/ name" with one space.
ESCAPED_SLASH_CANDIDATE_RE = re.compile(r"(?<![A-Za-z0-9._/-])/ " + CANDIDATE_BODY)

# Per-file allowlist of expected uninventoried `$`-candidates: documentation
# placeholders that are not real invocations. Any uninventoried candidate found in
# a file that is not listed here is treated as unexpected and fails CI, so a future
# implementer reviews it (for example, a typo'd skill name).
UNINVENTORIED_ALLOWLIST = {
    "skills-workspace/claudify/SKILL.md": {"name"},
}


def transformation_candidates(text: str) -> list[str]:
    """Every `$`-prefixed transformation-candidate name found in text, in order."""
    return [m.group(1) for m in DOLLAR_CANDIDATE_RE.finditer(text)]


def partition_candidates(text: str, names: set[str]) -> tuple[list[str], list[str]]:
    """Split candidates into (inventoried, uninventoried) against the skill inventory.

    This is the single source of truth for the transform: the script converts only
    the inventoried group, and the tests assert the uninventoried group is discarded.
    """
    inventoried: list[str] = []
    uninventoried: list[str] = []
    for cand in transformation_candidates(text):
        (inventoried if cand in names else uninventoried).append(cand)
    return inventoried, uninventoried


def escape_rogue_invocations(text: str, names: set[str]) -> str:
    """Neutralize pre-existing rogue `/name` invocations for known skills.

    Codex sources never intentionally use the Claude `/name` invocation form, so any
    invocation-position `/name` for a known skill is stale/rogue. Insert one space
    (`/name` -> `/ name`) so it cannot trigger a Claude skill. Path-position `/name`
    (e.g. `skills-user/queue-status`) is excluded by the leading boundary, so file
    paths are never touched.
    """
    def repl(m: "re.Match[str]") -> str:
        return "/ " + m.group(1) if m.group(1) in names else m.group(0)
    return SLASH_CANDIDATE_RE.sub(repl, text)


def transform_text(text: str, names: set[str]) -> str:
    """Escape rogue `/name`, then convert `$name` -> `/name` for inventoried skills only.

    Escaping runs first, on the original source (which has no legit `/name`), so it
    never touches the real `/name` invocations produced by the `$name` conversion.
    """
    text = escape_rogue_invocations(text, names)

    def repl(m: "re.Match[str]") -> str:
        return "/" + m.group(1) if m.group(1) in names else m.group(0)
    return DOLLAR_CANDIDATE_RE.sub(repl, text)


def reverse_text(text: str, names: set[str]) -> str:
    """Inverse of transform_text for tests: undo `$`->`/`, then un-escape `/ name`."""
    def undo_dollar(m: "re.Match[str]") -> str:
        return "$" + m.group(1) if m.group(1) in names else m.group(0)
    text = SLASH_CANDIDATE_RE.sub(undo_dollar, text)

    def undo_escape(m: "re.Match[str]") -> str:
        return "/" + m.group(1) if m.group(1) in names else m.group(0)
    return ESCAPED_SLASH_CANDIDATE_RE.sub(undo_escape, text)


def claudify_bucket(src_dir: Path, out_dir: Path, names: set[str]) -> int:
    """Copy src_dir into out_dir, transforming invocations in text files.

    Returns the number of files written.
    """
    written = 0
    for src in sorted(src_dir.rglob("*")):
        rel = src.relative_to(src_dir)
        dest = out_dir / rel
        if src.is_dir():
            dest.mkdir(parents=True, exist_ok=True)
            continue
        dest.parent.mkdir(parents=True, exist_ok=True)
        if src.suffix.lower() in TRANSFORM_SUFFIXES:
            text = src.read_text(encoding="utf-8")
            dest.write_text(transform_text(text, names), encoding="utf-8")
        else:
            shutil.copy2(src, dest)
        written += 1
    return written


def install_workspace_skills(out_ws_dir: Path, dest_skills_dir: Path) -> int:
    """Replace each workspace skill in dest_skills_dir from generated copies."""
    if not out_ws_dir.is_dir():
        return 0
    dest_skills_dir.mkdir(parents=True, exist_ok=True)
    installed = 0
    for skill_dir in sorted(out_ws_dir.iterdir()):
        if not skill_dir.is_dir():
            continue
        target = dest_skills_dir / skill_dir.name
        if target.exists():
            shutil.rmtree(target)
        shutil.copytree(skill_dir, target)
        installed += 1
    return installed


def generate(agent_root: Path, output_dir: Path) -> dict:
    names = known_skill_names(agent_root)
    if output_dir.exists():
        shutil.rmtree(output_dir)
    counts = {}
    for bucket in BUCKETS:
        src = agent_root / bucket
        if not src.is_dir():
            counts[bucket] = 0
            continue
        counts[bucket] = claudify_bucket(src, output_dir / bucket, names)
    return {"names": names, "counts": counts, "output": output_dir}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Generate Claude-compatible skill copies from Codex skill sources."
    )
    parser.add_argument(
        "--agent-root",
        help="axolync-agent repo root (default: the repo containing this script).",
    )
    parser.add_argument(
        "--workspace",
        help="Workspace root for .claude/skills install (default: parent of the agent root).",
    )
    parser.add_argument(
        "--output",
        help="Output directory for generated copies (default: <agent-root>/.claudify-out).",
    )
    parser.add_argument(
        "--no-install",
        action="store_true",
        help="Generate artifacts only; do not auto-install workspace skills.",
    )
    args = parser.parse_args(argv)

    agent_root = Path(args.agent_root).resolve() if args.agent_root else Path(__file__).resolve().parents[1]
    workspace = Path(args.workspace).resolve() if args.workspace else agent_root.parent
    output_dir = Path(args.output).resolve() if args.output else agent_root / ".claudify-out"

    result = generate(agent_root, output_dir)
    print(f"claudify: {len(result['names'])} known skills")
    for bucket, count in result["counts"].items():
        print(f"claudify: generated {count} files for {bucket} -> {output_dir / bucket}")

    if not args.no_install:
        dest = workspace / ".claude" / "skills"
        installed = install_workspace_skills(output_dir / "skills-workspace", dest)
        print(f"claudify: installed {installed} workspace skills into {dest}")
    else:
        print("claudify: --no-install set; skipped workspace skill install")

    user_src = output_dir / "skills-user"
    user_dest = Path.home() / ".claude" / "skills"
    print("")
    print("claudify: user skills were generated but NOT installed globally.")
    print(f"claudify: to install them by hand (usually once per environment), copy:")
    print(f"    from: {user_src}")
    print(f"    into: {user_dest}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
