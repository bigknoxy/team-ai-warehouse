# Milestone Planning - team-ai-warehouse

## Current State (v1.0.0)
- 34 skills in warehouse
- 4 tools integrated (Claude Code, OpenCode, Codex, Pi)
- 9 CLI commands (init, sync, status, list, validate, rollback, version, tag, contrib)
- CI/CD pipeline configured
- Branch protection enabled
- One-line install/uninstall working

## Potential Milestones (Ranked by Impact)

### 1. `uaa doctor` - Diagnostic Command (HIGH PRIORITY)
**Problem:** Users have no way to diagnose why skills aren't appearing in their tools.
**Solution:** A `uaa doctor` command that:
- Verifies each tool's skill directory exists
- Checks symlinks are valid (not broken)
- Validates SKILL.md files in each tool dir
- Reports tool-specific issues
- Offers auto-fix for common problems

**TDD Approach:** 
- Test doctor command with broken symlinks
- Test doctor command with missing directories
- Test doctor command with invalid SKILL.md
- Test auto-fix functionality
- Test output formatting

### 2. More Tool Integrations (MEDIUM PRIORITY)
**Problem:** Only 4 tools supported, but users want Cursor, Windsurf, Gemini CLI
**Solution:** Add tool adapter framework, implement adapters for:
- Cursor (uses `.cursor/rules/`)
- Windsurf (uses `.windsurf/`)
- Gemini CLI (uses `~/.gemini-cli/skills/`)

### 3. Skill Search & Discovery (MEDIUM PRIORITY)
**Problem:** No way to find skills by keyword or category
**Solution:** `uaa search <query>` - fuzzy search across skill names/descriptions
- Filter by category (gstack, team, personal)
- Filter by tool compatibility
- Rank by relevance

### 4. Skill Metrics Dashboard (LOWER PRIORITY)
**Problem:** Basic tracking exists but not actionable
**Solution:** Enhanced analytics:
- Most used skills
- Success/failure rates per skill
- Team adoption metrics
- Time-to-competency tracking

### 5. Per-Skill Versioning (LOWER PRIORITY)
**Problem:** Can only version entire warehouse
**Solution:** Individual skill versioning with:
- Changelog per skill
- Rollback single skills
- Deprecate skills gracefully

---

## Selected Top Milestone: `uaa doctor`

**Rationale:**
1. High impact - immediately useful for debugging
2. Well-testable with TDD (multiple failure scenarios)
3. Follows SOLID (single responsibility for diagnostics)
4. Follows DRY (reuses existing validate-skill.py logic)
5. Small enough to implement in one session
6. Addresses real user pain point (skills not showing up)

**Implementation Plan:**
1. Write tests first (TDD)
2. Implement doctor command
3. Add auto-fix capabilities
4. Test with various broken states
5. Add subcommands: check, fix, report

**Acceptance Criteria:**
- Detects broken symlinks
- Detects missing tool directories
- Detects invalid SKILL.md files
- Can auto-fix common issues
- Outputs actionable report
- All tests pass