---
name: ticket-pilot
description: >
  Ticket Pilot: coordinate Linear issue work with GitHub-backed task tracking.
  Works with any agent (Hermes, Codex, Claude Code, OpenClaw, Cursor, Gemini CLI).
  Use when the user asks to work on a Linear issue, sync Linear and GitHub,
  update Linear comments/status while coding, inspect teammate issue status,
  create branches/PRs for Linear tasks, or run an agent workflow across Linear
  issues/projects and GitHub repositories.
version: 3.0.0
author: Rachel Lu
license: MIT
platforms: [linux, macos, windows]
prerequisites:
  env_vars: [LINEAR_API_KEY]
  commands: [curl]
  github: "gh CLI or GITHUB_TOKEN (one required)"
tags: [Linear, GitHub, Issues, Project Management, Automation, Workflow, Sync]
---

# Ticket Pilot

## Overview

Run a Linear issue as a traceable engineering workflow.

- **Linear** = task control plane: issue status, assignee, project, labels, progress comments.
- **GitHub** = durable artifact store: code, branches, commits, PRs, task notes, logs.
- **This skill** = orchestrator: connects both sides, keeps them in sync.

This skill is **agent-agnostic**. It does not depend on any specific MCP server or CLI
framework. It works with whatever auth and tools the agent's environment provides.

### Agent compatibility

This skill uses the [Agent Skills open standard](https://agentskills.io).
Any agent that supports `SKILL.md` + YAML frontmatter can use it.

Install with curl (recommended):
```bash
curl -fsSL https://raw.githubusercontent.com/RachelXiaolan/ticket-pilot/main/install.sh | bash -s -- --agent claude
```

Or via skills.sh:
```bash
npx skills add RachelXiaolan/ticket-pilot
```

| Agent | Skills directory |
|-------|-----------------|
| Claude Code | `~/.claude/skills/` |
| Codex | `~/.codex/skills/` |
| Hermes | `~/.hermes/skills/productivity/` |
| OpenClaw | `~/.openclaw/skills/` |
| Cursor | `.cursor/skills/` |
| Gemini CLI | `.gemini/skills/` |

The agent using this skill should identify itself by name in progress comments
(e.g. "Hermes agent", "Claude Code", "Codex") so team members know who did what.

## Companion Skills (load for platform mechanics)

This skill defines the **orchestration workflow**. For the underlying platform mechanics,
load these companion skills:

- **`linear`** — Linear GraphQL API patterns + Python CLI helper (`scripts/linear_api.py`).
  Use `linear_api.py` for faster one-liners: `python3 linear_api.py whoami`, `list-teams`,
  `create-issue`, `update-status`, `add-comment`, `search-issues`, etc. Prefer this helper
  over hand-crafted curl for all standard Linear operations.
- **`github-repo-management`** — repo creation, cloning, settings, releases, secrets.
- **`github-pr-workflow`** — branch → commit → PR → CI monitoring → merge lifecycle.
- **`github-issues`** — GitHub issue management (when GitHub issues are also in scope).

The curl/GraphQL examples below are for reference. For any standard Linear operation,
check the `linear` skill's CLI helper first — it wraps the common cases.

## Authentication

### Linear

Use a **Linear Personal API key** (preferred for simplicity):

1. Go to Linear → Settings → Account → Security & access → Personal API keys
   (https://linear.app/settings/account/security)
2. Create a key, copy it.
3. Set it as `LINEAR_API_KEY` environment variable (or in agent env config).

API details:
- Endpoint: `https://api.linear.app/graphql` (POST)
- Header: `Authorization: $LINEAR_API_KEY` (no "Bearer" prefix)
- All requests are POST with `Content-Type: application/json`
- Both UUIDs and short IDs (e.g. `AI-1972`) work

Quick test:
```bash
curl -s -X POST https://api.linear.app/graphql \
  -H "Authorization: $LINEAR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "{ viewer { id name email } }"}' | python3 -m json.tool
```

If the agent environment has a Linear MCP available, that works too — use the MCP
tools directly and skip the API key.

### GitHub

**Option 1 — gh CLI (preferred):**
```bash
gh auth login          # interactive setup
gh auth status         # verify
```

**Option 2 — Personal Access Token (PAT):**
Set `GITHUB_TOKEN` in the environment. The skill will use it for API calls.
```
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxx
```

**Option 3 — GitHub App / MCP:**
If a GitHub MCP or App is configured, use it directly.

The skill auto-detects auth method:
```bash
# Detection priority
if command -v gh &>/dev/null && gh auth status &>/dev/null; then
  AUTH="gh"        # use gh CLI for everything
elif [ -n "$GITHUB_TOKEN" ]; then
  AUTH="token"     # use curl + GITHUB_TOKEN
else
  AUTH="none"      # ask user to authenticate
fi
```

## Onboarding

### When to run onboarding

Run onboarding when:
- First connecting to a workspace (no `settings.md` exists)
- The user asks to change defaults
- Auth fails or workspace/repo context changes

### First-run setup flow

1. **Verify Linear access.** Test the API key with a `viewer` query. If it fails, ask
   the user to create a new key at https://linear.app/settings/account/security.

2. **Verify GitHub access.** Run `gh auth status` or check `$GITHUB_TOKEN`. If neither
   is available, present both options (gh CLI or PAT) and let the user choose.

3. **Auto-discover workspace context.** Query all of the following in read-only mode:
   - Teams (`teams { nodes { id name key } }`)
   - Projects (`projects(first: 50) { nodes { id name teams { nodes { key } } } }`)
   - Labels (`issueLabels(first: 50) { nodes { id name color } }`)
   - Workflow states for each team
   - Users / potential assignees (`users { nodes { id name email active } }`)

4. **Let user choose defaults.** Present the discovered options and let the user select:

   | Setting | How to present |
   |---------|---------------|
   | **Default team** | List all teams, ask user to pick one |
   | **Default project** | List projects in the selected team, ask user to pick (or "none") |
   | **Default label(s)** | List all labels, ask user to pick their personal label(s) |
   | **Default assignee** | Default to the current user; ask if they want to add others |

5. **Confirm and save.** Show a summary of all selected defaults, get user confirmation,
   then write to `settings.md`. Include this note to the user:

   > 💡 These defaults will be used automatically when creating new issues.
   > To override any default for a specific issue, just specify it when creating
   > (e.g. "create an issue in team SBY", "assign to Yongcheng", "add label Leo").

6. **Save only non-secret defaults** to `settings.md`. Never save tokens, keys, or secrets.

Read `references/onboarding-settings.md` for the exact settings format and revalidation rules.

### Default resolution at issue creation

When creating a Linear issue, resolve each field in this order:

1. **User-specified value** (if the user said "team SBY" or "assign to Leo") — use it.
2. **Saved default** (from `settings.md`) — use it silently.
3. **No default and user didn't specify** — ask the user.

Always show the resolved values before creating (e.g. "Creating in team **ken-team**,
assigned to **Rachel**, labeled **Rachel**. Correct?"). Give the user a chance to
override before confirming.

## Label & Assignee Rules

When creating or updating Linear issues, always apply labels and assignees explicitly:

- **Default assignee = current user** (from `settings.md`). Auto-assign to the user unless they say otherwise.
- **Default label = user's personal label** (e.g. `Rachel`). Always attach the user's label to their own issues.
- **If the issue involves other teammates** — ask the user which labels and assignees to add. Do not guess.
- **If the issue is ambiguous** (could belong to multiple people) — ask one concise question rather than auto-assigning.
- **Never remove or change someone else's label/assignee** without asking.

Summary: **Default to the user, ask when uncertain.**

## Intent Detection — Read vs Write

**Before doing anything**, determine the user's intent:

| User says | Intent | What to do |
|-----------|--------|------------|
| "看一下 AI-2090" / "看看这个 issue" / "什么情况" | **Read-only** | Read the issue, summarize it, STOP. Do NOT change status, post comments, create GitHub issues, or start working. |
| "帮我看看团队在做什么" / "看看大家进度" | **Read-only** | Query and summarize team status. Do NOT modify anything. |
| "开始做 AI-2090" / "处理 AI-2090" / "搞一下这个" | **Start work** | Run the full Start Workflow below. |
| "AI-2090 做完了" / "改完了" | **Complete work** | Verify, move to In Review/Done, post completion comment. |
| "建个 issue：xxx" | **Create** | Create new issue + GitHub mirror. |
| Unclear | **Ask** | "你是想让我看一下这个 issue，还是开始做？" |

**Critical:** When in doubt, default to **read-only**. Changing issue status, posting comments,
and creating GitHub issues are **write actions** that the user must explicitly trigger —
either by saying "开始/处理/做" or by confirming when asked.

Never assume the user wants to start working just because they mentioned an issue.
A user saying "看一下 AI-2107" means "read and summarize it" — that's it.

## Start Workflow

**Only enter this workflow when the user explicitly says to start work**
(e.g. "开始做", "处理", "搞一下", "work on", "start").

1. **Resolve the target Linear issue** from the user request.
   - Accept issue IDs like `AI-2090`, Linear URLs, or a query like "my current issue".
   - Read the issue: title, description, status, assignee, team, project, labels,
     comments, and linked PRs.
   - Read team workflow states before changing anything.

2. **Confirm ownership and scope.**
   - Apply Label & Assignee Rules (above).
   - If unassigned and the user wants it, assign it.
   - If another human owns it, ask before reassigning.
   - If ambiguous, ask one concise question.

3. **Create a linked GitHub issue** (if one doesn't exist yet).
   - Use the same title (with Linear ID prefix, e.g. `AI-2090: <title>`).
   - Body must include the Linear issue URL and a summary.
   - This GitHub issue mirrors progress comments from Linear (see "Comment Sync" below).
   - GitHub issues **cannot** fully track workflow status (In Progress etc.) or numeric priority — Linear is
     the source of truth for those. GitHub labels/assignees/projects DO exist and can be used for basic categorization (see "Label / Assignee / Project mirroring" below).
   - Link the GitHub issue number back to Linear via a comment.

4. **(Optional) Create a GitHub code context.** — only if the issue involves actual code work.
   - Many issues (research, planning, discussion) don't need branches or PRs — skip this step.
   - When code IS involved: create or switch to a branch named `linear/<issue-id>-<short-slug>`.
   - Optionally create a task artifact folder with `scripts/init_task_record.py`.

5. **Mark work started.**
   - Move the Linear issue to "In Progress" (or team equivalent).
   - Leave a **comment on both Linear and GitHub issue** with scope and first planned step.
   - Include branch/repo info if step 4 was done.

## During Work

### Comment principles

Comments are **phase-based, not prompt-based**. The agent should:

1. **Analyze the task flow** — identify natural phases/parts in the work. Multiple steps that
   belong to the same phase (e.g. "research phase", "implementation phase") should be
   summarized in **one comment** when the phase completes, not commented step-by-step.

2. **Comment at phase boundaries** — when one logical chunk of work is done, post a concise
   update. Don't post a comment for every single interaction.

3. **Be concise** — each comment should be short and scannable. No walls of text.

### Required in every comment

Every comment MUST include:

- **Who**: which agent/person did this (e.g. "Hermes agent", "Codex", or the user's name)
- **What happened**: brief summary of what was accomplished in this phase
- **Key outputs**: links to tangible results — repo, branch, published page, PR, document, etc.
  If there are no tangible outputs this phase, say what the next step is instead.

### Comment triggers

Post a comment when:

| Trigger | Example |
|---------|---------|
| **Phase complete** | "Research done — identified 3 options" |
| **Key output produced** | "Published: https://..." / "PR opened: #12" |
| **Blocked / needs human** | "Blocked: need API access, @user please check" |
| **Task complete** | "Done — PR merged, verification passed" |

Do NOT post a comment for every prompt. If the user sends 5 messages that are all part of
"writing the report", post ONE comment when the report is done.

### Example comment

```
Hermes agent — Phase 2: Implementation complete

- Built the sync_comment.py script
- Committed to branch linear/ai-2090-ticket-pilot-skill (commit 37c1b92)
- Repo: https://github.com/RachelXiaolan/ticket-pilot/tree/linear/ai-2090-ticket-pilot-skill
Next: open PR and move to In Review
```

Note how it's short, says who did it, what was done, links the key output, and says what's next.

### Customization

The exact format is not locked down. Users should feel free to adjust:
- Language (Chinese / English / mixed)
- Level of detail
- Emoji usage
- Whether to include timestamps, commit hashes, etc.

The skill provides the baseline; the user defines their preferred style.

## Comment Sync (Linear ↔ GitHub Issue)

Every Linear progress comment must be **mirrored to the linked GitHub issue**. This keeps
both platforms in sync for team members who check either one.

**Use `scripts/sync_comment.py` to post to both platforms in one call:**

```bash
python3 scripts/sync_comment.py \
  --linear-id AI-2090 \
  --gh-issue 2 \
  --repo RachelXiaolan/ticket-pilot \
  --emoji 🚀 \
  --title "Starting work" \
  --body "Branch: linear/ai-2090-ticket-pilot-skill
Scope: MVP workflow validation
Next: create branch, commit skill files, open PR"
```

**What GitHub issues CAN mirror:**
- Comments / progress updates ✓
- Links to commits, branches, PRs ✓ (when applicable)
- Labels ✓ — GitHub has its own labels; can mirror Linear labels or use GitHub-native ones
- Assignees ✓ — GitHub has assignees (up to 10 per issue)
- Projects ✓ — GitHub Projects (v2) can group issues, similar to Linear projects

**What GitHub issues CANNOT fully mirror (Linear is source of truth):**
- **Workflow state machine** — Linear has structured states (Backlog → In Progress → In Review → Done) with types. GitHub has no built-in workflow status. Workaround: use GitHub labels as pseudo-status (e.g. `status:in-progress`), but this is optional.
- **Priority levels** — Linear has numeric priority (0-4). GitHub has no native priority field. Workaround: labels or GitHub Project custom fields.

### Label / Assignee / Project mirroring (technical debt)

> **TODO:** When deploying to a team GitHub org (e.g. FeedMob's GitHub space), the following needs configurable defaults and mirroring — just like Linear onboarding does today:
>
> - **GitHub default labels** — map Linear labels to GitHub labels (e.g. Linear "Rachel lu" → GitHub "rachel-lu"). Requires org-level label setup.
> - **GitHub default assignees** — map Linear users to GitHub usernames. Requires a user mapping table.
> - **GitHub Projects** — map Linear projects to GitHub Projects (v2). Requires project setup in the org.
> - **Org-level onboarding** — when the repo lives under a team org (not personal), an additional onboarding step should discover org members, org labels, and org projects, then let the user choose defaults — same pattern as Linear onboarding.
>
> For now (MVP with personal GitHub), this is deferred. Only comments are mirrored; labels/assignees/projects are managed on Linear.

### Linear Comment (use `linear` skill CLI helper)

```bash
# Preferred: use the linear skill's Python CLI
SCRIPT=$(find ~/.hermes -path '*skills/productivity/linear/scripts/linear_api.py' 2>/dev/null | head -1)
python3 "$SCRIPT" add-comment AI-1972 --body "Starting work. Branch: linear/ai-1972-add-login. Next: review auth flow."
```

### Linear Status Update (use `linear` skill CLI helper)

```bash
# Preferred: use the linear skill's Python CLI
python3 "$SCRIPT" update-status AI-1972 --state "In Progress"
# Or by stateId (UUID):
python3 "$SCRIPT" update-status AI-1972 --state-id "<STATE_UUID>"
```

> **Note:** The `linear` skill CLI handles state name → stateId resolution automatically.
> For raw GraphQL or edge cases not covered by the CLI, fall back to curl patterns
> documented in the `linear` skill.

## State Flow

Default state movement:

```text
Backlog/Todo → In Progress → In Review → Done
```

- Use `Done` only when the user requested direct completion and verification passed.
- Use `In Review` when a PR or human check is expected.
- Do not change state if: the issue belongs to another assignee without consent,
  required credentials/decisions are missing, or verification could not run.

Read `references/state-model.md` for status mapping and custom team states.

## GitHub Sync

GitHub plays two roles in this workflow. **Issue sync is the core; PR/branch is optional.**

### 1. GitHub Issue (progress mirror) — core, always do this

- Created alongside each Linear issue (1:1 mapping)
- Mirrors all progress comments from Linear
- Keeps GitHub-side team members in the loop
- This is the **primary purpose** of GitHub in this workflow

### 2. GitHub Code Artifacts (optional, only when code is involved)

Only create branches/commits/PRs when the issue involves actual code work. Many issues
(research, discussion, planning, documentation) don't need code at all — just use issue + comments.

When code IS involved:
- Create a branch: `linear/<issue-id>-<short-slug>`
- Commit with issue ID in message
- Open PR with Linear issue link in body
- Include the Linear issue ID in branch names, commit messages, PR titles

Read `references/github-conventions.md` for the Linear-specific branch/commit/PR conventions.
For the full GitHub mechanics (clone, create repo, push, create PR, monitor CI, merge),
load the `github-repo-management` and `github-pr-workflow` skills.

## Team Visibility

When the user asks to see coworker status:
- List Linear users and teams.
- Query issues by assignee, team, status, label, project, and updated time.
- Summarize by person: active, blocked, recently done, stale.
- Do not modify coworker-owned issues unless explicitly requested.

## Credential Rules

- Ask for credentials only at the moment they are needed.
- Treat tokens as one-time secrets. Never store in files, git, comments, logs, or commits.
- Do not print tokens back to the user.
- Store stable non-secret defaults (user IDs, workspace/team IDs, org/repo names,
  branch conventions) only after explicit confirmation.
- Reuse saved defaults silently on future runs, but revalidate when auth fails or
  the user says defaults changed.

## Pitfalls

### Linear free plan — active issue limit

Linear free-tier workspaces have a cap on **active issues**. When the limit is reached, `issueCreate` returns:

```json
{
  "errors": [{
    "extensions": {
      "code": "USAGE_LIMIT_EXCEEDED",
      "meta": { "usageMetric": "activeIssueCount" }
    }
  }]
}
```

**Before creating issues during onboarding or MVP demos**, check the workspace is not at capacity. If it is, the user must archive/close existing issues or upgrade the plan. Do not retry `issueCreate` after this error — it will keep failing until the workspace is under quota.

### Codex CLI — sandbox blocks network by default

Codex CLI runs in a sandbox with **network access off** by default. Linear/GitHub API
calls fail with DNS errors, and escalation requests get auto-rejected.

**Fix:** Set Codex's approval policy to default-permit (Auto Review → default permissions),
or launch with `--full-auto`:

```bash
codex --full-auto "Use ticket-pilot on AI-2090"
```

This is a Codex-wide sandbox setting — other agents don't have this issue.

### Settings auto-discovery

During onboarding, **proactively query** the workspace to auto-fill settings rather than asking the user to type IDs. Query in this order:

1. `viewer { id name email }` — confirm identity
2. `teams { nodes { id name key } }` — get team keys/IDs
3. `workflowStates(filter: { team: { key: { eq: "KEY" } } })` — get status UUIDs for the default team
4. `issueLabels(first: 30)` — discover available labels
5. `projects(first: 20)` — list projects

Present the discovered values and let the user confirm rather than blank-prompting for each one.

## Stop Conditions

Stop and ask the user when:
- A required UI-only action is needed.
- A credential is needed.
- A deploy target cannot see the repo.
- A service remains unhealthy after two retries.
- A permission error changes the trust model.
- Continuing would reassign someone else's issue or publish private material.

When stopping, leave a Linear comment if Linear is available:

```text
Blocked at <step>. Symptom: <observed>. Error: <message>. Need you to check <specific thing>.
```

## Auth Detection

GitHub auth is auto-detected at runtime. The skill should check in this priority order:

```bash
if command -v gh &>/dev/null && gh auth status &>/dev/null; then
  AUTH="gh"        # use gh CLI for everything
elif [ -n "$GITHUB_TOKEN" ]; then
  AUTH="token"     # use curl + GITHUB_TOKEN
else
  AUTH="none"      # present options to user: gh CLI or PAT
fi
```

When `AUTH="none"`, offer both paths and let the user choose — do not force one method.

## Team Naming Conventions

When creating issues, always follow the target team's existing naming pattern. Before creating your first issue on a team, query recent issues to learn the pattern.

FeedMob ken-team (AI) pattern (discovered 2026-06-13):

```text
#YYYYMMDD-NameN 描述内容
```

Examples:
- `#20260613-RachelLu-1 Ticket Pilot — Linear issue 自动同步更新的标准化 skill`
- `#20260612-Leo03 YouTube调控，每天发一篇最有价值的`
- `#20260610-Windy02 要把Rachel Lu 加进来会议说工作情况`

Description body starts with:
```text
提出日期: YYYY-MM-DD
备注: 来源：... Action（... 值日）。
```

For other teams or workspaces, **always sample 10+ recent issues first** to detect the pattern before creating.

## Full Workflow Checklist

The end-to-end cycle. Steps 1-4 and 9-10 are **always** done (core issue sync). Steps 5-8 are **only when code is involved**.

**Core (always):**
1. **Create Linear issue** (or resolve existing) — follow team naming convention, apply user's label + assignee
2. **Create linked GitHub issue** — same title with Linear ID, body links back to Linear
3. **Status → In Progress** — Linear only (query workflow states first to get stateId)
4. **Start comment** — post to **both** Linear and GitHub issue (scope, first step)

**Code artifacts (optional, only if writing code):**
5. **Create GitHub branch** — `linear/<issue-id>-<slug>` from latest main
6. **Do work + commit** — include issue ID in commit message
7. **Key node comment** — post to **both** platforms (commit hash, file list, what's done)
8. **Push branch + open PR** — draft by default, include Linear issue link in body

**Close (always):**
9. **Status → In Review or Done** — Linear only
10. **Completion comment** — post to **both** platforms (PR URL if applicable, verification, remaining steps)

See `references/workflow-template.md` for the full MVP transcript with exact API calls.

## Resources

- `scripts/sync_comment.py` — post a progress comment to BOTH Linear and GitHub issue in one call.
- `scripts/init_task_record.py` — create a task artifact folder for a Linear issue.
- `references/onboarding-settings.md` — first-run onboarding and settings format.
- `references/state-model.md` — status mapping and comment rules.
- `references/github-conventions.md` — branch, commit, PR, and task artifact conventions.
- `references/workflow-template.md` — full-cycle workflow with exact API calls (includes bidirectional comment mirroring).
