import os
import re
from typing import Any, Dict, Optional, Tuple
from urllib.parse import quote

import requests


class GitLabProviderError(RuntimeError):
    pass


def parse_issue_url(url: str) -> Tuple[str, str, int]:
    normalized = url.strip().rstrip('/')
    pattern = re.compile(r'^https?://([^/]+)/(.+?)(?:/-)?/issues/(\d+)$')
    match = pattern.match(normalized)
    if not match:
        raise GitLabProviderError('Invalid GitLab issue URL')
    host, project_path, issue_iid = match.groups()
    project_path = project_path.replace('/-', '')
    base_url = f'https://{host}'
    return base_url, project_path, int(issue_iid)


def _api_url(base_url: str, path: str) -> str:
    return f'{base_url}/api/v4{path}'


def _headers() -> Dict[str, str]:
    token = os.getenv('GITLAB_TOKEN')
    if not token:
        raise GitLabProviderError('Missing required environment variable: GITLAB_TOKEN')
    return {'Accept': 'application/json', 'PRIVATE-TOKEN': token}


def _request(method: str, url: str, *, params: Optional[Dict[str, Any]] = None, json_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    response = requests.request(method, url, headers=_headers(), params=params, json=json_data, timeout=30)
    if response.status_code >= 400:
        raise GitLabProviderError(f'GitLab API error {response.status_code}: {response.text}')
    if response.text:
        return response.json()
    return {}


def _project_api_path(project_path: str) -> str:
    return quote(project_path, safe='')


def fetch_issue_metadata(issue_url: str) -> Dict[str, Any]:
    base_url, project_path, issue_iid = parse_issue_url(issue_url)
    encoded = _project_api_path(project_path)
    issue = _request('GET', _api_url(base_url, f'/projects/{encoded}/issues/{issue_iid}'))
    labels = [label for label in issue.get('labels', []) if isinstance(label, str)]
    return {
        'provider': 'gitlab',
        'base_url': base_url,
        'repo': project_path,
        'issue_number': issue_iid,
        'title': issue.get('title', ''),
        'description': issue.get('description', ''),
        'labels': labels,
        'web_url': issue.get('web_url', issue_url),
    }


def post_issue_comment(issue_url: str, body: str) -> str:
    base_url, project_path, issue_iid = parse_issue_url(issue_url)
    encoded = _project_api_path(project_path)
    project = _request('GET', _api_url(base_url, f'/projects/{encoded}'))
    project_id = int(project['id'])
    note = _request(
        'POST',
        _api_url(base_url, f'/projects/{project_id}/issues/{issue_iid}/notes'),
        json_data={'body': body},
    )
    web_url = note.get('web_url')
    if not web_url:
        raise GitLabProviderError('Comment created but no web_url returned')
    return str(web_url)
