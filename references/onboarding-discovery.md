# Onboarding Discovery Queries

Step-by-step recipe for discovering the user's Linear context during first-run onboarding.
Use the `linear` skill's Python CLI helper (`scripts/linear_api.py`) when available —
it wraps these queries. Fall back to raw curl/GraphQL if the CLI is unavailable.

## Step 1: Verify identity

```bash
# CLI helper
python3 linear_api.py whoami

# Raw GraphQL
curl -s -X POST https://api.linear.app/graphql \
  -H "Authorization: $LINEAR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "{ viewer { id name email } }"}' | python3 -m json.tool
```

Record: user name, email, user ID.

## Step 2: List teams

```bash
python3 linear_api.py list-teams

# Raw
curl -s -X POST https://api.linear.app/graphql \
  -H "Authorization: $LINEAR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "{ teams { nodes { id name key } } }"}' | python3 -m json.tool
```

Record: default team name, key, ID. Ask the user which is their primary team.

## Step 3: List workflow states for the default team

```bash
python3 linear_api.py list-states --team-key <KEY>

# Raw
curl -s -X POST https://api.linear.app/graphql \
  -H "Authorization: $LINEAR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "{ workflowStates(filter: { team: { key: { eq: \"<KEY>\" } } }) { nodes { id name type } } }"}' \
  | python3 -m json.tool
```

Record: state IDs for each intent (started → In Progress, review → In Review,
completed → Done). Map by `type` field if names differ.

## Step 4: List projects (optional)

```bash
python3 linear_api.py list-projects
```

Record: default project if one is relevant.

## Step 5: List labels

```bash
# Raw (no CLI wrapper for labels)
curl -s -X POST https://api.linear.app/graphql \
  -H "Authorization: $LINEAR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "{ issueLabels { nodes { id name color } } }"}' | python3 -m json.tool
```

Record: default label IDs (e.g. user name as label).

## Step 6: Verify GitHub access

```bash
# Option A: gh CLI
gh auth status
GH_USER=$(gh api user --jq '.login')

# Option B: PAT
curl -s -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/user | python3 -c "import sys,json; print(json.load(sys.stdin)['login'])"
```

Record: GitHub username/org, auth method in use (gh vs token vs mcp).

## Step 7: Write settings.md

Present all discovered values to the user for confirmation, then write to
`~/.agent-linear-github/settings.md` using the format in `references/onboarding-settings.md`.

## Onboarding defaults reference (FeedMob example)

These are the proposed defaults for Rachel's FeedMob workspace. They are NOT written
to settings.md until the user explicitly confirms them.

```text
Linear workspace: feedmob
Linear user: Rachel Lu
Linear email: rachel.lu@feedmob.com
Default team: ken-team
Default label: Rachel
Start status: In Progress
Review status: In Review
Complete status: Done

GitHub owner/org: feed-mob
Default repository: ask
Branch prefix: linear/
PR policy: draft
Auto-move status on start: yes
Auto-move status on completion: In Review
```
