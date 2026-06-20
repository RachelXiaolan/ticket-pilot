#!/usr/bin/env python3
"""Create a task artifact folder for a Linear issue.

Usage:
    python3 init_task_record.py AI-1972 --title "Add login" --repo "owner/repo" --branch "linear/ai-1972-add-login"
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Initialize a Linear task artifact folder")
    parser.add_argument("issue_id", help="Linear issue ID, e.g. AI-1972")
    parser.add_argument("--title", default="", help="Issue title")
    parser.add_argument("--repo", default="", help="GitHub repo URL or slug")
    parser.add_argument("--branch", default="", help="Git branch name")
    parser.add_argument("--root", default="tasks", help="Artifact root folder")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Refresh an existing task artifact (rewrites task.json and notes.md)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    issue_id = args.issue_id.upper()
    task_dir = Path(args.root) / issue_id

    task_json = task_dir / "task.json"
    notes_md = task_dir / "notes.md"

    existing = task_json.exists() or notes_md.exists()
    if existing and not args.force:
        print(
            f"❌ Task artifact already exists at {task_dir}. "
            "Re-running with the same args would silently leave a stale notes.md from a previous issue. "
            "Pass --force to refresh, or remove the folder manually.",
            file=sys.stderr,
        )
        sys.exit(2)

    try:
        # When --force, mkdir(exist_ok=True) so we reuse the folder. Otherwise the
        # existing-files check above has already exited.
        task_dir.mkdir(parents=True, exist_ok=True)
        (task_dir / "logs").mkdir(exist_ok=True)
    except PermissionError as e:
        print(
            f"❌ Cannot create task artifact at {task_dir}: permission denied ({e}). "
            "Check that --root points to a writable directory.",
            file=sys.stderr,
        )
        sys.exit(1)
    except OSError as e:
        print(f"❌ Cannot create task artifact at {task_dir}: {e}", file=sys.stderr)
        sys.exit(1)

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
