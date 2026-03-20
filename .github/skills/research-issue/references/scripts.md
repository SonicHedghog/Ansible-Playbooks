# Script reference

## scripts/fetch_issue.py
- Purpose: Detect provider from URL and print normalized issue metadata JSON.
- Command: `python scripts/fetch_issue.py --url <issue-url>`
- Flags:
  - `--url` (required): GitHub/GitLab issue URL.
- Output: JSON with `provider`, `repo`, `issue_number`, `title`, `description`, `labels`, and `web_url`.
- Errors: unsupported provider URL, malformed URL, missing provider token, API errors.

## scripts/research_issue.py
- Purpose: Build draft issue research comment from topic research plus issue-specific application notes, and optionally post it.
- Commands:
  - Draft to stdout: `python scripts/research_issue.py --url <issue-url> --summary-file <path> --output-draft -`
  - Draft to file: `python scripts/research_issue.py --url <issue-url> --summary-file <path> --output-draft <path>`
  - Post comment: `python scripts/research_issue.py --url <issue-url> --summary-file <path> --post`
- Flags:
  - `--url` (required): Issue URL.
  - `--summary-file` (required): Markdown/text source that should include:
    - topic knowledge (general, reusable)
    - issue application guidance (specific to the issue)
  - `--output-draft` (optional): `-` for stdout or a file path.
  - `--post` (optional): Posts comment to provider issue endpoint.
- Output: Draft comment text/path and posted comment URL when `--post` is used.
- Errors: missing/empty summary file, unsupported URL, missing provider token, provider API errors.

## Research content contract
- Knowledge-base persistence must include only topic knowledge.
- Issue-specific recommendations, rollout sequence, and implementation tactics should remain in comment drafts and chat output.

## scripts/git_providers/github.py
- Purpose: GitHub issue metadata and issue comment operations.
- Used by: `fetch_issue.py`, `research_issue.py`.
- Env: requires `GITHUB_TOKEN`.

## scripts/git_providers/gitlab.py
- Purpose: GitLab issue metadata and issue comment operations.
- Used by: `fetch_issue.py`, `research_issue.py`.
- Env: requires `GITLAB_TOKEN`.

## scripts/utils/env_loader.py
- Purpose: Load `.env` values by searching current directory and parent directories.
- Used by: `fetch_issue.py`, `research_issue.py`.

## scripts/utils/normalize.py
- Purpose: Normalize provider issue metadata into a shared schema for downstream processing.
- Used by: `fetch_issue.py`, `research_issue.py`.
