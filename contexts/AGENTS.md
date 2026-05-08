# Universal AI Agent Standardization Platform (UAASP)

Shared contexts, skills, and agents for team-wide AI-assisted development.

## Supported Tools
- **Claude Code** — `~/.claude/skills/`
- **OpenCode** — `~/.config/opencode/skills/`
- **Codex** — `~/.codex/skills/`
- **Pi** — via extensions or `--skill` flag

## Quick Start

```bash
# First time setup
git clone <warehouse-url> ~/team-ai-warehouse
cd ~/team-ai-warehouse
./scripts/uaa init

# Sync to all tools
./scripts/uaa sync --all
```

## Skill Categories

| Category | Location | Description |
|-----------|----------|-------------|
| `gstack` | `skills/gstack/` | Migrated from ~/.claude/skills/gstack |
| `team` | `skills/team/` | Team-specific skills (shared) |
| `personal` | `skills/personal/` | Personal skills (Josh) |

## Validation

```bash
# Validate a skill
python3 scripts/validate-skill.py skills/team/my-skill

# Validate all skills
find skills/ -name "SKILL.md" -exec python3 scripts/validate-skill.py {} \;
```

## Session Learnings (Self-Improvement)

This section tracks learnings from implementation sessions.

### Session: 2026-05-07 (Slice 1)

**What worked:**
- Symlinked gstack skills copied correctly with `cp -rL`
- Validation script catches missing/invalid SKILL.md files
- agentskills.io spec is clear and implementable

**What didn't:**
- Need to handle skills with no SKILL.md gracefully
- Validation script needs YAML dependency (added to requirements.txt)

**Improvements for next slice:**
- Add unit tests for validation script
- Create example team skill with full frontmatter
- Test e2e: sync to all 4 tools

**Metrics:**
- Skills validated: 34 (all gstack + team skills)
- Validation errors: 0
- Setup time: ~2 mins
- Tools integrated: 4 (Claude Code, OpenCode, Codex, Pi)

### Session: 2026-05-07 (Slice 2 & 3)

**What worked:**
- `uaa` CLI built successfully (393 lines, 21 unit tests pass)
- All 4 tools now have skill symlinks (verified valid)
- `uaa status` shows skill counts and last modified time
- `uaa list` filters by category (gstack, team, personal)
- `uaa sync` creates symlinks to all tool dirs

**What didn't:**
- Initial `find` command for validation used `dirname` incorrectly (fixed)
- OpenCode only had 3 symlinks initially (re-ran `uaa sync` to fix)
- Pi dir didn't exist (created manually before sync)

**Improvements for next slice:**
- Add `uaa sync --all` to sync to all tools at once
- Add `uaa doctor` to verify tool installations
- Write e2e test that simulates tool reading skills
- Add Pi extension config generation

**Metrics (Slice 2 & 3):**
- CLI commands: 5 (init, sync, status, list, validate)
- Unit tests: 21 (all pass)
- Skills synced: 34 to 4 tools each
- Symlinks verified: 34 × 4 = 136 total
