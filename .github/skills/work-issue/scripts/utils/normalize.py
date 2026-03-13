import re
from typing import Any, Dict, List

from slugify import slugify


def _normalize_labels(labels: Any) -> List[str]:
    if labels is None:
        return []
    if isinstance(labels, list):
        normalized: List[str] = []
        for label in labels:
            if isinstance(label, str):
                normalized.append(label)
            elif isinstance(label, dict):
                name = label.get("name") or label.get("title")
                if name:
                    normalized.append(str(name))
        return normalized
    return []


def normalize_issue_data(provider: str, issue_data: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "provider": provider,
        "repo": issue_data.get("repo"),
        "issue_number": int(issue_data.get("issue_number")),
        "title": issue_data.get("title") or "",
        "description": issue_data.get("description") or "",
        "labels": _normalize_labels(issue_data.get("labels")),
    }


def generate_default_branch_name(issue_number: int, title: str, prefix: str = "issue") -> str:
    safe_title = slugify(title or "untitled", separator="-")
    safe_title = re.sub(r"-{2,}", "-", safe_title).strip("-")
    return f"{prefix}/{issue_number}-{safe_title}" if safe_title else f"{prefix}/{issue_number}"
