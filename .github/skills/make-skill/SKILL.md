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
5. Create the skill scaffold and any requested scripts/config.

## Step-by-step workflow
1. Start with a short summary of what `/make-skill` will do.
2. Run a discovery interview. Ask one focused question at a time and follow up until answers are specific enough to implement.
3. If user answers are vague, propose choices and explain tradeoffs in simple terms.
4. Confirm scope (what the skill should do and should not do).
5. Confirm output files (at minimum `SKILL.md`, plus scripts/templates/config if needed).
6. Ask whether the new skill should be local or global.
7. Resolve destination path (agent should know the standard paths for local vs global skills).
8. Generate files with concrete, user-approved behavior.
9. Summarize created files and key decisions.

## Discovery questions (required topics)
Ask questions until each topic is clear:
- Skill name and one-line description.
- Primary task(s) the skill should help with.
- Expected invocation shape (for example `/skill-name <arg>`).
- Inputs the user will provide.
- Outputs/artifacts the skill should produce.
- Whether scripts should be generated; if yes, language/runtime and script names.
- Environment variables:
  - Which variables are required vs optional.
  - Defaults and validation rules.
  - Secret handling expectations.
- External tools/dependencies required.
- Safety constraints (what must never happen).
- Whether the skill should ask for confirmation before destructive actions.
- Example user prompts and expected behavior.
- Out-of-scope behaviors (explicitly list what the skill will not do).

## When user is unsure
If the user does not know how to answer, provide practical options and recommend one:
- Script language options (Python, PowerShell, Bash, no scripts).
- Interaction style (single command vs multi-step interview).
- Error handling style (fail-fast vs guided recovery).
- Scope style (minimal MVP vs broader automation).

Use plain language and explain why a recommendation is useful.

## Storage rules (must ask explicitly)
Always ask:
"Should this new skill be local to this repository or global to your machine?"

Then store in the matching location (the agent should know the standard paths for local vs global skills).

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

## Quality bar
- Be specific over generic.
- Prefer concrete commands, paths, and examples.
- Avoid hidden assumptions; ask follow-ups when needed.
- Do not finish until required topics are sufficiently defined.
