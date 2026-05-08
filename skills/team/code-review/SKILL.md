---
name: code-review
description: |
  Team code review skill. Use when reviewing PRs, diffs, or code changes.
  Checks for security patterns, team coding standards, and generates findings
  in consistent severity format (Critical/Warning/Suggestion).
license: MIT
metadata:
  author: team-leads
  version: "1.0.0"
  tags: [team, review, security]
allowed-tools: Bash(git:*) Read Grep
---

# Team Code Review Skill

## Review Checklist

### Security (Critical)
- [ ] No hardcoded secrets or API keys
- [ ] All user inputs are validated/sanitized
- [ ] SQL queries use parameterized statements
- [ ] Authentication checks are present on protected endpoints

### Team Standards (Warning)
- [ ] Functions have TypeScript types (if applicable)
- [ ] Error handling follows team pattern (Result type / try-catch)
- [ ] New endpoints have integration tests
- [ ] Commit messages follow conventional commits

### Style & Quality (Suggestion)
- [ ] Code is DRY (no obvious duplication)
- [ ] Functions are under 50 lines
- [ ] Variable names are descriptive
- [ ] No commented-out code left in place

## Severity Levels

| Level | Description | Action |
|-------|-------------|--------|
| **Critical** | Security issue, data loss risk, breaks production | Block PR |
| **Warning** | Bug, missing test, incorrect error handling | Request changes |
| **Suggestion** | Style improvement, refactoring opportunity | Optional feedback |

## Output Format

```
## Code Review Findings

### Critical Issues (N)
1. [File:Line] Description with context

### Warnings (N)
1. [File:Line] Description with context

### Suggestions (N)
1. [File:Line] Description with context

### Summary
- Files reviewed: N
- Critical: N | Warnings: N | Suggestions: N
- Recommendation: APPROVE / REQUEST CHANGES
```

## Team-Specific Rules

- We use conventional commits: `feat:`, `fix:`, `chore:`, etc.
- All PRs need at least 1 reviewer approval
- Database changes need migration script + rollback plan
