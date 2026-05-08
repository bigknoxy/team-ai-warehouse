# Advanced Patterns

## Multi-Tool Design

Skills can leverage multiple tools for complex workflows:

```markdown
---
name: full-stack-review
description: Run CEO, design, and eng reviews sequentially with auto-decisions
---

# Full Stack Review

## Phase 1: CEO Review
Load `/plan-ceo-review` skill and run with scope expansion mode.

## Phase 2: Design Review
Load `/plan-design-review` and rate each dimension 0-10.

## Phase 3: Eng Review
Load `/plan-eng-review` to lock in architecture.

## Auto-Decision Principles
1. Prefer scope expansion when ROI > 2x
2. Fix design issues scoring < 7
3. Always address security concerns
```

## Agent-Specific Optimizations

Tailor skills for different agents:

```markdown
---
name: codex-consult
description: Consult Codex CLI for second opinions
---

# Codex Consult

## For Codex (OpenAI)
Use the codex CLI wrapper with session continuity.

## For Claude
Invoke via `/codex` skill which wraps the CLI.

## For OpenCode
Use the skill directly - it detects the codex binary.
```

## Hooks

Hooks trigger skills automatically on events:

```yaml
# In warehouse.yaml
hooks:
  pre-commit:
    - skill: lint-skill-md
      args: --check-frontmatter
  post-sync:
    - skill: validate-all
      args: --quiet
```

## MCP (Model Context Protocol) Integration

Skills can declare MCP server dependencies:

```markdown
---
name: browser-qa
description: QA test with headless browser via MCP
mcp:
  - name: playwright
    server: npx @modelcontextprotocol/server-playwright
---

# Browser QA

Use the Playwright MCP server tools:
- `playwright_navigate` - Navigate to URL
- `playwright_screenshot` - Capture screenshot
- `playwright_click` - Click elements
```

## Composing Skills

Build complex workflows from simple skills:

```markdown
---
name: autoplan
description: Auto-review pipeline running CEO + design + eng reviews
depends:
  - plan-ceo-review
  - plan-design-review
  - plan-eng-review
---

# Autoplan

1. Load plan-ceo-review, run with auto-decisions
2. Load plan-design-review, apply results
3. Load plan-eng-review, lock in plan
4. Surface taste decisions at approval gate
```

## Parameterized Skills

Pass dynamic values to skills:

```markdown
---
name: deploy-check
description: Check deployment status with configurable timeout
---

# Deploy Check

Arguments:
- `timeout` (default: 30s)
- `environment` (default: production)

Run: `uaa run deploy-check --timeout 60s --environment staging`
```
