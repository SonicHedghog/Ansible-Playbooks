---
name: work-issue
description: Automate work issue creation and management. Use this skill to create, update, and track GitHub issues from natural language requests. Ideal for converting chat messages into structured issue tickets.
---
# /work-issue Skill

## Purpose
`/work-issue` helps an agent start work from a GitHub or GitLab issue by:
1. Fetching normalized issue metadata.
2. Asking the user for a branch name.
3. Creating and pushing the branch with direct git commands.
4. Starting interactive implementation work.
5. Opening and assigning a PR/MR only after commits exist on the branch.
6. Editing the PR/MR title or description when needed.

Run all scripts from this file's directory.

## Step-by-step workflow
1. Run `python scripts/fetch_issue.py --url <issue-url>`.
2. Agent analyzes normalized issue metadata.
3. Agent asks user for branch name (suggesting a default).
4. Create/switch branch with git: `git checkout -b <name>` (or `git checkout <name>` if it exists).
5. Push branch with git: `git push --set-upstream origin <name>` (or `git push` if upstream exists).
6. Agent begins working the issue.
7. Agent commits/pushes only after user confirmation.
8. Run `python scripts/setup_branch.py --issue-json <issue.json|-> --branch-name <name>` after commits to create/assign PR/MR.
9. Optionally run `python scripts/edit_pr.py --issue-json <issue.json|-> --branch-name <name> [--title ...] [--body ...]` to update PR/MR.

## Script reference
- `fetch_issue.py`: Fetches provider issue metadata and prints normalized issue JSON.
	Command: `python scripts/fetch_issue.py --url <issue-url>`
- `setup_branch.py`: Ensures PR/MR exists and is assigned for a branch only when the branch is ahead of default.
	Command: `python scripts/setup_branch.py --issue-json <issue.json|-> --branch-name <name>`
- `edit_pr.py`: Updates the open PR/MR title/body for a branch.
	Command: `python scripts/edit_pr.py --issue-json <issue.json|-> --branch-name <name> [--title ...] [--body ...]`

## Git commands the agent should run directly
- Create branch: `git checkout -b <branch-name>`
- Switch to existing branch: `git checkout <branch-name>`
- Push first time: `git push --set-upstream origin <branch-name>`
- Push updates: `git push`
- Show status: `git status --short --branch`
- Show local commits ahead: `git rev-list --count origin/HEAD..<branch-name>`

## Instructions for the agent
- Never submit code without explicit user approval.
- Always ask for branch name before running branch-related git commands.
- Work interactively and request clarification when requirements are ambiguous.

## Agent workflow sequence
### Step 1 — Fetch issue
- Run `fetch_issue.py` with the provided issue URL.
- Parse JSON output.

### Step 2 — Ask user for branch name
- Suggest a default name.
- Accept user override.

### Step 3 — Create branch + PR/MR
- Run git commands directly to create/switch and push the user-selected branch.
- Run `setup_branch.py` only after commits exist; it must not create a PR/MR if the branch has no commits ahead of default.

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

## Agent integration contract
- Skill invocation: `/work-issue <url>`.
- Agent must run scripts in the required order and run git commands directly for branch operations.
- Agent must ask for branch name before running branch-related commands.
- Agent must not push code without explicit user approval.
- Agent must not create a PR/MR until branch commits exist.
