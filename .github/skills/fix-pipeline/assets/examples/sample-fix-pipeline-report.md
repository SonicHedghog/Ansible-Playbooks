# fix-pipeline report

## Pipeline
- provider: github
- repository: acme/widgets
- pipeline url: https://github.com/acme/widgets/actions/runs/1234567890
- branch: feature/fix-lint
- sha: 5b91f925f2f8b2ab8f2de80b995a6dd4cb55de01
- status: completed

## Error signature groups
### Group 1
- signature: src/api/client.py:42:1: F401 'json' imported but unused
- occurrences: 2
- jobs:
  - lint | stage=lint | status=failure
  - lint-macos | stage=lint-macos | status=failure

## Recommended next step
Ask the user which error signature group to fix first, then scope edits to that group.

## Code quality reports
- Import 'json' is unused
  severity: warning
  path: src/api/client.py

## Security reports
- requests
  severity: high
  description: Requests library vulnerable to potential security issue
