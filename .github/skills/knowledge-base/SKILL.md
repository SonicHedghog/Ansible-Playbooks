---
name: knowledge-base
description: Search local knowledge docs and automatically trigger /learn when no reliable match is found.
---

# /knowledge-base Skill

## Purpose
Use this skill to answer questions from a local knowledge base of Markdown documentation. If the skill cannot find sufficient documentation, it automatically invokes /learn to acquire new knowledge and store it in the knowledge base.

## Invocation
- Primary: /knowledge-base <query>
- Optional style: /knowledge-base <query> --category <name>

## Inputs
- Required:
  - query: natural-language question or topic to find.
- Optional:
  - category: preferred category folder name under assets/docs.

## Outputs
- Direct answer synthesized from matched documentation.
- Source list of matched files used for the answer.
- If no good match exists:
  - Automatic /learn invocation request with inferred topic/source strategy.
  - Newly created documentation file under assets/docs/<category>/.
  - Final answer refreshed from newly learned documentation.

## Path Resolution
- Determine the current skill root from the location of this SKILL.md.
- Default knowledge docs root: <knowledge-base-skill-root>/assets/docs/
- Default /learn template path: <learn-skill-root>/assets/templates/learned-doc-template.md

## Storage Layout
- Knowledge root: <knowledge-base-skill-root>/assets/docs/
- Category folders: <knowledge-base-skill-root>/assets/docs/<category>/
- Preferred doc format: Markdown with frontmatter and source attribution.
- Primary generation template (owned by /learn):
  - <learn-skill-root>/assets/templates/learned-doc-template.md

## Workflow
1. Normalize the query into search terms and likely category.
2. Search existing docs under <knowledge-base-skill-root>/assets/docs/.
3. Rank matches by relevance (title hits, heading hits, body matches, freshness).
4. If confidence is high, synthesize answer and cite the files used.
5. If confidence is low or no matches are found, automatically invoke /learn using the unresolved query.
6. Re-run search after /learn stores a new doc.
7. Return the best answer with updated citations.

## Agent Rules
- Prefer existing local docs before learning from external sources.
- Auto-learn when no sufficient result is found; do not ask for confirmation for standard learning.
- Keep all learned documentation in <knowledge-base-skill-root>/assets/docs/.
- Maintain category organization and use descriptive filenames.
- Always include provenance in learned docs (source URL/path, learned timestamp).

## Safety Rules
- Never delete or overwrite existing docs unless explicitly requested.
- Never access private/authenticated websites as part of auto-learning.
- Only use publicly accessible URLs and user-provided local files.
- If source quality is uncertain, mark content as provisional in the generated doc.
- If query could trigger harmful or disallowed content, decline per policy.

## Confirmation Rules
- Confirmation is required before any destructive action (delete, move, bulk rename).
- Confirmation is not required for non-destructive doc creation during auto-learn.

## Environment Variables
- Required: none.
- Optional:
  - KB_DOCS_ROOT: Overrides default docs root. Default: <knowledge-base-skill-root>/assets/docs
  - KB_DEFAULT_CATEGORY: Category fallback when topic classification is uncertain. Default: general
- Validation:
  - Paths must resolve inside the allowed workspace boundaries.
  - Category names must be filesystem-safe (letters, numbers, dash, underscore).
- Secrets:
  - No secrets are required or expected.

## External Dependencies
- None required beyond standard agent tools.

## Integration Contract
- This skill depends on /learn for knowledge acquisition on misses.
- /learn must return:
  - destination file path
  - topic/category
  - source attribution
- After /learn completes, /knowledge-base repeats retrieval and answers from stored docs.

## Out Of Scope
- Building vector databases or semantic index services.
- Crawling private intranets or authenticated portals.
- Mutating unrelated repository files.
- Rewriting user-authored docs without explicit request.

## References
- Tool and command references: references/tools.md
