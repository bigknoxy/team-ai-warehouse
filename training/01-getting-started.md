# Getting Started with UAASP

## What is SKILL.md?

The **UAASP** (Universal AI Agent Skill Protocol) is an open standard for defining reusable AI agent skills. Skills are stored in `SKILL.md` files - a human-readable, machine-parseable format that works across all major AI coding tools.

A skill is a self-contained set of instructions, workflows, and resources that an AI agent can load on-demand to perform specialized tasks.

## Installing `uaa`

The `uaa` (Universal Agent Assistant) CLI tool manages your skill warehouse:

```bash
# Clone the warehouse
git clone https://github.com/your-org/team-ai-warehouse.git
cd team-ai-warehouse

# Run the setup script
./scripts/setup.sh

# Verify installation
./scripts/uaa --version
```

## First Sync

Sync skills from the warehouse to your local agent:

```bash
# List available skills
./scripts/uaa list

# Sync all skills to your agent
./scripts/uaa sync

# Sync a specific skill
./scripts/uaa sync --skill autoplan

# Check sync status
./scripts/uaa status
```

## Supported Agents

UAASP works with:
- **Claude** (Claude Code CLI)
- **OpenCode**
- **Codex** (OpenAI)
- **Pi** (Inflection)

Each agent auto-discovers skills from their standard skill directories after sync.
