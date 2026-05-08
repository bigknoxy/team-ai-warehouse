# Team Collaboration

## Fork Workflow

UAASP uses a fork-based workflow for team collaboration:

### 1. Fork the Warehouse

```bash
# Fork on GitHub/GitLab, then clone your fork
git clone https://github.com/your-username/team-ai-warehouse.git
cd team-ai-warehouse
```

### 2. Create a Feature Branch

```bash
git checkout -b feature/new-skill-name
```

### 3. Make Changes and Commit

```bash
# Add your skill
git add skills/my-new-skill/
git commit -m "feat: add my-new-skill for X use case"
```

### 4. Push and Create Pull Request

```bash
git push origin feature/new-skill-name
# Create PR on GitHub/GitLab
```

## Code Review Checklist

Reviewers should check:

- [ ] `SKILL.md` has valid YAML frontmatter
- [ ] Description clearly indicates when to trigger
- [ ] Instructions are actionable and specific
- [ ] No secrets or sensitive data in skill files
- [ ] Examples provided where helpful
- [ ] Compatible with all target agents

## `uaa contrib` - Contributing Back

The `uaa contrib` command helps streamline contributions:

```bash
# Check what skills you've added locally
./scripts/uaa contrib --list-local

# Validate all your contributions
./scripts/uaa contrib --validate

# Generate a contribution summary for your PR
./scripts/uaa contrib --summary

# Interactive mode - walks you through contributing
./scripts/uaa contrib --interactive
```

## Team Conventions

| Convention | Value |
|------------|-------|
| Branch prefix | `feature/`, `fix/`, `docs/` |
| Commit style | Conventional Commits |
| Skill naming | `lowercase-with-hyphens` |
| Max skill size | 10KB `SKILL.md` |
| Required review | 1 approver minimum |

## Syncing Team Updates

```bash
# Add upstream remote (first time only)
git remote add upstream https://github.com/team/team-ai-warehouse.git

# Fetch and merge upstream changes
git fetch upstream
git checkout main
git merge upstream/main

# Re-sync your agent
./scripts/uaa sync
```
