import subprocess
from typing import List


class GitOperationError(RuntimeError):
    pass


def _run_git(args: List[str]) -> str:
    result = subprocess.run(
        ["git", *args],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise GitOperationError(result.stderr.strip() or result.stdout.strip() or "Git command failed")
    return result.stdout.strip()


def create_local_branch(branch_name: str) -> None:
    if local_branch_exists(branch_name):
        _run_git(["checkout", branch_name])
        return
    _run_git(["checkout", "-b", branch_name])


def push_branch(branch_name: str) -> None:
    if _has_upstream(branch_name):
        _run_git(["push"])
        return
    _run_git(["push", "--set-upstream", "origin", branch_name])


def detect_git_user() -> str:
    user = _run_git(["config", "user.name"])
    if not user:
        raise GitOperationError("Git user.name is not configured")
    return user


def local_branch_exists(branch_name: str) -> bool:
    result = subprocess.run(
        ["git", "show-ref", "--verify", f"refs/heads/{branch_name}"],
        check=False,
        capture_output=True,
        text=True,
    )
    return result.returncode == 0


def get_default_branch_ref() -> str:
    candidates = [
        ["symbolic-ref", "--short", "refs/remotes/origin/HEAD"],
        ["rev-parse", "--abbrev-ref", "origin/HEAD"],
    ]
    for args in candidates:
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


def branch_has_commits_ahead(branch_name: str) -> bool:
    base_ref = get_default_branch_ref()
    count = _run_git(["rev-list", "--count", f"{base_ref}..{branch_name}"])
    return int(count) > 0


def _has_upstream(branch_name: str) -> bool:
    result = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", f"{branch_name}@{{upstream}}"],
        check=False,
        capture_output=True,
        text=True,
    )
    return result.returncode == 0
