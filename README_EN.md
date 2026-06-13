# Ticket Pilot 🎫✈️

**Multi-agent skill for Linear ↔ GitHub issue sync.**

Ticket Pilot lets any AI agent (Hermes, Claude Code, Codex, OpenClaw, Cursor, Gemini CLI) coordinate Linear issue work with GitHub-backed tracking. When you work on a Linear issue, the agent automatically:

- Creates a linked GitHub issue (1:1 mirror)
- Posts progress comments to **both** platforms at phase boundaries
- Tracks status on Linear (source of truth)
- Optionally creates branches/PRs when code is involved

## Installation

### Option 1: curl one-liner (recommended)

```bash
# Default: install to Claude Code
curl -fsSL https://raw.githubusercontent.com/RachelXiaolan/ticket-pilot/main/install.sh | bash

# Specify agent (comma-separated for multiple)
curl -fsSL https://raw.githubusercontent.com/RachelXiaolan/ticket-pilot/main/install.sh | bash -s -- --agent hermes
curl -fsSL https://raw.githubusercontent.com/RachelXiaolan/ticket-pilot/main/install.sh | bash -s -- --agent claude,codex,hermes
```

Available agents: `claude` `codex` `hermes` `openclaw` `cursor` `gemini`

### Option 2: Claude Code plugin marketplace

```
/plugin marketplace add RachelXiaolan/ticket-pilot
/plugin install ticket-pilot
```

### Option 3: skills.sh CLI

```bash
npx skills add RachelXiaolan/ticket-pilot
```

### Option 4: Manual

```bash
git clone https://github.com/RachelXiaolan/ticket-pilot.git
cp -r ticket-pilot/ ~/.claude/skills/ticket-pilot/    # swap in your agent's path
```

| Agent | Skills directory |
|-------|-----------------|
| Claude Code | `~/.claude/skills/` |
| Codex | `~/.codex/skills/` |
| Hermes | `~/.hermes/skills/productivity/` |
| OpenClaw | `~/.openclaw/skills/` |
| Cursor | `.cursor/skills/` |
| Gemini CLI | `.gemini/skills/` |

## Prerequisites

### Linear
- Personal API key from https://linear.app/settings/account/security → Personal API keys
- Set as `LINEAR_API_KEY` environment variable

### GitHub (any one)
- **gh CLI** (preferred): `gh auth login`
- **Personal Access Token**: set as `GITHUB_TOKEN`
- **GitHub MCP / App**: if already configured

## First Run

When you first use Ticket Pilot, the agent will:
1. Verify Linear + GitHub auth
2. Auto-discover your workspace: teams, projects, labels, users
3. Ask you to choose defaults (team, project, label, assignee)
4. Save to `~/.ticket-pilot/settings.md`

After that, creating issues uses your defaults automatically. Override anytime by specifying explicitly.

## How It Works

```
Linear Issue (source of truth)
  ├── status / priority / assignee / label
  ├── progress comments ──→ mirrored to GitHub issue
  │
  └── ←── links ──→ GitHub Issue (mirror)
                        ├── same comments
                        ├── (optional) branch + commit + PR
                        └── (optional) labels / assignees
```

### Comment style
- **Phase-based, not prompt-based** — group related steps, comment when a phase ends
- **Every comment includes**: who did it (agent name), what happened, key outputs (links)
- Concise and scannable. No walls of text.

### Issue creation
- Follows your team's naming convention (auto-detected)
- Applies your default label + assignee
- Creates GitHub issue simultaneously with link back to Linear

## Supported Agents

Ticket Pilot uses the [Agent Skills open standard](https://github.com/anthropics/skills) (`SKILL.md` + YAML frontmatter). Any agent that supports this standard can use it.

| Agent | Skills directory | Activation |
|-------|-----------------|------------|
| Claude Code | `~/.claude/skills/` | Native |
| OpenAI Codex | `~/.codex/skills/` | Auto-discovery |
| Hermes Agent | `~/.hermes/skills/` | Native |
| OpenClaw | `~/.openclaw/skills/` | YAML frontmatter triggers |
| Cursor | `.cursor/skills/` | `@ticket-pilot` |
| Gemini CLI | `.gemini/skills/` | `activate_skill()` |

## File Structure

```
ticket-pilot/
├── SKILL.md                          # Main skill instructions
├── README.md                         # This file
├── references/
│   ├── onboarding-settings.md        # First-run setup format
│   ├── state-model.md                # Linear status mapping
│   ├── github-conventions.md         # Branch/commit/PR conventions
│   └── workflow-template.md          # Validated workflow examples
└── scripts/
    ├── init_task_record.py           # Task artifact skeleton
    └── sync_comment.py               # Post comment to both platforms
```

## Auth Compatibility

| Agent | Linear | GitHub |
|-------|--------|--------|
| All agents | `$LINEAR_API_KEY` (env var) | `$GITHUB_TOKEN` (env var) or `gh auth` (CLI) |

The skill auto-detects which GitHub auth method is available and uses it. No agent-specific configuration needed.

## License

MIT

## Author

Rachel Lu (@RachelXiaolan)
