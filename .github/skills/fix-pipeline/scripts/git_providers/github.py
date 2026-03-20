import os
import re
from typing import Any, Dict, List, Optional, Tuple

import requests


class GitHubProviderError(RuntimeError):
    pass


def parse_pipeline_url(url: str) -> Tuple[str, str, int]:
    pattern = re.compile(r"^https?://github\.com/([^/]+)/([^/]+)/actions/runs/(\d+)(?:/.*)?$")
    match = pattern.match(url.strip())
    if not match:
        raise GitHubProviderError("Invalid GitHub Actions run URL")
    owner, repo, run_id = match.groups()
    return owner, repo, int(run_id)


def _headers() -> Dict[str, str]:
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    token = os.getenv("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def _request(
    method: str,
    url: str,
    *,
    params: Optional[Dict[str, Any]] = None,
    allow_redirects: bool = True,
) -> requests.Response:
    response = requests.request(
        method,
        url,
        headers=_headers(),
        params=params,
        timeout=30,
        allow_redirects=allow_redirects,
    )
    if response.status_code >= 400:
        raise GitHubProviderError(f"GitHub API error {response.status_code}: {response.text}")
    return response


def _request_json(method: str, url: str, *, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    response = _request(method, url, params=params)
    if response.text:
        return response.json()
    return {}


def fetch_pipeline_metadata(pipeline_url: str) -> Dict[str, Any]:
    owner, repo, run_id = parse_pipeline_url(pipeline_url)
    run = _request_json("GET", f"https://api.github.com/repos/{owner}/{repo}/actions/runs/{run_id}")
    return {
        "provider": "github",
        "repo": f"{owner}/{repo}",
        "pipeline_id": run_id,
        "pipeline_url": pipeline_url,
        "branch": run.get("head_branch") or "",
        "sha": run.get("head_sha") or "",
        "status": run.get("status") or "",
        "conclusion": run.get("conclusion") or "",
    }


def _extract_check_run_id(job: Dict[str, Any]) -> Optional[int]:
    check_run_url = str(job.get("check_run_url") or "")
    if not check_run_url:
        return None
    match = re.search(r"/check-runs/(\d+)$", check_run_url)
    if not match:
        return None
    return int(match.group(1))


def list_run_jobs(repo_full_name: str, run_id: int, *, max_jobs: int = 25) -> List[Dict[str, Any]]:
    owner, repo = repo_full_name.split("/", 1)
    jobs_data = _request_json(
        "GET",
        f"https://api.github.com/repos/{owner}/{repo}/actions/runs/{run_id}/jobs",
        params={"per_page": max_jobs},
    )
    jobs = jobs_data.get("jobs", []) if isinstance(jobs_data, dict) else []
    normalized_jobs: List[Dict[str, Any]] = []
    for job in jobs:
        conclusion = str(job.get("conclusion") or "")
        status = str(job.get("status") or "")
        check_run_id = _extract_check_run_id(job)
        normalized_jobs.append(
            {
                "id": int(job.get("id")),
                "name": str(job.get("name") or ""),
                "stage": str(job.get("name") or ""),
                "status": conclusion or status,
                "web_url": str(job.get("html_url") or ""),
                "check_run_id": check_run_id,
                "conclusion": conclusion,
                "raw_status": status,
            }
        )
    return normalized_jobs


def fetch_job_log(repo_full_name: str, job_id: int) -> str:
    owner, repo = repo_full_name.split("/", 1)
    response = _request(
        "GET",
        f"https://api.github.com/repos/{owner}/{repo}/actions/jobs/{job_id}/logs",
        allow_redirects=True,
    )
    return response.text


def fetch_check_run_annotations(
    repo_full_name: str,
    check_run_id: int,
    *,
    max_annotations: int = 100,
) -> List[Dict[str, Any]]:
    owner, repo = repo_full_name.split("/", 1)
    annotations: List[Dict[str, Any]] = []
    page = 1
    per_page = 50

    while len(annotations) < max_annotations:
        response = _request_json(
            "GET",
            f"https://api.github.com/repos/{owner}/{repo}/check-runs/{check_run_id}/annotations",
            params={"per_page": per_page, "page": page},
        )

        if not isinstance(response, list) or not response:
            break

        annotations.extend(response)
        if len(response) < per_page:
            break
        page += 1

    return annotations[:max_annotations]
