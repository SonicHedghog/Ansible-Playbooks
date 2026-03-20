# Tools and integrations

## python
- Role: Runs skill scripts for provider detection, metadata fetch, draft generation, and optional posting.
- Command shapes:
  - `python scripts/fetch_issue.py --url <issue-url>`
  - `python scripts/research_issue.py --url <issue-url> --summary-file <path> --output-draft -`
  - `python scripts/research_issue.py --url <issue-url> --summary-file <path> --post`
- Inputs: issue URL, summary file path, optional draft destination.
- Outputs: normalized JSON, draft comment text or file path, and posted comment URL.
- Failure modes: non-zero exit on invalid URL, missing token, missing/empty summary file, or API error.

## knowledge-base skill
- Role: Retrieve existing topic-level knowledge before learning new material.
- Invocation: `skill("knowledge-base")`
- Inputs: topic query terms derived from issue title/body.
- Outputs: matched knowledge docs or indication that coverage is insufficient.
- Failure modes: no relevant docs found.

## learn skill
- Role: Ingest topic-focused sources into structured knowledge docs when needed.
- Invocation: `skill("learn")`
- Inputs: selected public sources for each topic (official docs preferred).
- Outputs: persisted docs in knowledge-base location.
- Failure modes: inaccessible URL, parsing/normalization issues.

## Topic extraction guidance
- Derive 1-3 reusable topics from issue wording.
- Prefer nouns/concepts over task phrasing (for example, use `Renovate` instead of `add renovate to this repo`).
- Keep issue-specific rollout decisions out of knowledge docs; include those only in the issue comment draft.
