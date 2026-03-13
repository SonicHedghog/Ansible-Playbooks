import os
import re
from typing import Any, Dict, Optional, Tuple

import requests


class GitHubProviderError(RuntimeError):
    pass


def parse_issue_url(url: str) -> Tuple[str, str, int]:
    pattern = re.compile(r"^https?://github\.com/([^/]+)/([^/]+)/issues/(\d+)(?:/.*)?$")
    match = pattern.match(url.strip())
    if not match:
        raise GitHubProviderError("Invalid GitHub issue URL")
    owner, repo, issue_number = match.groups()
    return owner, repo, int(issue_number)


def _headers() -> Dict[str, str]:
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    token = os.getenv("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def _request(method: str, url: str, *, params: Optional[Dict[str, Any]] = None, json_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    response = requests.request(method, url, headers=_headers(), params=params, json=json_data, timeout=30)
    if response.status_code >= 400:
        raise GitHubProviderError(f"GitHub API error {response.status_code}: {response.text}")
    if response.text:
        return response.json()
    return {}


def fetch_issue_metadata(issue_url: str) -> Dict[str, Any]:
    owner, repo, issue_number = parse_issue_url(issue_url)
    issue = _request("GET", f"https://api.github.com/repos/{owner}/{repo}/issues/{issue_number}")
    labels = [label.get("name") for label in issue.get("labels", []) if label.get("name")]
    return {
        "provider": "github",
        "repo": f"{owner}/{repo}",
        "issue_number": issue_number,
        "title": issue.get("title", ""),
        "description": issue.get("body", ""),
        "labels": labels,
    }


def _get_default_branch(owner: str, repo: str) -> str:
    repo_data = _request("GET", f"https://api.github.com/repos/{owner}/{repo}")
    return repo_data.get("default_branch", "main")


def _resolve_assignee(owner: str, repo: str, git_user: str) -> str:
    collaborators = _request("GET", f"https://api.github.com/repos/{owner}/{repo}/collaborators", params={"per_page": 100})
    if isinstance(collaborators, list):
        for user in collaborators:
            login = user.get("login", "")
            if login.lower() == git_user.lower():
                return login
    me = _request("GET", "https://api.github.com/user")
    login = me.get("login")
    if not login:
        raise GitHubProviderError("Unable to resolve GitHub assignee")
    return login


def create_pr(issue_data: Dict[str, Any], branch_name: str) -> Dict[str, Any]:
    owner, repo = issue_data["repo"].split("/", 1)
    base_branch = _get_default_branch(owner, repo)
    issue_number = int(issue_data["issue_number"])
    title = issue_data.get("title") or f"Work issue #{issue_number}"
    body = f"Closes #{issue_number}"
    return _request(
        "POST",
        f"https://api.github.com/repos/{owner}/{repo}/pulls",
        json_data={
            "title": title,
            "head": branch_name,
            "base": base_branch,
            "body": body,
        },
    )


def get_open_pr_for_branch(repo_full_name: str, branch_name: str) -> Optional[Dict[str, Any]]:
    owner, repo = repo_full_name.split("/", 1)
    pulls = _request(
        "GET",
        f"https://api.github.com/repos/{owner}/{repo}/pulls",
        params={"state": "open", "head": f"{owner}:{branch_name}", "per_page": 1},
    )
    if isinstance(pulls, list) and pulls:
        return pulls[0]
    return None


def assign_pr(repo_full_name: str, pr_number: int, git_user: str) -> None:
    owner, repo = repo_full_name.split("/", 1)
    assignee = _resolve_assignee(owner, repo, git_user)
    _request(
        "POST",
        f"https://api.github.com/repos/{owner}/{repo}/issues/{pr_number}/assignees",
        json_data={"assignees": [assignee]},
    )


def create_pr_and_assign(issue_data: Dict[str, Any], branch_name: str, git_user: str) -> str:
    pr = create_pr(issue_data, branch_name)
    pr_number = int(pr["number"])
    assign_pr(issue_data["repo"], pr_number, git_user)
    return pr["html_url"]


def ensure_pr_and_assign(issue_data: Dict[str, Any], branch_name: str, git_user: str) -> Tuple[str, bool]:
    existing = get_open_pr_for_branch(issue_data["repo"], branch_name)
    if existing:
        pr_number = int(existing["number"])
        assign_pr(issue_data["repo"], pr_number, git_user)
        return existing["html_url"], False

    pr = create_pr(issue_data, branch_name)
    pr_number = int(pr["number"])
    assign_pr(issue_data["repo"], pr_number, git_user)
    return pr["html_url"], True


def update_open_pr_for_branch(repo_full_name: str, branch_name: str, *, title: Optional[str] = None, body: Optional[str] = None) -> str:
    existing = get_open_pr_for_branch(repo_full_name, branch_name)
    if not existing:
        raise GitHubProviderError(f"No open PR found for branch '{branch_name}'")

    owner, repo = repo_full_name.split("/", 1)
    payload: Dict[str, Any] = {}
    if title is not None:
        payload["title"] = title
    if body is not None:
        payload["body"] = body
    if not payload:
        raise GitHubProviderError("Nothing to update: provide --title and/or --body")

    pr_number = int(existing["number"])
    updated = _request(
        "PATCH",
        f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}",
        json_data=payload,
    )
    return str(updated.get("html_url") or existing["html_url"])
