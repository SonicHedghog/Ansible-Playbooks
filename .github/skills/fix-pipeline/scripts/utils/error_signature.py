import re
from typing import Iterable


_ERROR_PATTERNS = [
    re.compile(r"(?i)\b(?:error|exception|traceback|failed|lint|fatal)\b.*"),
    re.compile(r"(?i)^\s*e\s+\S+"),
]


def _clean_line(line: str) -> str:
    cleaned = re.sub(r"\x1b\[[0-9;]*m", "", line)
    return cleaned.strip()


def derive_error_signature(log_text: str) -> str:
    lines = [_clean_line(line) for line in log_text.splitlines() if _clean_line(line)]
    if not lines:
        return "No log lines captured"

    for line in reversed(lines):
        for pattern in _ERROR_PATTERNS:
            if pattern.search(line):
                return line[:220]

    tail = lines[-1]
    return tail[:220]


def trim_log_excerpt(log_text: str, *, max_lines: int = 80) -> str:
    lines = [_clean_line(line) for line in log_text.splitlines()]
    non_empty = [line for line in lines if line]
    if not non_empty:
        return ""
    excerpt = non_empty[-max_lines:]
    return "\n".join(excerpt)


def group_signatures(signatures: Iterable[dict]) -> list[dict]:
    grouped: dict[str, list[dict]] = {}
    for item in signatures:
        signature = str(item.get("error_signature") or "Unknown failure signature")
        grouped.setdefault(signature, []).append(item)

    groups: list[dict] = []
    for signature, items in grouped.items():
        groups.append(
            {
                "error_signature": signature,
                "count": len(items),
                "jobs": [
                    {
                        "id": job.get("id"),
                        "name": job.get("name"),
                        "stage": job.get("stage"),
                        "status": job.get("status"),
                        "web_url": job.get("web_url"),
                    }
                    for job in items
                ],
            }
        )

    groups.sort(key=lambda value: value["count"], reverse=True)
    return groups
