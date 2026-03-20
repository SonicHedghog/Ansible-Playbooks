# Tool references

## python
- Role in workflow:
  - Executes provider-agnostic pipeline inspection script.
- Command shape used:
  - python scripts/fetch_pipeline.py --url <pipeline-url> [--max-jobs <n>] [--output-json <path>] [--output-md <path>]
- Important arguments:
  - --url: required pipeline URL.
  - --max-jobs: max jobs to inspect, default 25.
  - --output-json: optional artifact output path.
  - --output-md: optional markdown output path.
- Inputs and outputs:
  - Input URL and optional limits.
  - Outputs normalized JSON to stdout and optional files.
- Error behavior:
  - Non-zero exit on invalid URL, provider API failures, or auth failures.

## git
- Role in workflow:
  - Branch management, commit, and push for selected fix.
- Command shapes used:
  - git checkout -b <branch-name>
  - git checkout <branch-name>
  - git status --short --branch
  - git add <paths>
  - git commit -m "fix(ci): resolve <short signature>"
  - git push --set-upstream origin <branch-name>
  - git push
- Important arguments:
  - -b creates a new branch.
  - --set-upstream sets tracking on first push.
- Inputs and outputs:
  - Operates on the local working tree and remote origin.
- Error behavior and common failures:
  - Branch already exists, no staged changes, missing remote auth, branch protection failures.

## requests library
- Role in workflow:
  - Performs REST API calls to GitHub and GitLab endpoints.
- API usage shape in scripts:
  - requests.request(method, url, headers=..., params=..., timeout=30)
- Important defaults:
  - 30 second timeout.
  - Provider token injected via headers.
- Inputs and outputs:
  - Input URL, auth headers, optional query params.
  - Output JSON metadata and raw log text.
- Error behavior:
  - HTTP status >= 400 raises provider-specific runtime errors.

## Provider tokens
- Role in workflow:
  - Authorize REST API access to pipeline and job log data.
- Variables:
  - GITHUB_TOKEN required for GitHub URLs.
  - GITLAB_TOKEN required for GitLab URLs.
- Safety:
  - Tokens must never be printed or persisted in generated artifacts.
