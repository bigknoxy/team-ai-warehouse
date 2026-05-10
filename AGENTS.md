# AGENTS.md — team-ai-warehouse

Universal AI Agent Standardization Platform (UAASP) — a skill/agent registry for team-wide AI-assisted development.

## Project Type

Warehouse/registry for sharing AI agent skills across multiple tools (Claude Code, OpenCode, Codex, Pi).

## Key Commands

```bash
# Main CLI (Python, no .py extension)
python3 scripts/uaa --help

# Common subcommands
python3 scripts/uaa init          # Initialize warehouse
python3 scripts/uaa sync          # Sync skills to tool dirs
python3 scripts/uaa status       # Show status + skill counts
python3 scripts/uaa list          # List all skills
python3 scripts/uaa validate     # Validate SKILL.md files

# Skill validation standalone
python3 scripts/validate-skill.py skills/gstack/skill-name

# Run tests
python3 -m pytest testing/test_validate_skill.py -v
```

## Directory Structure

| Directory | Purpose |
|-----------|---------|
| `skills/gstack/` | Migrated gstack skills (~34 skills) |
| `skills/team/` | Team-specific skills |
| `skills/personal/` | Personal skills (Josh) |
| `scripts/uaa` | Main CLI (Python, 393 lines) |
| `scripts/validate-skill.py` | SKILL.md validator |
| `testing/` | Unit tests (pytest) |
| `contexts/` | Startup instructions for tools |
| `training/` | Learning materials |
| `tracking/` | Metrics + dashboards |

## Known Issues

- `testing/test_uaa.py` has encoding issues (stray quote chars) — tests fail to load. Use `testing/test_validate_skill.py` for verified tests.

## Validation Spec

SKILL.md files must have:
- `name`: lowercase, max 64 chars, allowed: `a-z0-9-`
- `description`: max 1024 chars
- At least one of: `location`, `instructions`, `rules`

See `warehouse.yaml` for full validation config.

## References

- `contexts/AGENTS.md` — Universal startup context (all tools)
- `skills/gstack/AGENTS.md` — gstack-specific build commands
- `PROJECT_SUMMARY.md` — Full project history + metrics