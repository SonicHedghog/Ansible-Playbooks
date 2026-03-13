---
name: work-issue
description: Automate work issue creation and management. Use this skill to create, update, and track GitHub issues from natural language requests. Ideal for converting chat messages into structured issue tickets.
---
# /work-issue Skill

## Purpose
`/work-issue` helps an agent start work from a GitHub or GitLab issue by:
1. Fetching normalized issue metadata.
2. Asking the user for a branch name.
3. Creating and pushing the branch.
4. Starting interactive implementation work.
5. Opening and assigning a PR/MR only after commits exist on the branch.
6. Editing the PR/MR title or description when needed.

Run all scripts from this files's directory.

## Step-by-step workflow
1. Run `python scripts/fetch_issue.py --url <issue-url>`.
2. Agent analyzes normalized issue metadata.
3. Agent asks user for branch name (suggesting a default).
4. Run `python scripts/setup_branch.py --issue-json <issue.json|-> --branch-name <name>`.
5. Agent begins working the issue.
6. Agent commits/pushes only after user confirmation.
7. Re-run `setup_branch.py` after commits to create/assign PR/MR.
8. Optionally run `python scripts/edit_pr.py --issue-json <issue.json|-> --branch-name <name> [--title ...] [--body ...]` to update PR/MR.

## Instructions for the agent
- Never submit code without explicit user approval.
- Always ask for branch name before running `setup_branch.py`.
- Work interactively and request clarification when requirements are ambiguous.

## Agent workflow sequence
### Step 1 — Fetch issue
- Run `fetch_issue.py` with the provided issue URL.
- Parse JSON output.

### Step 2 — Ask user for branch name
- Suggest a default name.
- Accept user override.

### Step 3 — Create branch + PR/MR
- Run `setup_branch.py` with issue metadata JSON and the user-selected branch name to create/push the branch.
- `setup_branch.py` must not create a PR/MR if the branch has no commits ahead of default.

### Step 4 — Begin working the issue
- Analyze issue description.
- Inspect relevant files.
- Propose changes.
- Ask for clarification when needed.

### Step 5 — Finalize
- Show final diff.
- Ask for confirmation.
- Commit + push changes.
- Re-run `setup_branch.py` to create/assign PR/MR if it does not exist yet.
- Run `edit_pr.py` to update PR/MR description/title if needed.

## Copilot integration contract
- Skill invocation: `/work-issue <url>`.
- Copilot must run scripts in the required order.
- Copilot must ask for branch name before running `setup_branch.py`.
- Copilot must not push code without explicit user approval.
- Copilot must not create a PR/MR until branch commits exist.
