# Script command contracts

## fetch_pipeline.py
- Purpose:
  - Normalize pipeline metadata for GitHub or GitLab.
  - Extract failed jobs.
  - Fetch per-job logs.
  - Compute error signatures and grouped failure clusters.
  - Optionally write JSON and markdown artifacts.

- Command shape:
  - python scripts/fetch_pipeline.py --url <pipeline-url> [--max-jobs <n>] [--output-json <path>] [--output-md <path>]

- Arguments:
  - --url (required): pipeline URL.
  - --max-jobs (optional): max jobs to inspect, default 25.
  - --output-json (optional): writes normalized JSON artifact.
  - --output-md (optional): writes markdown report artifact.

- Expected inputs:
  - GitHub Actions run URL in the form:
    - https://github.com/<owner>/<repo>/actions/runs/<run-id>
  - GitLab pipeline URL in the form:
    - https://<host>/<group>/<project>/-/pipelines/<pipeline-id>

- Output JSON keys:
  - provider
  - repo
  - pipeline_id
  - pipeline_url
  - branch
  - sha
  - status
  - conclusion
  - failed_jobs[]:
    - id, name, stage, status, web_url, log_excerpt, error_signature
    - check_run_id (GitHub only)
    - annotation_summary (GitHub only: total, warning_count, failure_count, notice_count)
    - annotations[] (GitHub only: annotation_level, path, start_line, end_line, title, message)
    - Note: for GitHub, this list may include jobs with warning/notice annotations even when the job did not fail.
  - error_signature_groups[]:
    - error_signature, count, jobs[]

- Error and exit behavior:
  - Exits non-zero on unsupported URLs.
  - Exits non-zero on provider auth/API failures.
  - Exits non-zero on malformed provider responses.

- Common failure modes:
  - Missing provider token.
  - URL does not match provider run or pipeline format.
  - API rate limit or permissions failure.
  - Pipeline has no accessible job logs.
