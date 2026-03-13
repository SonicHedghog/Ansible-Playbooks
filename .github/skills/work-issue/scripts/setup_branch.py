import argparse
import json
import subprocess

from git_providers import github, gitlab
from utils.env_loader import load_env
from utils.issue_json import read_issue_json


def _run_git(args: list[str]) -> str:
    result = subprocess.run(
        ["git", *args],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        message = result.stderr.strip() or result.stdout.strip() or "Git command failed"
        raise RuntimeError(message)
    return result.stdout.strip()


def _default_base_ref() -> str:
    for args in (
        ["symbolic-ref", "--short", "refs/remotes/origin/HEAD"],
        ["rev-parse", "--abbrev-ref", "origin/HEAD"],
    ):
        result = subprocess.run(
            ["git", *args],
            check=False,
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            value = result.stdout.strip()
            if value:
                return value
    return "origin/main"


def _branch_has_commits_ahead(branch_name: str) -> bool:
    base_ref = _default_base_ref()
    count = _run_git(["rev-list", "--count", f"{base_ref}..{branch_name}"])
    return int(count) > 0


def _detect_git_user() -> str:
    user = _run_git(["config", "user.name"])
    if not user:
        raise RuntimeError("Git user.name is not configured")
    return user


def main() -> None:
    load_env()

    parser = argparse.ArgumentParser(description="Ensure PR/MR exists for a branch when commits are ahead of default.")
    parser.add_argument("--issue-json", required=True, help="Path to issue JSON or '-' to read from stdin")
    parser.add_argument("--branch-name", required=True, help="Branch name to evaluate for PR/MR creation")
    args = parser.parse_args()

    issue_data = read_issue_json(args.issue_json)
    provider = issue_data.get("provider")
    if provider not in {"github", "gitlab"}:
        raise ValueError("Issue JSON must include provider='github' or provider='gitlab'")

    ready_for_pr = _branch_has_commits_ahead(args.branch_name)
    pr_url = None
    pr_created = False

    if ready_for_pr:
        git_user = _detect_git_user()
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
