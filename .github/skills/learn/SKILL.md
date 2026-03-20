---
name: learn
description: Learn from a public URL or local document and store structured markdown in the knowledge-base docs folder.
---

# /learn Skill

## Purpose
Use this skill to ingest knowledge from a public URL or user-provided local document, transform it into structured Markdown documentation, and save it into the local knowledge base.

## Invocation
- Primary: /learn <url-or-path> [topic]

## Inputs
- Required:
  - url-or-path: public URL or local file path.
- Optional:
  - topic: target topic/title for naming and categorization.

## Outputs
- A new Markdown documentation file at:
  - <knowledge-base-skill-root>/assets/docs/<category>/<topic>.md
- Structured sections:
  - Summary
  - Key concepts
  - Procedures/steps (if applicable)
  - Caveats/limitations
  - Sources
- Source attribution metadata in frontmatter.

## Path Resolution
- Determine the current skill root from the location of this SKILL.md.
- Resolve knowledge base docs root in this order:
  1. KB_DOCS_ROOT (if set)
  2. sibling knowledge-base skill root: <skills-parent>/knowledge-base/assets/docs/
  3. fail with a clear error if no valid docs root is found

## Storage And Naming
- Destination root: <knowledge-base-skill-root>/assets/docs/
- Category strategy:
  - infer from topic/content; fallback to general
- Filename strategy:
  - slug(topic) or slug(source-title)
  - append date suffix if conflict exists

## Assets
- Template for generated docs:
  - <learn-skill-root>/assets/templates/learned-doc-template.md

## Workflow
1. Parse input to determine source type:
  - URL (http/https)
  - Local path (md, txt, pdf supported when readable)
2. Validate allowed source policy:
  - URL must be public and reachable without authentication.
  - Local path must exist and be user-provided.
3. Acquire source content:
  - URL: fetch page content.
  - Local file: read file content.
4. Extract core knowledge and produce concise structured markdown using the learned-doc template.
5. Infer category and normalize title/topic.
6. Ensure destination folder exists under the resolved knowledge-base assets/docs root.
7. Write new doc with source attribution and learned timestamp.
8. Return created file path, topic, category, and source summary.

## Safety Rules
- Never access private/authenticated pages.
- Never execute downloaded code or embedded scripts from sources.
- Never overwrite existing docs without explicit user approval.
- Reject sources that appear malicious or unrelated to the requested topic.
- Preserve attribution and clearly label synthesized content.

## Confirmation Rules
- No confirmation needed for creating new docs.
- Confirmation required before overwriting, deleting, or moving existing docs.

## Environment Variables
- Required: none.
- Optional:
  - KB_DOCS_ROOT: <knowledge-base-skill-root>/assets/docs (default when resolvable)
  - LEARN_DEFAULT_CATEGORY: general (default fallback)
- Validation:
  - Resolved destination must stay inside allowed workspace boundaries.
  - Topic/category must be path-safe.
- Secrets:
  - No secrets are required.

## External Dependencies
- None required beyond built-in agent tools.

## Integration Contract
- Designed to be called directly by users or automatically by /knowledge-base.
- Must return enough metadata for /knowledge-base to re-query:
  - created file path
  - category
  - inferred topic/title
  - source location

## Out Of Scope
- Authenticated scraping or credential-based access.
- Bulk site crawling/indexing.
- Executing code from learned content.
- Non-document persistence formats (database/vector index) in MVP.

## Example Prompts
- /learn https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_intro.html ansible playbook basics
- /learn C:/Users/kyleh/Downloads/nginx-notes.pdf nginx tuning

## References
- Tool and command references: references/tools.md
- Template used for generated content: assets/templates/learned-doc-template.md
