# Onboarding Settings

Use this reference when first configuring the Linear-GitHub agent loop or when the user asks to change defaults.

## Settings Path

```text
~/.ticket-pilot/settings.md
```

Create the parent directory if needed. The file is a local, user-specific defaults document, **not** a credential store.

## First-Run Flow

1. **Check whether the settings file exists** and has the required sections.
2. **Verify Linear access.**
   - Check `$LINEAR_API_KEY` is set and valid.
   - If missing, direct the user to https://linear.app/settings/account/security → Personal API keys.
   - After key is set, verify workspace, user, teams, labels, projects, and statuses with read-only queries.
3. **Verify GitHub access.**
   - Priority 1: `gh auth status` — if valid, use `gh` for all GitHub operations.
   - Priority 2: `$GITHUB_TOKEN` — if set, use `curl` with this token.
   - Priority 3: Ask the user to choose: install `gh` CLI (`gh auth login`) or provide a PAT.
   - Verify org/repo permissions with read-only discovery calls.
4. **Present discovered defaults** to the user for confirmation.
5. **Write only confirmed, non-secret values** to `settings.md`.

## Required Settings Shape

Use plain Markdown with stable headings:

```markdown
# Ticket Pilot Settings

Last verified: YYYY-MM-DD

## Linear

- Workspace: <workspace-name>
- Workspace ID: <id if known>
- Default team: <team-name>
- Default team key: <KEY> (e.g. AI, ENG)
- Default team ID: <uuid>
- User name: <name>
- User email: <email>
- User ID: <linear-user-id>
- Default project: <name or blank>
- Default labels: <comma-separated>
- Status mapping:
  - Start: In Progress
  - Review: In Review
  - Complete: Done
  - Blocked: <team status or blank>

## GitHub

- Default owner/org: <github-owner>
- Default repository: <owner>/<repo> or "ask"
- Repository visibility default: public/private/ask
- Branch prefix: linear/
- Task artifact path: tasks/
- PR policy: draft/ready/ask

## Sync Rules

- Linear comment cadence: start, key node, failure, stop, completion
- Include commit/PR links in Linear comments: yes
- Include Linear issue ID in branch/commit/PR: yes
- Auto-move status on start: yes
- Auto-move status on completion: In Review unless user says Done

## Auth Method

- Linear: API key ($LINEAR_API_KEY)
- GitHub: gh / token / mcp (record which method is in use, NOT the credential itself)

## Notes

- <non-secret team preferences>
```

## Never Store

Never write these to `settings.md` or any file:

- Linear API keys or OAuth tokens
- GitHub PATs, OAuth tokens, GitHub App private keys, installation tokens
- Client secrets, cookies, bearer tokens, SSH private keys
- Raw authorization URLs containing one-time codes or state values

## Revalidation Rules

Reuse saved defaults on future runs, but revalidate when:

- Linear API returns auth failure, missing tools, or unexpected workspace/user.
- GitHub auth fails, repo/org access fails, or the default repo no longer exists.
- The user says they changed workspace, team, username, GitHub org, repository, or permissions.
- A write action would affect a different assignee, team, repo, or visibility than the saved defaults.

When revalidation changes a non-secret default, show the diff and ask before updating `settings.md`.
