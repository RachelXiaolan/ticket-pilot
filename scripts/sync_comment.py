#!/usr/bin/env python3
"""Post a progress comment to BOTH Linear and the linked GitHub issue.

Usage:
    python3 sync_comment.py \
        --linear-id AI-2090 \
        --gh-issue 2 \
        --repo RachelXiaolan/ticket-pilot \
        --emoji 🚀 \
        --title "Starting work" \
        --body "Branch: linear/ai-2090-...\nScope: MVP validation\nNext: create branch"

If --gh-issue or --repo is omitted, posts to Linear only (with a warning).
Requires LINEAR_API_KEY env var and gh CLI auth.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys


def linear_comment(issue_id: str, body: str) -> str | None:
    """Post a comment to a Linear issue. Returns comment ID or None."""
    key = os.environ.get("LINEAR_API_KEY")
    if not key:
        print("⚠️  LINEAR_API_KEY not set — skipping Linear comment", file=sys.stderr)
        return None

    # Use GraphQL variables instead of string interpolation.
    # Previously the body was manually escaped into the query string, which is
    # fragile — control characters (\r, \t, \x00), backticks, or unicode could
    # break the mutation payload. Variables let the GraphQL server handle all
    # escaping correctly.
    query = (
        "mutation($input: CommentCreateInput!) {"
        "  commentCreate(input: $input) { success comment { id } }"
        "}"
    )
    variables = {
        "input": {
            "issueId": issue_id,
            "body": body,
        }
    }

    result = subprocess.run(
        ["curl", "-s", "-X", "POST", "https://api.linear.app/graphql",
         "-H", f"Authorization: {key}",
         "-H", "Content-Type: application/json",
         "-d", json.dumps({"query": query, "variables": variables})],
        capture_output=True, text=True, timeout=15
    )

    # Robust error handling: Linear responses come in three failure shapes,
    # and we must never raise out of this function:
    #   1. Non-JSON / empty stdout (network failure, 5xx HTML page) → JSONDecodeError
    #   2. {"errors": [...]}                          → handle via .get("errors")
    #   3. {"data": null, "errors": [...]}            → None is not subscriptable
    try:
        data = json.loads(result.stdout) if result.stdout.strip() else {}
    except json.JSONDecodeError as e:
        print(f"❌ Linear comment failed: non-JSON response: {e}", file=sys.stderr)
        return None

    if data.get("errors"):
        print(f"❌ Linear comment failed: {data['errors']}", file=sys.stderr)
        return None

    payload = data.get("data") or {}
    comment = (payload.get("commentCreate") or {}).get("comment") or {}
    comment_id = comment.get("id")
    if not comment_id:
        print(f"❌ Linear comment failed: unexpected response shape: {data}", file=sys.stderr)
        return None

    print(f"✅ Linear comment posted to {issue_id} (id: {comment_id[:8]}...)")
    return comment_id


def github_comment(issue_num: str, repo: str, body: str) -> bool:
    """Post a comment to a GitHub issue via gh CLI. Returns True on success."""
    if not issue_num or not repo:
        print("⚠️  No GitHub issue/repo specified — skipping GitHub mirror", file=sys.stderr)
        return False

    result = subprocess.run(
        ["gh", "issue", "comment", issue_num,
         "--repo", repo,
         "--body", body],
        capture_output=True, text=True, timeout=15
    )
    if result.returncode != 0:
        print(f"❌ GitHub comment failed: {result.stderr}", file=sys.stderr)
        return False
    print(f"✅ GitHub comment posted to {repo}#{issue_num}")
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description="Post a synced comment to Linear + GitHub issue")
    parser.add_argument("--linear-id", required=True, help="Linear issue ID (e.g. AI-2090)")
    parser.add_argument("--gh-issue", default="", help="GitHub issue number")
    parser.add_argument("--repo", default="", help="GitHub repo (owner/name)")
    parser.add_argument("--emoji", default="💬", help="Emoji prefix")
    parser.add_argument("--title", default="Progress update", help="Short title for the comment")
    parser.add_argument("--body", required=True, help="Comment body (Markdown)")
    args = parser.parse_args()

    # Linear gets the full comment
    linear_body = f"{args.emoji} **{args.title}**\n\n{args.body}"

    # GitHub gets a mirrored version with Linear link
    gh_body = f"{args.emoji} **{args.title}** *(mirrored from Linear {args.linear_id})*\n\n{args.body}"

    linear_comment(args.linear_id, linear_body)
    github_comment(args.gh_issue, args.repo, gh_body)


if __name__ == "__main__":
    main()
