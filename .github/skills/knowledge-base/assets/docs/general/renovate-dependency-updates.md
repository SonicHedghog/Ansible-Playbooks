---
title: Renovate Dependency Update Automation
category: general
source: https://docs.renovatebot.com/
learned_at: 2026-03-20T00:00:00Z
confidence: medium
---

# Renovate Dependency Update Automation

## Summary
Renovate automates dependency updates by scanning repositories for supported dependency files and opening pull requests with controlled update policies. It is commonly used to keep CI actions, package dependencies, and lock files current without manual tracking.

## Key Concepts
- Renovate can run as a GitHub app or self-hosted runner and is supported on GitHub and GitLab.
- Configuration is repository-driven and typically starts from `config:recommended` in `renovate.json` or `renovate.json5`.
- `packageRules` are the primary control mechanism for grouping, labeling, scheduling, and automerge behavior.
- The `github-actions` manager updates action references in workflow files and can also handle digest pinning scenarios.
- For non-standard version declarations, `customManagers` with `regex` can extract and update dependencies using named capture groups.

## Procedures
1. Enable Renovate on the repository and add a baseline config with conservative defaults.
2. Start with `extends: ["config:recommended"]` and add explicit `packageRules` for update scope and PR noise control.
3. Add manager-specific configuration (for example GitHub Actions) when workflow dependencies need custom handling.
4. Validate behavior on initial PRs, then incrementally tune grouping, automerge, and approval policies.
5. Use dependency dashboard and status checks before broadening automerge rules.

## Caveats
- Aggressive automerge without strong CI checks can introduce regressions.
- Regex custom managers require RE2-compatible patterns; lookaheads/backreferences are not supported.
- Some advanced configuration pages were not fetchable during this run, so this summary emphasizes verified manager and preset guidance.

## Sources
- https://docs.renovatebot.com/
- https://docs.renovatebot.com/modules/manager/github-actions/
- https://docs.renovatebot.com/modules/manager/regex/
- https://docs.renovatebot.com/presets-default/
