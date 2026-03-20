---
name: research-issue
description: Research a GitHub/GitLab issue and summarize context for implementation.
---
# /research-issue Skill

## Purpose
`/research-issue` performs preliminary research for a GitHub or GitLab issue URL by extracting the underlying technical topic(s), researching those topics, capturing reusable knowledge, and drafting an issue comment that applies the topic knowledge to the specific issue.

This skill interoperates across GitHub and GitLab by auto-detecting provider from the issue URL, using shared normalized metadata, and using provider-specific API calls for reads/writes.

## Invocation
- Primary: `/research-issue <issue-url> [focus text]`
- Interactive fallback: `/research-issue`, then prompt for URL and optional focus text.

## Inputs
- Required: issue URL (GitHub or GitLab issue URL)
- Optional: focus text (for example: architecture, risk, rollout, testing)

## Outputs
- Chat summary with topic-oriented findings plus issue-specific application guidance.
- Persisted research notes in knowledge docs (through `knowledge-base` and `learn`) for general topics only.
- Draft issue comment for user review.
- Posted issue comment only after explicit confirmation.

## Step-by-step workflow
1. Resolve input:
   - If no URL argument was provided, ask for one.
   - Ask for optional focus text if not provided.
2. Fetch normalized issue metadata:
   - Run `python scripts/fetch_issue.py --url <issue-url>`.
3. Extract topic candidates from the issue:
   - Use issue title/body to identify 1-3 technical topics (for example: Renovate, dependency update policy, CI update safety).
   - Keep topic names general and reusable across issues.
4. Build topic knowledge context:
   - Search existing docs first via `knowledge-base` for each topic.
   - If context is missing or stale, invoke `learn` on topic-focused public sources (official docs, trustworthy references).
   - Do not invoke `learn` on the issue URL itself for knowledge-base content.
5. Produce research summary:
   - Separate output into:
     - Topic knowledge (general): definitions, concepts, setup/options, caveats.
     - Issue application (specific): how the topic knowledge should be applied to this issue.
5. Draft issue comment:
   - Run `python scripts/research_issue.py --url <issue-url> --summary-file <path-to-summary.md> --output-draft -`.
   - Show draft comment to user.
6. Confirm posting:
   - Ask for explicit approval before posting.
   - If approved, run `python scripts/research_issue.py --url <issue-url> --summary-file <path-to-summary.md> --post`.
   - If not approved, stop after draft.

## Safety rules
- Never post to an issue without explicit user confirmation in the current session.
- Never mutate labels, assignees, milestones, or issue state; this skill only reads and comments.
- Fail fast on unsupported URLs, malformed inputs, or missing provider token.
- Do not claim posting succeeded unless API response confirms success.
- Never store issue-specific implementation plans in the knowledge base; only store reusable topic knowledge.

## Environment variables
- `GITHUB_TOKEN` (required for GitHub URLs)
- `GITLAB_TOKEN` (required for GitLab URLs)

Validation rules:
- Detect provider from URL first.
- Require only the token for the detected provider.
- Exit with error if the required token is missing.

## Out of scope
- Creating branches/PRs/MRs.
- Code changes or implementation execution.
- Project management edits (labels, status, assignment).
- Bulk research across multiple issues in one invocation.
- Persisting issue-specific tactical plans as general knowledge docs.

## Integration contract
- The agent must run provider scripts from this skill root.
- The agent must use `knowledge-base` before `learn` when possible.
- The agent must direct `learn` to topic-level sources, not to the issue page as a knowledge source.
- The agent must always surface a draft comment and request confirmation before posting.
- The agent should keep posted comments concise and implementation-focused.

## References
- See `references/tools.md` for CLI tools and skill integrations.
- See `references/scripts.md` for script interfaces and behavior.
- Assets used by this skill:
  - `assets/templates/comment-template.md`
  - `assets/examples/research-summary-example.md`
