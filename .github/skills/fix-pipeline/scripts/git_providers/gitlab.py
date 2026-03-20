import os
import re
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import quote

import requests


class GitLabProviderError(RuntimeError):
    pass


def parse_pipeline_url(url: str) -> Tuple[str, str, int]:
    normalized = url.strip().rstrip("/")
    pattern = re.compile(r"^https?://([^/]+)/(.+?)/-/pipelines/(\d+)$")
    match = pattern.match(normalized)
    if not match:
        raise GitLabProviderError("Invalid GitLab pipeline URL")
    host, project_path, pipeline_id = match.groups()
    return f"https://{host}", project_path, int(pipeline_id)


def _headers() -> Dict[str, str]:
    token = os.getenv("GITLAB_TOKEN")
    headers = {"Accept": "application/json"}
    if token:
        headers["PRIVATE-TOKEN"] = token
    return headers


def _api_url(base_url: str, path: str) -> str:
    return f"{base_url}/api/v4{path}"


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
        raise GitLabProviderError(f"GitLab API error {response.status_code}: {response.text}")
    return response


def _request_json(method: str, url: str, *, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    response = _request(method, url, params=params)
    if response.text:
        return response.json()
    return {}


def _encode_project(project_path: str) -> str:
    return quote(project_path, safe="")


def fetch_pipeline_metadata(pipeline_url: str) -> Dict[str, Any]:
    base_url, project_path, pipeline_id = parse_pipeline_url(pipeline_url)
    encoded = _encode_project(project_path)
    pipeline = _request_json("GET", _api_url(base_url, f"/projects/{encoded}/pipelines/{pipeline_id}"))
    return {
        "provider": "gitlab",
        "base_url": base_url,
        "repo": project_path,
        "pipeline_id": pipeline_id,
        "pipeline_url": pipeline_url,
        "branch": pipeline.get("ref") or "",
        "sha": pipeline.get("sha") or "",
        "status": pipeline.get("status") or "",
        "conclusion": pipeline.get("status") or "",
    }


def list_failed_jobs(base_url: str, project_path: str, pipeline_id: int, *, max_jobs: int = 25) -> List[Dict[str, Any]]:
    encoded = _encode_project(project_path)
    jobs_data = _request_json(
        "GET",
        _api_url(base_url, f"/projects/{encoded}/pipelines/{pipeline_id}/jobs"),
        params={"per_page": max_jobs},
    )

    jobs = jobs_data if isinstance(jobs_data, list) else []
    failures: List[Dict[str, Any]] = []
    for job in jobs:
        status = str(job.get("status") or "")
        if status in {"failed", "canceled", "skipped"}:
            failures.append(
                {
                    "id": int(job.get("id")),
                    "name": str(job.get("name") or ""),
                    "stage": str(job.get("stage") or ""),
                    "status": status,
                    "web_url": str(job.get("web_url") or ""),
                }
            )
    return failures


def fetch_job_log(base_url: str, project_path: str, job_id: int) -> str:
    encoded = _encode_project(project_path)
    response = _request(
        "GET",
        _api_url(base_url, f"/projects/{encoded}/jobs/{job_id}/trace"),
        allow_redirects=True,
    )
    return response.text
