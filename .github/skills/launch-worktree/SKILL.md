---
name: launch-worktree
description: Run user-requested implementation tasks inside a git worktree created in the parent directory of the project, then remove that worktree after explicit user confirmation.
---
# /launch-worktree Skill

## Purpose
`/launch-worktree` helps an agent complete implementation work in an isolated git worktree by:
1. Collecting the requested task and branch name.
2. Creating (or reusing) a worktree in the parent directory of the project folder.
3. Performing all requested work inside that worktree path.
4. Showing diffs/status for user review.
5. Removing the worktree only after explicit user confirmation.

## Step-by-step workflow
1. Ask the user what should be implemented and confirm the target branch name.
2. Resolve paths:
- Repo root: `git rev-parse --show-toplevel`
- Project folder name: basename of repo root
- Parent folder: parent of repo root
- Worktree folder: `<parent>/<project>-worktree`
- Alternate worktree folder pattern: `<parent>/<project>-worktree-<suffix>`
3. Ensure default branch reference is available:
- `git fetch origin`
- Determine default branch from `origin/HEAD` (for example `origin/main`).
4. Create or switch worktree:
- If worktree path does not exist: `git worktree add -b <branch-name> <worktree-path> <default-branch>`.
- If it exists and is valid, ask the user to choose one of these options:
- Reuse existing worktree: run `git -C <worktree-path> checkout <branch-name>` (or create branch there if needed).
- Create another worktree: ask for a suffix or name, build `<project>-worktree-<suffix>`, and run `git worktree add -b <branch-name> <alternate-worktree-path> <default-branch>`.
5. Perform all user-requested edits, tests, and validation from the selected worktree path.
6. Present results with:
- `git -C <worktree-path> status --short --branch`
- `git -C <worktree-path> diff`
7. Ask the user to confirm completion.
8. After explicit confirmation, remove the worktree:
- `git worktree remove <worktree-path>`
- Optionally run `git worktree prune`.

## Git commands the agent should run directly
- List worktrees: `git worktree list`
- Add worktree + branch: `git worktree add -b <branch-name> <worktree-path> <start-point>`
- Add second worktree + branch: `git worktree add -b <branch-name> <alternate-worktree-path> <start-point>`
- Checkout existing branch in worktree: `git -C <worktree-path> checkout <branch-name>`
- Show worktree status: `git -C <worktree-path> status --short --branch`
- Show worktree diff: `git -C <worktree-path> diff`
- Remove worktree: `git worktree remove <worktree-path>`
- Prune metadata: `git worktree prune`

## Safety and behavior rules
- Always ask for branch name before branch-related commands.
- Keep all implementation work scoped to the worktree path once created.
- If a default worktree already exists, ask whether to reuse it or create another one.
- Never delete the worktree without explicit user confirmation.
- Never commit or push without explicit user approval.
- If worktree removal fails because of uncommitted changes, show status and ask the user how to proceed.

## Agent integration contract
- Skill invocation: `/launch-worktree <task>`.
- Agent must create the worktree in the parent of the project folder.
- Agent must support creating an additional worktree path when one already exists.
- Agent must do implementation work in that worktree path.
- Agent must ask for completion confirmation before deleting the worktree.
