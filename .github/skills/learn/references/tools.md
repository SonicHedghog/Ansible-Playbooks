# Learn Skill Tool References

## fetch_webpage
- Role: Retrieve content from public web pages for learning.
- Command shape used:
  - urls: ["https://..."]
  - query: concise extraction goal (topic focus)
- Inputs: one or more public URLs plus extraction query.
- Outputs: extracted content relevant to the query.
- Common failures: inaccessible URL, blocked/unsupported content, low-signal pages.

## read_file
- Role: Read user-provided local documents when source is a path.
- Command shape used:
  - filePath: absolute path
  - startLine/endLine: bounded reads (multiple reads if needed)
- Inputs: local path and line bounds.
- Outputs: source text content for transformation.
- Common failures: file not found, unsupported binary content, insufficient line range.

## create_directory
- Role: Ensure category destination exists under knowledge-base docs root.
- Command shape used:
  - dirPath: <knowledge-base-skill-root>/assets/docs/<category>
- Inputs: destination directory.
- Outputs: folder created/existing.
- Common failures: invalid path, permission issues.

## create_file
- Role: Persist transformed, structured Markdown knowledge docs.
- Command shape used:
  - filePath: <knowledge-base-skill-root>/assets/docs/<category>/<topic>.md
  - content: markdown with frontmatter and source attribution
- Inputs: destination path and generated markdown.
- Outputs: created knowledge document.
- Common failures: invalid filename, collisions with existing file.

## file_search
- Role: Detect potential filename collisions before creating new docs.
- Command shape used:
  - query: <knowledge-base-skill-root>/assets/docs/**/<slug>.md
- Inputs: glob pattern.
- Outputs: existing matching paths.
- Common failures: no matches, overly broad patterns.

## grep_search
- Role: Optional duplicate-topic detection by scanning existing docs.
- Command shape used:
  - query: topic terms (regex or text)
  - includePattern: <knowledge-base-skill-root>/assets/docs/**
- Inputs: topic text and include pattern.
- Outputs: candidate duplicates for merge/append decisions.
- Common failures: false positives/negatives with short terms.
