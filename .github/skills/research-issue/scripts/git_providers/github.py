import os
import re
from typing import Any, Dict, Optional, Tuple

import requests


class GitHubProviderError(RuntimeError):
    pass


def parse_issue_url(url: str) -> Tuple[str, str, int]:
    pattern = re.compile(r'^https?://github\.com/([^/]+)/([^/]+)/issues/(\d+)(?:/.*)?$')
    match = pattern.match(url.strip())
    if not match:
        raise GitHubProviderError('Invalid GitHub issue URL')
    owner, repo, issue_number = match.groups()
    return owner, repo, int(issue_number)


def _headers() -> Dict[str, str]:
    token = os.getenv('GITHUB_TOKEN')
    if not token:
        raise GitHubProviderError('Missing required environment variable: GITHUB_TOKEN')

    return {
        'Accept': 'application/vnd.github+json',
        'X-GitHub-Api-Version': '2022-11-28',
        'Authorization': f'Bearer {token}',
    }


def _request(method: str, url: str, *, params: Optional[Dict[str, Any]] = None, json_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    response = requests.request(method, url, headers=_headers(), params=params, json=json_data, timeout=30)
    if response.status_code >= 400:
        raise GitHubProviderError(f'GitHub API error {response.status_code}: {response.text}')
    if response.text:
        return response.json()
    return {}


def fetch_issue_metadata(issue_url: str) -> Dict[str, Any]:
    owner, repo, issue_number = parse_issue_url(issue_url)
    issue = _request('GET', f'https://api.github.com/repos/{owner}/{repo}/issues/{issue_number}')
    labels = [label.get('name') for label in issue.get('labels', []) if label.get('name')]
    return {
        'provider': 'github',
        'repo': f'{owner}/{repo}',
        'issue_number': issue_number,
        'title': issue.get('title', ''),
        'description': issue.get('body', ''),
        'labels': labels,
        'web_url': issue.get('html_url', issue_url),
    }


def post_issue_comment(issue_url: str, body: str) -> str:
    owner, repo, issue_number = parse_issue_url(issue_url)
    payload = {'body': body}
    comment = _request('POST', f'https://api.github.com/repos/{owner}/{repo}/issues/{issue_number}/comments', json_data=payload)
    html_url = comment.get('html_url')
    if not html_url:
        raise GitHubProviderError('Comment created but no html_url returned')
    return str(html_url)
