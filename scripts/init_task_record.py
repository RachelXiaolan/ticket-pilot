#!/usr/bin/env python3
"""Create a task artifact folder for a Linear issue.

Usage:
    python3 init_task_record.py AI-1972 --title "Add login" --repo "owner/repo" --branch "linear/ai-1972-add-login"
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

# Linear issue identifiers follow "<TEAM_KEY>-<NUMBER>" where TEAM_KEY is 1-12
# uppercase letters/digits and NUMBER is a positive integer (e.g. AI-2134, ENG2-9).
_LINEAR_ID_RE = re.compile(r"^[A-Z][A-Z0-9]{0,11}-\d+$")

# Characters that should never appear in a Linear issue identifier. We reject
# these before regex matching so the error message is clearer and so that
# downstream code (which composes paths from this value) cannot be tricked
# into resolving outside the intended artifact root.
_FORBIDDEN_CHARS = frozenset("/\\;&|`$><\n\r\t")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Initialize a Linear task artifact folder")
    parser.add_argument("issue_id", help="Linear issue ID, e.g. AI-1972")
    parser.add_argument("--title", default="", help="Issue title")
    parser.add_argument("--repo", default="", help="GitHub repo URL or slug")
    parser.add_argument("--branch", default="", help="Git branch name")
    parser.add_argument("--root", default="tasks", help="Artifact root folder")
    return parser.parse_args()


def _validate_issue_id(issue_id: str) -> str:
    """Normalize and validate a Linear issue ID. Reject anything that looks
    malicious or that cannot be a real Linear identifier (path traversal,
    shell metacharacters, empty string, whitespace, etc.)."""
    if not issue_id:
        raise ValueError("issue_id must not be empty")
    # Reject any whitespace (incl. tabs, newlines) up front.
    if any(ch.isspace() for ch in issue_id):
        raise ValueError(
            f"issue_id must not contain whitespace (got {issue_id!r})"
        )
    # Reject path separators and obvious shell-metacharacters.
    bad = sorted(ch for ch in issue_id if ch in _FORBIDDEN_CHARS)
    if bad:
        raise ValueError(
            f"issue_id contains disallowed characters {bad!r} "
            f"(got {issue_id!r})"
        )
    # Uppercase the input but require the user to pass uppercase (don't silently
    # rewrite) — Linear identifiers are uppercase by convention.
    normalized = issue_id.upper()
    if not _LINEAR_ID_RE.match(normalized):
        raise ValueError(
            f"issue_id {issue_id!r} is not a valid Linear identifier "
            f"(expected format like 'AI-2134')"
        )
    return normalized


def _validate_root(root: str) -> Path:
    """The artifact root must be a relative path with no traversal segments."""
    if not root:
        raise ValueError("--root must not be empty")
    root_path = Path(root)
    if root_path.is_absolute():
        raise ValueError(f"--root must be a relative path (got {root!r})")
    if any(part == ".." for part in root_path.parts):
        raise ValueError(f"--root must not contain '..' (got {root!r})")
    return root_path


def main() -> None:
    args = parse_args()
    try:
        issue_id = _validate_issue_id(args.issue_id)
        root_path = _validate_root(args.root)
    except ValueError as e:
        print(f"❌ {e}", file=sys.stderr)
        sys.exit(2)

    task_dir = (root_path / issue_id).resolve()
    # Belt-and-suspenders: confirm the resolved dir is still under the root.
    resolved_root = root_path.resolve()
    try:
        task_dir.relative_to(resolved_root)
    except ValueError:
        print(
            f"❌ refusing to create task dir outside of {resolved_root}: {task_dir}",
            file=sys.stderr,
        )
        sys.exit(2)

    logs_dir = task_dir / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)

    task_json = task_dir / "task.json"
    notes_md = task_dir / "notes.md"

    if not task_json.exists():
        task_json.write_text(
            json.dumps(
                {
                    "issue_id": issue_id,
                    "title": args.title,
                    "repo": args.repo,
                    "branch": args.branch,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "linear_url": "",
                    "pr_url": "",
                    "status": "started",
                    "secret_policy": "No secrets in task artifacts.",
                },
                indent=2,
                ensure_ascii=False,
            )
            + "\n",
            encoding="utf-8",
        )

    if not notes_md.exists():
        notes_md.write_text(
            f"# {issue_id} Notes\n\n"
            "## Scope\n\n"
            "- \n\n"
            "## Progress\n\n"
            "- Started task artifact.\n\n"
            "## Verification\n\n"
            "- \n\n"
            "## Links\n\n"
            f"- Repo: {args.repo}\n"
            f"- Branch: {args.branch}\n",
            encoding="utf-8",
        )

    print(task_dir)


if __name__ == "__main__":
    main()
