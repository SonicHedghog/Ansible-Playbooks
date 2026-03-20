import argparse
import json

from git_providers import github, gitlab
from utils.env_loader import load_env
from utils.issue_json import read_issue_json


def _normalize_cli_text(value: str | None) -> str | None:
    if value is None:
        return None
    return value.replace("\\r\\n", "\n").replace("\\n", "\n")


def main() -> None:
    load_env()

    parser = argparse.ArgumentParser(description="Update an existing open PR/MR for a branch.")
    parser.add_argument("--issue-json", required=True, help="Path to issue JSON or '-' to read from stdin")
    parser.add_argument("--branch-name", required=True, help="Branch name whose open PR/MR should be updated")
    parser.add_argument("--title", help="New PR/MR title")
    parser.add_argument("--body", help="New PR body (GitHub) or MR description (GitLab)")
    args = parser.parse_args()

    normalized_title = _normalize_cli_text(args.title)
    normalized_body = _normalize_cli_text(args.body)

    if normalized_title is None and normalized_body is None:
        raise ValueError("Provide at least one of --title or --body")

    issue_data = read_issue_json(args.issue_json)
    provider = issue_data.get("provider")
    if provider not in {"github", "gitlab"}:
        raise ValueError("Issue JSON must include provider='github' or provider='gitlab'")

    if provider == "github":
        pr_url = github.update_open_pr_for_branch(
            issue_data["repo"],
            args.branch_name,
            title=normalized_title,
            body=normalized_body,
        )
    else:
        pr_url = gitlab.update_open_mr_for_branch(
            issue_data["repo"],
            args.branch_name,
            title=normalized_title,
            description=normalized_body,
            base_url=str(issue_data.get("base_url") or "https://gitlab.com"),
        )

    result = {
        "branch_name": args.branch_name,
        "pr_url": pr_url,
        "updated": True,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
