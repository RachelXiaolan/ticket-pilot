#!/usr/bin/env python3
"""Create a task artifact folder for a Linear issue.

Usage:
    python3 init_task_record.py AI-1972 --title "Add login" --repo "owner/repo" --branch "linear/ai-1972-add-login"
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Initialize a Linear task artifact folder")
    parser.add_argument("issue_id", help="Linear issue ID, e.g. AI-1972")
    parser.add_argument("--title", default="", help="Issue title")
    parser.add_argument("--repo", default="", help="GitHub repo URL or slug")
    parser.add_argument("--branch", default="", help="Git branch name")
    parser.add_argument("--root", default="tasks", help="Artifact root folder")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    issue_id = args.issue_id.upper()
    task_dir = Path(args.root) / issue_id
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
