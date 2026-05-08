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

### Session: 2026-05-07 (Slice 4)

**What worked:**
- `setup.sh` script works (accepts repo URL via env var `UA_A_REPO_URL`)
- `uaa tag` creates Git tags for versioning
- `uaa contrib` creates branch, commits, pushes, opens PR
- Team feature unit tests: 17/17 pass
- Subagents (`general`, `rust-test`) handle complex tasks well

**What didn't:**
- Initial setup.sh had syntax error (fixed by subagent)
- `uaa contrib` requires `gh` CLI for PR creation (documented)

**Improvements for next slice:**
- Add `uaa doctor` to verify tool installations
- Create learning materials (training/ dir)
- Build tracking dashboard (tracking/ dir)
- Add CI/CD GitHub Action for validation

### Session: 2026-05-07 (Slice 5 - FINAL)

**What worked:**
- Training materials created (4 modules + quiz)
- Tracking dashboard built (HTML/CSS/JS, no dependencies)
- `track.py` script works (logs to metrics.jsonl)
- 302 metrics records simulated
- Quiz file created (7 questions with answers)
- E2E tests pass: 7/7 checks pass

**What didn't:**
- Subagent didn't create quiz file in correct path (fixed manually)
- `training/quizzes/` dir wasn't created by subagent (created manually)

**Improvements for production:**
- Add `uaa learn` command to open training materials
- Add `uaa dashboard` command to open tracking dashboard
- Add real CI/CD GitHub Action for validation
- Add `uaa doctor` command to verify tool installations

**Final Metrics (All Slices):**
- Total unit tests: 49 (21 CLI + 17 team features + 11 validator = 49 ALL PASS)
- Skills in warehouse: 34 (gstack) + 1 (team) = 35 total
- Tools integrated: 4 (Claude Code, OpenCode, Codex, Pi)
- Symlinks verified: 136 (34 × 4)
- Training modules: 4 + 1 quiz
- Tracking records: 302

**Self-Improvement Summary:**
- Used `general` subagent for complex implementation (CLI, team features, Slice 5)
- Used `rust-test` subagent for unit tests (faster, more thorough)
- Used `explore` subagent for research (SKILL.md spec)
- Pattern: subagent builds → I verify → write tests → e2e → update AGENTS.md
- Session monitoring: tracked metrics per slice, updated AGENTS.md after each
- Key learning: subagents handle complex tasks well, but always verify their output (quiz file path issue)

**Next Steps (Post-Session):**
1. Push to GitHub: `git init && git remote add origin <url> && git push -u origin main`
2. Share with team: `curl -sSL <raw-url>/scripts/setup.sh | bash`
3. Monitor adoption: `python3 scripts/track.py` + open `tracking/dashboard.html`
4. Iterate: Add more team skills to `skills/team/`
5. Scale: Add more tools (Cursor, Windsurf, Gemini CLI)
