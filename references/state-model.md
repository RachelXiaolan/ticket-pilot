# Linear State Model

## Status Types

Linear uses `WorkflowState` objects with a `type` field. **6 state types:**

| Type | Description |
|------|-------------|
| `triage` | Incoming issues needing review |
| `backlog` | Acknowledged but not yet planned |
| `unstarted` | Planned/ready but not started |
| `started` | Actively being worked on |
| `completed` | Done |
| `canceled` | Won't do |

Each team has its own named states. To change an issue's status, you need the `stateId` (UUID) of the target state.

### Query workflow states for a team

```bash
curl -s -X POST https://api.linear.app/graphql \
  -H "Authorization: $LINEAR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "{ workflowStates(filter: { team: { key: { eq: \"ENG\" } } }) { nodes { id name type } } }"}' \
  | python3 -m json.tool
```

## Default Mapping

Map by status type when exact names differ:

| Intent | Preferred name | Linear status type |
|--------|---------------|-------------------|
| Not started | Backlog or Todo | backlog / unstarted |
| Working | In Progress | started |
| Human review | In Review | started |
| Complete | Done | completed |
| Paused | Canceled or Blocked | canceled / custom |

Always list team statuses before updating an unfamiliar team.

## Comment Contract

Every issue workflow should leave comments at these points:

### 1. Start comment
- Issue accepted
- Repo and branch
- Immediate next step

### 2. Key node comments
- Implementation milestone
- Test result
- Deploy attempt
- External dependency

### 3. Blocker comment
- Exact symptom
- Exact error or log source
- What the user must inspect

### 4. Completion comment
- PR URL or commit hash
- Verification commands and result
- Remaining risks

## Completion Rules

Use `In Review` when:
- A PR exists and needs review.
- Deployment needs human confirmation.
- Verification passed locally but production verification is pending.

Use `Done` when:
- The requested work is complete.
- Verification passed.
- No PR/review/deploy check remains.

Do not mark `Done` only because code was pushed.
