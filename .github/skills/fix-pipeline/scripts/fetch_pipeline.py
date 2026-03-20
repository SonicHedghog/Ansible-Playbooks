import argparse
import json
import os
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

from git_providers import github, gitlab
from utils.env_loader import load_env
from utils.error_signature import derive_error_signature, group_signatures, trim_log_excerpt


def detect_provider(pipeline_url: str) -> str:
    parsed = urlparse(pipeline_url)
    host = parsed.netloc.lower()
    path = parsed.path.lower()

    if "github.com" in host and "/actions/runs/" in path:
        return "github"
    if ("gitlab" in host or "/-/pipelines/" in path) and "/-/pipelines/" in path:
        return "gitlab"

    raise ValueError("Unsupported pipeline provider in URL")


def _write_file(path_value: Optional[str], content: str) -> None:
    if not path_value:
        return
    path = Path(path_value)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _to_markdown(normalized: dict) -> str:
    lines: list[str] = []
    lines.append("# fix-pipeline report")
    lines.append("")
    lines.append("## Pipeline")
    lines.append(f"- provider: {normalized.get('provider', '')}")
    lines.append(f"- repository: {normalized.get('repo', '')}")
    lines.append(f"- pipeline url: {normalized.get('pipeline_url', '')}")
    lines.append(f"- branch: {normalized.get('branch', '')}")
    lines.append(f"- sha: {normalized.get('sha', '')}")
    lines.append(f"- status: {normalized.get('status', '')}")
    lines.append("")

    signature_groups = normalized.get("error_signature_groups", [])
    lines.append("## Error signature groups")
    if not signature_groups:
        lines.append("No failed jobs were detected.")
    else:
        for index, group in enumerate(signature_groups, start=1):
            lines.append(f"### Group {index}")
            lines.append(f"- signature: {group.get('error_signature', '')}")
            lines.append(f"- occurrences: {group.get('count', 0)}")
            lines.append("- jobs:")
            for job in group.get("jobs", []):
                lines.append(
                    f"  - {job.get('name', '')} | stage={job.get('stage', '')} | status={job.get('status', '')}"
                )
            lines.append("")

    lines.append("## Recommended next step")
    lines.append("Ask the user which error signature group to fix first, then scope edits to that group.")

    return "\n".join(lines).strip() + "\n"


def main() -> None:
    load_env()

    parser = argparse.ArgumentParser(description="Fetch and normalize pipeline failures from GitHub Actions or GitLab CI.")
    parser.add_argument("--url", required=True, help="Pipeline URL (GitHub Actions run or GitLab pipeline)")
    parser.add_argument("--max-jobs", type=int, default=25, help="Max jobs to inspect from pipeline")
    parser.add_argument("--output-json", help="Optional output path for normalized JSON")
    parser.add_argument("--output-md", help="Optional output path for markdown report")
    args = parser.parse_args()

    provider = detect_provider(args.url)

    if provider == "github":
        if not os.getenv("GITHUB_TOKEN"):
            raise RuntimeError("Missing required environment variable: GITHUB_TOKEN")
        metadata = github.fetch_pipeline_metadata(args.url)
        failed_jobs = github.list_failed_jobs(metadata["repo"], metadata["pipeline_id"], max_jobs=args.max_jobs)

        enriched_jobs = []
        for job in failed_jobs:
            log_text = github.fetch_job_log(metadata["repo"], int(job["id"]))
            job["log_excerpt"] = trim_log_excerpt(log_text)
            job["error_signature"] = derive_error_signature(log_text)
            enriched_jobs.append(job)
    else:
        if not os.getenv("GITLAB_TOKEN"):
            raise RuntimeError("Missing required environment variable: GITLAB_TOKEN")
        metadata = gitlab.fetch_pipeline_metadata(args.url)
        base_url = str(metadata.get("base_url") or "https://gitlab.com")
        failed_jobs = gitlab.list_failed_jobs(base_url, metadata["repo"], metadata["pipeline_id"], max_jobs=args.max_jobs)

        enriched_jobs = []
        for job in failed_jobs:
            log_text = gitlab.fetch_job_log(base_url, metadata["repo"], int(job["id"]))
            job["log_excerpt"] = trim_log_excerpt(log_text)
            job["error_signature"] = derive_error_signature(log_text)
            enriched_jobs.append(job)

    normalized = {
        **metadata,
        "failed_jobs": enriched_jobs,
        "error_signature_groups": group_signatures(enriched_jobs),
    }

    json_payload = json.dumps(normalized, ensure_ascii=False, indent=2)
    markdown_payload = _to_markdown(normalized)

    _write_file(args.output_json, json_payload + "\n")
    _write_file(args.output_md, markdown_payload)

    print(json_payload)


if __name__ == "__main__":
    main()
