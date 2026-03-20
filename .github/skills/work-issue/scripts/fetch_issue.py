import argparse
import json
from urllib.parse import urlparse

from git_providers import github, gitlab
from utils.env_loader import load_env
from utils.normalize import normalize_issue_data


def detect_provider(issue_url: str) -> str:
    parsed = urlparse(issue_url)
    host = parsed.netloc.lower()
    path = parsed.path.lower()
    if "github.com" in host:
        return "github"
    # Support gitlab.com and self-hosted GitLab issue URLs like /group/project/-/issues/123.
    if "gitlab" in host or "/-/issues/" in path:
        return "gitlab"
    raise ValueError("Unsupported issue provider in URL")


def main() -> None:
    load_env()

    parser = argparse.ArgumentParser(description="Fetch and normalize issue metadata.")
    parser.add_argument("--url", required=True, help="Issue URL (GitHub or GitLab)")
    args = parser.parse_args()

    provider = detect_provider(args.url)
    if provider == "github":
        issue_data = github.fetch_issue_metadata(args.url)
    else:
        issue_data = gitlab.fetch_issue_metadata(args.url)

    normalized = normalize_issue_data(provider, issue_data)
    print(json.dumps(normalized, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
