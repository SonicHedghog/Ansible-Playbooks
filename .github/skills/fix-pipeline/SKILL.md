---
name: fix-pipeline
description: Analyze a GitHub Actions or GitLab pipeline URL, group failing jobs by error signature, and guide a safe branch fix workflow.
---
# /fix-pipeline Skill

## Purpose
/fix-pipeline helps an agent start from a pipeline URL and complete a safe repair loop:
1. Fetch and normalize pipeline metadata from GitHub Actions or GitLab CI.
2. Identify failed jobs and extract error signatures from logs.
3. Group failures by signature so the highest-impact issue is visible first.
4. Let the user choose which grouped issue to solve.
5. Create or switch to the target branch, implement a focused fix, and push only after user confirmation.
6. Save both machine-readable and human-readable run artifacts.

Run scripts from this skill root.

## Invocation
- /fix-pipeline <pipeline-url>
- Optional overrides:
  - --branch <name>
  - --max-jobs <n>

## Step-by-step workflow
1. Run:
   python scripts/fetch_pipeline.py --url <pipeline-url> --max-jobs <n> --output-json assets/reports/latest-fix-pipeline.json --output-md assets/reports/latest-fix-pipeline.md
2. Parse normalized output and validate that failed jobs were detected.
3. Present grouped signatures ordered by highest occurrence count.
4. Ask the user to choose a failure group to fix first.
5. Resolve branch name:
   - Use --branch if provided.
   - Otherwise default to the pipeline branch from normalized output.
6. Create or switch branch with git:
   - git checkout -b <branch-name> (new)
   - git checkout <branch-name> (existing)
7. Implement a targeted fix only for the chosen signature group.
8. Show diff and test evidence to the user.
9. Ask once for explicit confirmation before commit and push.
10. If confirmed:
   - git add <paths>
   - git commit -m "fix(ci): resolve <short signature>"
   - git push --set-upstream origin <branch-name> (first push)
   - git push (subsequent pushes)
11. Print a final summary including branch, commit, pushed status, and artifact file paths.

## Inputs
- Required:
  - Pipeline URL for GitHub or GitLab.
- Optional:
  - Branch override.
  - Max jobs to inspect.

## Outputs and artifacts
- Terminal summary:
  - provider, pipeline, chosen signature group, changed files, commit, push status.
- JSON artifact:
  - assets/reports/latest-fix-pipeline.json
- Markdown artifact:
  - assets/reports/latest-fix-pipeline.md

## Environment variables
- Required by provider:
  - GITHUB_TOKEN for GitHub pipeline URLs.
  - GITLAB_TOKEN for GitLab pipeline URLs.
- Validation rules:
  - Fail fast if required provider token is missing.
  - Never print token values in terminal, logs, or artifacts.

## Script reference
- fetch_pipeline.py
  - Purpose: fetches provider pipeline metadata, failed jobs, logs, and grouped signatures.
  - Command:
    - python scripts/fetch_pipeline.py --url <pipeline-url> [--max-jobs <n>] [--output-json <path>] [--output-md <path>]

## Safety and confirmation rules
- Never do the following unless user explicitly permits it:
  - Push to default or protected branches.
  - Force-push.
  - Modify CI config files when not directly related to chosen failure signature.
  - Run destructive git commands such as reset --hard, clean -fd, or history rewrites.
  - Auto-close issues or auto-merge PR/MR.
- Require one explicit confirmation gate before commit and push.

## Scope and out-of-scope
In scope:
- Single pipeline diagnosis from URL.
- Signature grouping and user-selected fix targeting.
- Safe branch-based fix and push workflow.

Out of scope for v1:
- Automatic pipeline reruns unless user asks.
- Broad dependency upgrades unrelated to selected signature.
- Multi-repository fanout fixes.
- Infrastructure provisioning changes.
- Automatic PR/MR creation or merging.

## Example prompts
- /fix-pipeline https://github.com/org/repo/actions/runs/1234567890
- /fix-pipeline https://gitlab.com/group/project/-/pipelines/987654 --branch fix/pipeline-987654
- /fix-pipeline https://github.com/org/repo/actions/runs/1234567890 --max-jobs 25

## Agent integration contract
- Invocation shape:
  - /fix-pipeline <pipeline-url> [--branch <name>] [--max-jobs <n>]
- Contract requirements:
  - Agent must run fetch_pipeline.py first.
  - Agent must present grouped signatures and ask the user which one to fix.
  - Agent must use branch workflow and avoid direct default-branch pushes.
  - Agent must require explicit user confirmation before commit and push.

## References
- Tool and command references:
  - references/tools.md
- Script command contracts:
  - references/scripts.md
- Example artifacts:
  - assets/examples/sample-normalized-pipeline.json
  - assets/examples/sample-fix-pipeline-report.md
