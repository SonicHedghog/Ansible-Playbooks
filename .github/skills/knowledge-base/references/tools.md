# Knowledge-Base Tool References

## file_search
- Role: Find candidate documentation files in the knowledge root by path pattern.
- Command shape used:
  - query: <knowledge-base-skill-root>/assets/docs/**
- Inputs: glob pattern.
- Outputs: matching file paths.
- Common failures: no matches due to empty docs tree or incorrect path.

## grep_search
- Role: Search knowledge docs for relevant headings and body text.
- Command shape used:
  - query: query terms or regex alternatives
  - includePattern: <knowledge-base-skill-root>/assets/docs/**
  - isRegexp: true|false based on query mode
- Inputs: query text/regex and include pattern.
- Outputs: matching lines with file locations.
- Common failures: over-broad regex, no matches, ignored files not included.

## read_file
- Role: Read matched docs before synthesizing an answer.
- Command shape used:
  - filePath: matched file path
  - startLine/endLine: bounded ranges; increase range as needed
- Inputs: file path and line bounds.
- Outputs: raw file content for analysis.
- Common failures: wrong file path, insufficient line range.

## create_file
- Role: Persist newly learned documentation (usually via /learn output).
- Command shape used:
  - filePath: <knowledge-base-skill-root>/assets/docs/<category>/<topic>.md
  - content: structured markdown with source attribution
- Inputs: destination path and markdown body.
- Outputs: created file.
- Common failures: invalid path characters, duplicate filename conflicts.

## create_directory
- Role: Ensure category folders exist before writing new docs.
- Command shape used:
  - dirPath: <knowledge-base-skill-root>/assets/docs/<category>
- Inputs: directory path.
- Outputs: created/ensured directory.
- Common failures: invalid or unauthorized path.

## /learn (skill integration)
- Role: Acquire missing knowledge when local retrieval confidence is low.
- Invocation shape used:
  - /learn <url-or-path> [topic]
  - topic-only auto-learning path may infer sources from the topic before save
- Inputs: unresolved topic and optional source.
- Outputs: new markdown doc in knowledge base docs folder.
- Common failures: inaccessible source, low-quality source, unsupported file format.
