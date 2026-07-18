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


def invocation_pattern(names: set[str], prefix: str) -> re.Pattern[str]:
    # Longest name first so `queue-status` wins over `queue`.
    ordered = sorted(names, key=len, reverse=True)
    alt = "|".join(re.escape(name) for name in ordered)
    # Leading boundary excludes path/identifier chars so `foo/queue-status`
    # (a path) is never treated as an invocation; trailing boundary keeps the
    # match to a whole skill name.
    return re.compile(
        r"(?<![A-Za-z0-9._/-])" + re.escape(prefix) + r"(?:" + alt + r")(?![A-Za-z0-9-])"
    )


def transform_text(text: str, names: set[str]) -> str:
    pattern = invocation_pattern(names, "$")
    return pattern.sub(lambda m: "/" + m.group(0)[1:], text)


def reverse_text(text: str, names: set[str]) -> str:
    pattern = invocation_pattern(names, "/")
    return pattern.sub(lambda m: "$" + m.group(0)[1:], text)


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
