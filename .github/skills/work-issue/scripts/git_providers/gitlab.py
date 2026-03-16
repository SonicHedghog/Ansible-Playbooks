import os
import re
from typing import Any, Dict, Optional, Tuple
from urllib.parse import quote

import requests


class GitLabProviderError(RuntimeError):
    pass


def parse_issue_url(url: str) -> Tuple[str, str, int]:
    normalized = url.strip().rstrip("/")
    pattern = re.compile(r"^https?://([^/]+)/(.+?)(?:/-)?/issues/(\d+)$")
    match = pattern.match(normalized)
    if not match:
        raise GitLabProviderError("Invalid GitLab issue URL")
    host, project_path, issue_iid = match.groups()
    project_path = project_path.replace("/-", "")
    base_url = f"https://{host}"
    return base_url, project_path, int(issue_iid)


def _api_url(base_url: str, path: str) -> str:
    return f"{base_url}/api/v4{path}"


def _headers() -> Dict[str, str]:
    token = os.getenv("GITLAB_TOKEN")
    headers = {"Accept": "application/json"}
    if token:
        headers["PRIVATE-TOKEN"] = token
    return headers


def _request(method: str, url: str, *, params: Optional[Dict[str, Any]] = None, json_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    response = requests.request(method, url, headers=_headers(), params=params, json=json_data, timeout=30)
    if response.status_code >= 400:
        raise GitLabProviderError(f"GitLab API error {response.status_code}: {response.text}")
    if response.text:
        return response.json()
    return {}


def _project_api_path(project_path: str) -> str:
    return quote(project_path, safe="")


def fetch_issue_metadata(issue_url: str) -> Dict[str, Any]:
    base_url, project_path, issue_iid = parse_issue_url(issue_url)
    encoded = _project_api_path(project_path)
    issue = _request("GET", _api_url(base_url, f"/projects/{encoded}/issues/{issue_iid}"))
    labels = [label for label in issue.get("labels", []) if isinstance(label, str)]
    return {
        "provider": "gitlab",
        "base_url": base_url,
        "repo": project_path,
        "issue_number": issue_iid,
        "title": issue.get("title", ""),
        "description": issue.get("description", ""),
        "labels": labels,
    }


def _get_project(base_url: str, project_path: str) -> Dict[str, Any]:
    encoded = _project_api_path(project_path)
    return _request("GET", _api_url(base_url, f"/projects/{encoded}"))


def _resolve_assignee_id(base_url: str, git_user: str) -> int:
    users = _request("GET", _api_url(base_url, "/users"), params={"search": git_user})
    if isinstance(users, list):
        for user in users:
            username = str(user.get("username", ""))
            name = str(user.get("name", ""))
            if username.lower() == git_user.lower() or name.lower() == git_user.lower():
                return int(user["id"])
    me = _request("GET", _api_url(base_url, "/user"))
    if "id" not in me:
        raise GitLabProviderError("Unable to resolve GitLab assignee")
    return int(me["id"])


def create_mr(issue_data: Dict[str, Any], branch_name: str) -> Dict[str, Any]:
    base_url = str(issue_data.get("base_url") or "https://gitlab.com")
    project_path = issue_data["repo"]
    project = _get_project(base_url, project_path)
    default_branch = project.get("default_branch", "main")
    project_id = int(project["id"])
    issue_number = int(issue_data["issue_number"])
    title = issue_data.get("title") or f"Work issue !{issue_number}"
    description = f"Closes #{issue_number}"
    return _request(
        "POST",
        _api_url(base_url, f"/projects/{project_id}/merge_requests"),
        json_data={
            "title": title,
            "source_branch": branch_name,
            "target_branch": default_branch,
            "description": description,
        },
    )


def get_open_mr_for_branch(base_url: str, project_path: str, branch_name: str) -> Optional[Dict[str, Any]]:
    project = _get_project(base_url, project_path)
    project_id = int(project["id"])
    mrs = _request(
        "GET",
        _api_url(base_url, f"/projects/{project_id}/merge_requests"),
        params={"state": "opened", "source_branch": branch_name, "per_page": 1},
    )
    if isinstance(mrs, list) and mrs:
        return mrs[0]
    return None


def assign_mr(base_url: str, project_path: str, mr_iid: int, git_user: str) -> None:
    project = _get_project(base_url, project_path)
    project_id = int(project["id"])
    assignee_id = _resolve_assignee_id(base_url, git_user)
    _request(
        "PUT",
        _api_url(base_url, f"/projects/{project_id}/merge_requests/{mr_iid}"),
        json_data={"assignee_ids": [assignee_id]},
    )


def create_mr_and_assign(issue_data: Dict[str, Any], branch_name: str, git_user: str) -> str:
    base_url = str(issue_data.get("base_url") or "https://gitlab.com")
    mr = create_mr(issue_data, branch_name)
    mr_iid = int(mr["iid"])
    assign_mr(base_url, issue_data["repo"], mr_iid, git_user)
    return mr["web_url"]


def ensure_mr_and_assign(issue_data: Dict[str, Any], branch_name: str, git_user: str) -> Tuple[str, bool]:
    base_url = str(issue_data.get("base_url") or "https://gitlab.com")
    existing = get_open_mr_for_branch(base_url, issue_data["repo"], branch_name)
    if existing:
        mr_iid = int(existing["iid"])
        assign_mr(base_url, issue_data["repo"], mr_iid, git_user)
        return str(existing["web_url"]), False

    mr = create_mr(issue_data, branch_name)
    mr_iid = int(mr["iid"])
    assign_mr(base_url, issue_data["repo"], mr_iid, git_user)
    return str(mr["web_url"]), True


def update_open_mr_for_branch(
    project_path: str,
    branch_name: str,
    *,
    title: Optional[str] = None,
    description: Optional[str] = None,
    base_url: str = "https://gitlab.com",
) -> str:
    existing = get_open_mr_for_branch(base_url, project_path, branch_name)
    if not existing:
        raise GitLabProviderError(f"No open MR found for branch '{branch_name}'")

    if title is None and description is None:
        raise GitLabProviderError("Nothing to update: provide --title and/or --body")

    project = _get_project(base_url, project_path)
    project_id = int(project["id"])
    mr_iid = int(existing["iid"])

    payload: Dict[str, Any] = {}
    if title is not None:
        payload["title"] = title
    if description is not None:
        payload["description"] = description

    updated = _request(
        "PUT",
        _api_url(base_url, f"/projects/{project_id}/merge_requests/{mr_iid}"),
        json_data=payload,
    )
    return str(updated.get("web_url") or existing["web_url"])
