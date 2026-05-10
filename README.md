# team-ai-warehouse

**Universal AI Agent Standardization Platform (UAASP)** — A skill/agent registry for team-wide AI-assisted development.

This is the **warehouse** — a synchronized copy of AI agent skills that can be shared across multiple AI coding tools.

## What is this?

- **Skills**: Pre-defined instructions for AI agents (e.g., `/qa`, `/design-review`, `/autoplan`)
- **Warehouse**: Central repository that syncs skills to multiple AI tools
- **Supported tools**: Claude Code, OpenCode, Codex, Pi

## Quick Start (One-Liner)

```bash
# Install
curl -sSL https://raw.githubusercontent.com/bigknoxy/team-ai-warehouse/main/scripts/setup.sh | bash

# Uninstall
curl -sSL https://raw.githubusercontent.com/bigknoxy/team-ai-warehouse/main/scripts/setup.sh | bash -s -- --uninstall
```

## Manual Setup

```bash
# Clone
git clone https://github.com/bigknoxy/team-ai-warehouse.git
cd team-ai-warehouse

# Initialize
python3 scripts/uaa init

# Sync skills to all tools
python3 scripts/uaa sync --all

# Verify
python3 scripts/uaa status
```

## Key Commands

| Command | Description |
|---------|-------------|
| `python3 scripts/uaa init` | Initialize warehouse |
| `python3 scripts/uaa sync` | Sync skills to tool directories |
| `python3 scripts/uaa sync --all` | Sync to all 4 tools |
| `python3 scripts/uaa status` | Show skill counts |
| `python3 scripts/uaa list` | List all skills |
| `python3 scripts/uaa validate` | Validate SKILL.md files |
| `python3 scripts/uaa tag v1.0.0` | Create version tag |
| `python3 scripts/uaa contrib <skill>` | Create PR for a skill |

## Directory Structure

```
├── skills/               # SKILL.md files
│   ├── gstack/         # ~34 skills (migrated from upstream)
│   ├── team/           # Team-specific skills
│   └── personal/       # Personal skills (Josh)
├── scripts/            # CLI tools
│   ├── uaa            # Main CLI (Python)
│   ├── validate-skill.py  # SKILL.md validator
│   ├── setup.sh       # One-line installer
│   └── track.py       # Metrics logger
├── contexts/           # Startup instructions for tools
├── training/           # Learning materials
├── testing/            # Unit tests
└── .github/workflows/  # CI/CD
```

## Documentation

- [PROJECT_SUMMARY.md](./PROJECT_SUMMARY.md) — Full project history
- [AGENTS.md](./AGENTS.md) — Agent instructions
- [contexts/AGENTS.md](./contexts/AGENTS.md) — Universal startup context
- [docs/branch-protection.md](./docs/branch-protection.md) — Branch protection guide

## CI/CD

- **CI**: Runs on every PR → validates SKILL.md files, runs Python tests, linting
- **Release**: Auto-creates GitHub Release on tag push (`v*`)

## Contributing

1. Add/edit skill in `skills/team/` or `skills/personal/`
2. Run `python3 scripts/validate-skill.py skills/<category>/<skill>`
3. Commit and push
4. Create PR → requires 1 approval + CI passing

## Requirements

- Python 3.11+
- Git
- GitHub CLI (for `uaa contrib`)