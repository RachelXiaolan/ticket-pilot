# GitHub Conventions

## Branches

Default branch pattern:

```text
linear/<issue-id-lowercase>-<short-slug>
```

Example:

```text
linear/ai-1972-add-login-flow
```

If the repo already has a naming convention, follow the repo.

### Create a branch

```bash
git checkout main && git pull origin main
git checkout -b linear/ai-1972-add-login-flow
```

## Commits

Include the Linear issue ID in commit messages:

```text
AI-1972 Add login flow with OAuth

- Add login endpoint
- Add JWT token generation
- Add auth middleware
```

Keep commits focused and reversible. Do not commit secrets, `.env`, or credentials.

## Pull Requests

### Create with gh CLI

```bash
gh pr create \
  --title "AI-1972: Add login flow with OAuth" \
  --body "$(cat <<'EOF'
## Linear Issue
https://linear.app/<workspace>/issue/AI-1972

## Summary
- Added OAuth login flow
- JWT token generation and validation

## Test Plan
- [ ] Unit tests pass
- [ ] Manual login test

Closes [AI-1972]
EOF
)"
```

### Create with curl (PAT auth)

```bash
curl -s -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/repos/$OWNER/$REPO/pulls \
  -d '{
    "title": "AI-1972: Add login flow with OAuth",
    "body": "## Linear Issue\nhttps://linear.app/...\n\n## Summary\n...",
    "head": "linear/ai-1972-add-login-flow",
    "base": "main"
  }'
```

PR body should always include:
- Linear issue link
- Summary of changes
- Verification commands
- Deployment notes
- Risks or follow-ups

## Task Artifacts

When useful, create a task folder in the repo:

```text
tasks/<ISSUE-ID>/
  task.json      # metadata, no secrets
  notes.md       # decision log
  logs/          # test/deploy logs
```

Use `scripts/init_task_record.py` to create this skeleton:

```bash
python3 scripts/init_task_record.py AI-1972 \
  --title "Add login flow" \
  --repo "owner/repo" \
  --branch "linear/ai-1972-add-login-flow"
```

`task.json` should never contain secrets. Store references, not credentials.

## PR Lifecycle

```bash
# Push branch
git push -u origin HEAD

# Monitor CI (gh)
gh pr checks --watch

# Monitor CI (curl)
SHA=$(git rev-parse HEAD)
curl -s -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/commits/$SHA/status

# Merge when green
gh pr merge --squash --delete-branch
# OR
curl -s -X PUT \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/pulls/$PR_NUMBER/merge \
  -d '{"merge_method": "squash"}'
```
