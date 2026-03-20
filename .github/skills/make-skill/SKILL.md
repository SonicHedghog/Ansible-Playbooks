---
name: make-skill
description: Gather detailed requirements and generate a new skill scaffold, including scripts, env vars, and storage scope (global or local).
---
# /make-skill Skill

## Purpose
`/make-skill` helps an agent design and create another skill by running a structured interview with the user, then generating the skill files in the correct location.

This skill must:
1. Ask targeted questions to understand the skill's goal and workflow.
2. Ask follow-up questions to remove ambiguity.
3. Offer concrete options when the user is unsure.
4. Determine whether the new skill is local or global.
5. Prefer existing command-line tools over generating scripts.
6. Create scripts only when logic is complex, multi-step, or needs reusable static behavior.
7. Create the skill scaffold and any requested scripts/config.

## Step-by-step workflow
1. Start with a short summary of what `/make-skill` will do.
2. Run a discovery interview. Ask one focused question at a time and follow up until answers are specific enough to implement.
3. If user answers are vague, propose choices and explain tradeoffs in simple terms.
4. Confirm scope (what the skill should do and should not do).
5. Confirm output files (at minimum `SKILL.md`).
6. Prefer command examples that use available CLI tools directly.
7. Add scripts/templates/config only if the user explicitly wants them or complexity justifies them.
8. Ask whether the new skill should be local or global.
9. Resolve destination path from the active assistant environment, then treat that directory as the new skill root.
10. In generated instructions and examples, use skill-root-relative paths (for example `assets/`, `references/`, `scripts/`) rather than assistant-specific absolute or parent paths.
11. Generate files with concrete, user-approved behavior.
12. Create or update a `references` section/file documenting every CLI tool and script used by the generated skill.
13. Place any non-doc/script artifacts in `assets/`.
14. Summarize created files and key decisions.

## Discovery questions (required topics)
Ask questions until each topic is clear:
- Skill name and one-line description.
- Primary task(s) the skill should help with.
- Expected invocation shape (for example `/skill-name <arg>`).
- Inputs the user will provide.
- Outputs/artifacts the skill should produce.
- Non-doc/script artifacts that should be created under `assets/`.
- Whether scripts are actually needed, or if CLI commands are sufficient.
- If scripts are needed, language/runtime and script names.
- Environment variables:
  - Which variables are required vs optional.
  - Defaults and validation rules.
  - Secret handling expectations.
- External tools/dependencies required.
- Documentation expectations for tools/scripts to include in `references`.
- Safety constraints (what must never happen).
- Whether the skill should ask for confirmation before destructive actions.
- Example user prompts and expected behavior.
- Out-of-scope behaviors (explicitly list what the skill will not do).

## When user is unsure
If the user does not know how to answer, provide practical options and recommend one:
- Prefer "no scripts" and direct CLI commands when feasible.
- Script language options (Python, PowerShell, Bash) only when complexity or reuse requires it.
- Interaction style (single command vs multi-step interview).
- Error handling style (fail-fast vs guided recovery).
- Scope style (minimal MVP vs broader automation).

Use plain language and explain why a recommendation is useful.

## Tooling preference policy
Default behavior:
- Use existing command-line tools directly in the skill instructions whenever possible.
- Avoid generating Bash/Python scripts for simple one-off command sequences.

Generate scripts only when at least one of these is true:
- The workflow is complex enough that inline commands would be hard to maintain.
- Logic needs reusable/static behavior (shared parsing, transformation, validation, or orchestration).
- Cross-platform branching or robust error handling would be too bulky in inline command steps.
- The user explicitly requests script generation.

## References documentation policy
Any generated skill must include documentation material under `references` for every CLI tool or script it uses.

Required coverage per tool/script:
- What it does in the workflow.
- Exact command shape(s) used by the skill.
- Important flags/arguments and defaults.
- Expected inputs/outputs.
- Error/exit behavior or common failure modes relevant to the skill.

Placement rules:
- Add a `## References` section in the generated `SKILL.md` for concise entries.
- If references are long, create `references/` files (for example `references/tools.md` or `references/<tool>.md`) and link them from `SKILL.md`.
- Keep references aligned with the actual commands and scripts used by the generated skill.

## Assets policy
Any generated artifact that is not documentation or an executable script must go under `assets/`.

Examples:
- Templates, sample payloads, fixture data, schema snippets, static config examples, diagrams, and prompt snippets.

Placement rules:
- Use `assets/` at the skill root for non-doc/script files.
- Use subfolders when needed (for example `assets/templates/`, `assets/examples/`, `assets/data/`).
- Keep filenames descriptive and reference them from `SKILL.md` when they are part of the workflow.

## Storage rules (must ask explicitly)
Always ask:
"Should this new skill be local to this repository or global to your machine?"

Then store in the matching location as resolved by the active assistant environment.

For all generated docs, instructions, and references:
- Use paths relative to the created skill root.
- Do not require a specific parent directory name.

If the target directory does not exist, create it.

## Generation contract
When generating the new skill:
1. Include YAML frontmatter:
   - `name`
   - `description`
2. Include a clear purpose section.
3. Include step-by-step workflow for the agent.
4. Include command/script references if scripts are part of scope.
5. Include safety rules and confirmation requirements.
6. Include an invocation and integration contract.
7. Include `references` documentation for every CLI tool and script used.
8. Place all other required artifacts in `assets/`.

## Quality bar
- Be specific over generic.
- Prefer concrete commands, paths, and examples.
- Avoid hidden assumptions; ask follow-ups when needed.
- Do not finish until required topics are sufficiently defined.
