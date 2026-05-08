# Writing Skills

## SKILL.md Anatomy

Every skill is a `SKILL.md` file with YAML frontmatter and markdown body:

```markdown
---
name: my-skill
description: Brief description of what this skill does
---

# My Skill

Instructions for the AI agent...
```

## YAML Frontmatter Fields

| Field | Required | Description |
|-------|----------|-------------|
| `name` | Yes | Unique skill identifier (lowercase, hyphens) |
| `description` | Yes | When to trigger this skill (used by agent routing) |
| `location` | No | Path to skill resources (defaults to skill dir) |

## Writing Your First Skill

1. Create a new directory in `skills/`:

```bash
mkdir -p skills/my-first-skill
cd skills/my-first-skill
```

2. Create `SKILL.md`:

```markdown
---
name: greet-user
description: Greet a user by name in a friendly, personalized way
---

# Greet User Skill

When the user asks to be greeted or says hello:

1. Extract the user's name from context or ask for it
2. Use a warm, friendly tone
3. Include a personalized detail if available

Example greeting format:
> Hello, {name}! Great to see you working on {project} today.
```

3. Validate your skill:

```bash
./scripts/uaa validate skills/my-first-skill/SKILL.md
```

4. Test the skill:

```bash
./scripts/uaa test --skill greet-user
```

## Best Practices

- **Description is the trigger**: Write descriptions that match user intent phrases
- **Be concise**: Agents work better with focused, actionable instructions
- **Include examples**: Show, don't just tell
- **One job per skill**: Keep skills single-purpose for better composability
