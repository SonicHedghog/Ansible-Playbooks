import argparse
import json
import sys
from typing import Any, Dict

from git_providers import github, gitlab
from utils.env_loader import load_env
from utils.git_ops import branch_has_commits_ahead, create_local_branch, detect_git_user, push_branch


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

    parser = argparse.ArgumentParser(description="Create branch and push it. Create PR/MR only when branch has commits.")
    parser.add_argument("--issue-json", required=True, help="Path to issue JSON or '-' to read from stdin")
    parser.add_argument("--branch-name", required=True, help="Branch name to create and push")
    args = parser.parse_args()

    issue_data = _read_issue_json(args.issue_json)
    provider = issue_data.get("provider")
    if provider not in {"github", "gitlab"}:
        raise ValueError("Issue JSON must include provider='github' or provider='gitlab'")

    create_local_branch(args.branch_name)
    push_branch(args.branch_name)
    ready_for_pr = branch_has_commits_ahead(args.branch_name)
    pr_url = None
    pr_created = False

    if ready_for_pr:
        git_user = detect_git_user()
        if provider == "github":
            pr_url, pr_created = github.ensure_pr_and_assign(issue_data, args.branch_name, git_user)
        else:
            pr_url, pr_created = gitlab.ensure_mr_and_assign(issue_data, args.branch_name, git_user)

    result = {
        "branch_name": args.branch_name,
        "pr_url": pr_url,
        "pr_created": pr_created,
        "ready_for_pr": ready_for_pr,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
