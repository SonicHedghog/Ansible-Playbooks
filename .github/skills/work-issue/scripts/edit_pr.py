import argparse
import json
import sys
from typing import Any, Dict

from git_providers import github, gitlab
from utils.env_loader import load_env


def _read_issue_json(input_value: str) -> Dict[str, Any]:
    if input_value == "-":
        raw = sys.stdin.read()
        if not raw.strip():
            raise ValueError("No JSON was provided on stdin")
        return json.loads(raw)

    with open(input_value, "rb") as file:
        payload = file.read()

    for encoding in ("utf-8", "utf-8-sig", "utf-16"):
        try:
            return json.loads(payload.decode(encoding))
        except (UnicodeDecodeError, json.JSONDecodeError):
            continue

    raise ValueError("Unable to parse issue JSON from file")


def main() -> None:
    load_env()

    parser = argparse.ArgumentParser(description="Update an existing open PR/MR for a branch.")
    parser.add_argument("--issue-json", required=True, help="Path to issue JSON or '-' to read from stdin")
    parser.add_argument("--branch-name", required=True, help="Branch name whose open PR/MR should be updated")
    parser.add_argument("--title", help="New PR/MR title")
    parser.add_argument("--body", help="New PR body (GitHub) or MR description (GitLab)")
    args = parser.parse_args()

    if args.title is None and args.body is None:
        raise ValueError("Provide at least one of --title or --body")

    issue_data = _read_issue_json(args.issue_json)
    provider = issue_data.get("provider")
    if provider not in {"github", "gitlab"}:
        raise ValueError("Issue JSON must include provider='github' or provider='gitlab'")

    if provider == "github":
        pr_url = github.update_open_pr_for_branch(
            issue_data["repo"],
            args.branch_name,
            title=args.title,
            body=args.body,
        )
    else:
        pr_url = gitlab.update_open_mr_for_branch(
            issue_data["repo"],
            args.branch_name,
            title=args.title,
            description=args.body,
        )

    result = {
        "branch_name": args.branch_name,
        "pr_url": pr_url,
        "updated": True,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
