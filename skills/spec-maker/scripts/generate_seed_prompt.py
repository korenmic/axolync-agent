from __future__ import annotations

import argparse
import html
import re
import sys
import time
from pathlib import Path


FEATURE_LABEL = "Feature Description: Summary:"
WORKSPACE_LABEL = "Workspace path:"


def detect_newline(text: str) -> str:
    idx = text.find("\r\n")
    if idx != -1:
        return "\r\n"
    return "\n"


def html_escape_seed(text: str) -> str:
    return html.escape(text, quote=True).replace("`", "&#x60;")


def split_seed(seed_text: str) -> tuple[str, str, str, str]:
    product_idx = seed_text.find("\n## Product Context")
    tech_idx = seed_text.find("\n## Technical Constraints")
    open_idx = seed_text.find("\n## Open Questions")
    if product_idx == -1 or tech_idx == -1 or open_idx == -1:
        raise ValueError(
            "Seed does not contain the expected top-level sections: "
            "## Product Context, ## Technical Constraints, ## Open Questions"
        )

    summary = seed_text[:product_idx].rstrip()
    product = seed_text[product_idx + 1 : tech_idx].rstrip()
    technical = seed_text[tech_idx + 1 : open_idx].rstrip()
    open_questions = seed_text[open_idx + 1 :].rstrip()
    return summary, product, technical, open_questions


def find_latest_template(workspace: Path) -> Path:
    chat_dir = workspace / ".codex" / "tmp" / "chat"
    candidates = sorted(chat_dir.glob("prompt-*.md"), key=lambda p: p.stat().st_mtime)
    if not candidates:
        raise FileNotFoundError(
            f"No template prompt files found under {chat_dir}. "
            "Run the Kiro wizard once or pass --template."
        )
    return candidates[-1]


def extract_template_parts(template_path: Path) -> tuple[str, str, str]:
    raw = template_path.read_text(encoding="utf-8")
    newline = detect_newline(raw)
    lines = raw.splitlines()

    feature_idx = next(
        (i for i, line in enumerate(lines) if line == FEATURE_LABEL),
        None,
    )
    workspace_idx = next(
        (i for i, line in enumerate(lines) if line.startswith(WORKSPACE_LABEL)),
        None,
    )
    if feature_idx is None or workspace_idx is None or workspace_idx <= feature_idx:
        raise ValueError(
            f"Template prompt {template_path} does not match the expected Kiro wrapper shape."
        )

    prefix = newline.join(lines[: feature_idx + 1])
    footer = newline.join(lines[workspace_idx:])
    return prefix, footer, newline


def replace_workspace_line(footer: str, workspace_display: str) -> str:
    replacement = f"Workspace path: {workspace_display}".replace("\\", r"\\")
    return re.sub(
        r"^Workspace path:.*$",
        replacement,
        footer,
        count=1,
        flags=re.MULTILINE,
    )


def build_prompt(
    prefix: str,
    footer: str,
    newline: str,
    workspace_display: str,
    seed_sections: tuple[str, str, str, str],
) -> str:
    summary, product, technical, open_questions = seed_sections
    body_parts = [
        html_escape_seed(summary),
        "",
        "Product Context:",
        html_escape_seed(product),
        "",
        "Technical Constraints:",
        html_escape_seed(technical),
        "",
        "Open Questions:",
        html_escape_seed(open_questions),
        "",
        replace_workspace_line(footer, workspace_display),
    ]
    return prefix + newline + newline.join(body_parts) + newline


def default_output_path(workspace: Path) -> Path:
    stamp = int(time.time() * 1000)
    return workspace / ".codex" / "tmp" / "chat" / f"prompt-{stamp}-specmaker.md"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate a Kiro-style spec prompt file from a project seed."
    )
    parser.add_argument("--seed", required=True, help="Path to the seed markdown file.")
    parser.add_argument("--workspace", required=True, help="Workspace root path.")
    parser.add_argument(
        "--output",
        help="Optional output prompt file path. Defaults to .codex/tmp/chat/prompt-<ts>-specmaker.md under the workspace.",
    )
    parser.add_argument(
        "--template",
        help="Optional existing prompt file to clone the wrapper from. Defaults to the newest .codex/tmp/chat/prompt-*.md under the workspace.",
    )
    args = parser.parse_args()

    seed_path = Path(args.seed).resolve()
    workspace_input = args.workspace
    workspace = Path(args.workspace).resolve()
    output_path = Path(args.output).resolve() if args.output else default_output_path(workspace)
    template_path = Path(args.template).resolve() if args.template else find_latest_template(workspace)

    seed_text = seed_path.read_text(encoding="utf-8")
    seed_sections = split_seed(seed_text)
    prefix, footer, newline = extract_template_parts(template_path)
    prompt_text = build_prompt(prefix, footer, newline, workspace_input, seed_sections)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(prompt_text, encoding="utf-8", newline="")
    print(output_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
