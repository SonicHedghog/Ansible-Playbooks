import argparse
from pathlib import Path
from urllib.parse import urlparse

from git_providers import github, gitlab
from utils.env_loader import load_env
from utils.normalize import normalize_issue_data


def detect_provider(issue_url: str) -> str:
    parsed = urlparse(issue_url)
    host = parsed.netloc.lower()
    path = parsed.path.lower()
    if 'github.com' in host:
        return 'github'
    if 'gitlab' in host or '/-/issues/' in path:
        return 'gitlab'
    raise ValueError('Unsupported issue provider in URL')


def _build_comment(summary_text: str, issue: dict) -> str:
    issue_title = issue.get('title', '').strip()
    focus_line = 'Preliminary research summary for implementation planning.'
    lines = [
        '## Preliminary Research',
        '',
        focus_line,
        '',
        f"Issue: {issue_title}" if issue_title else 'Issue: (title unavailable)',
        '',
        summary_text.strip(),
    ]
    return '\n'.join(lines).strip() + '\n'


def main() -> None:
    load_env()

    parser = argparse.ArgumentParser(description='Draft or post a research comment for an issue URL.')
    parser.add_argument('--url', required=True, help='Issue URL (GitHub or GitLab)')
    parser.add_argument('--summary-file', required=True, help='Path to markdown/plaintext summary file')
    parser.add_argument('--output-draft', default='', help='Write draft to path, or use - to print to stdout')
    parser.add_argument('--post', action='store_true', help='Post comment to the issue (requires explicit approval from caller)')
    args = parser.parse_args()

    provider = detect_provider(args.url)
    summary_path = Path(args.summary_file)
    if not summary_path.exists() or not summary_path.is_file():
        raise FileNotFoundError(f'Summary file not found: {summary_path}')

    summary_text = summary_path.read_text(encoding='utf-8')
    if not summary_text.strip():
        raise ValueError('Summary file is empty')

    if provider == 'github':
        issue_data = github.fetch_issue_metadata(args.url)
    else:
        issue_data = gitlab.fetch_issue_metadata(args.url)

    normalized = normalize_issue_data(provider, issue_data)
    comment_body = _build_comment(summary_text, normalized)

    if args.output_draft:
        if args.output_draft == '-':
            print(comment_body)
        else:
            out = Path(args.output_draft)
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(comment_body, encoding='utf-8')
            print(str(out.resolve()))

    if args.post:
        if provider == 'github':
            url = github.post_issue_comment(args.url, comment_body)
        else:
            url = gitlab.post_issue_comment(args.url, comment_body)
        print(f'Posted comment: {url}')


if __name__ == '__main__':
    main()
