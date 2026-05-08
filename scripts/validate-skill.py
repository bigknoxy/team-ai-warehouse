#!/usr/bin/env python3
"""
SKILL.md Validator - validates skills against agentskills.io specification
Usage: python3 validate-skill.py <skill-directory>
"""

import sys
import os
import re

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML library is required. Install it with: pip install PyYAML")
    sys.exit(1)

def validate_skill(skill_dir):
    """Validate a single skill directory against the SKILL.md spec."""
    errors = []
    warnings = []
    
    # Check 1: SKILL.md exists
    skill_md = os.path.join(skill_dir, "SKILL.md")
    if not os.path.isfile(skill_md):
        errors.append(f"MISSING: SKILL.md not found in {skill_dir}")
        return errors, warnings
    
    # Read file
    with open(skill_md, 'r') as f:
        content = f.read()
    
    # Check 2: Has YAML frontmatter between ---
    if not content.startswith('---'):
        errors.append("INVALID: SKILL.md must start with --- (YAML frontmatter)")
        return errors, warnings
    
    parts = content.split('---', 2)
    if len(parts) < 3:
        errors.append("INVALID: SKILL.md must have YAML frontmatter between --- delimiters")
        return errors, warnings
    
    yaml_text = parts[1]
    body = parts[2]
    
    # Parse YAML
    try:
        frontmatter = yaml.safe_load(yaml_text)
    except yaml.YAMLError as e:
        errors.append(f"INVALID YAML: {e}")
        return errors, warnings
    
    if not isinstance(frontmatter, dict):
        errors.append("INVALID: YAML frontmatter must be a dictionary")
        return errors, warnings
    
    # Check 3: Required fields
    if 'name' not in frontmatter:
        errors.append("MISSING: 'name' field is required")
    if 'description' not in frontmatter:
        errors.append("MISSING: 'description' field is required")
    
    # Check 4: name validation
    if 'name' in frontmatter:
        name = frontmatter['name']
        if not isinstance(name, str):
            errors.append("INVALID: 'name' must be a string")
        else:
            # Length check
            if len(name) < 1:
                errors.append("INVALID: 'name' must be at least 1 character")
            if len(name) > 64:
                errors.append(f"INVALID: 'name' must be <= 64 chars (got {len(name)})")
            
            # Character check
            if not re.match(r'^[a-z0-9-]+$', name):
                errors.append("INVALID: 'name' can only contain lowercase letters, numbers, hyphens")
            if name.startswith('-'):
                errors.append("INVALID: 'name' cannot start with hyphen")
            if name.endswith('-'):
                errors.append("INVALID: 'name' cannot end with hyphen")
            if '--' in name:
                errors.append("INVALID: 'name' cannot contain consecutive hyphens")
            
            # Check name matches directory
            dir_name = os.path.basename(os.path.normpath(skill_dir))
            if name != dir_name:
                errors.append(f"MISMATCH: name '{name}' doesn't match directory '{dir_name}'")
    
    # Check 5: description validation
    if 'description' in frontmatter:
        desc = frontmatter['description']
        if not isinstance(desc, str):
            errors.append("INVALID: 'description' must be a string")
        else:
            if len(desc) < 1:
                errors.append("INVALID: 'description' must be at least 1 character")
            if len(desc) > 1024:
                errors.append(f"INVALID: 'description' must be <= 1024 chars (got {len(desc)})")
    
    # Check 6: optional field validation
    if 'compatibility' in frontmatter:
        comp = frontmatter['compatibility']
        if isinstance(comp, str) and len(comp) > 500:
            errors.append(f"INVALID: 'compatibility' must be <= 500 chars (got {len(comp)})")
    
    # Check 7: body length recommendation
    body_lines = body.strip().count('\n')
    if body_lines > 500:
        warnings.append(f"RECOMMENDATION: body is {body_lines} lines (recommended <= 500)")
    
    return errors, warnings

def resolve_skill_dir(path):
    """Resolve a path to a skill directory (handles both dir and SKILL.md file)."""
    if os.path.isfile(path) and path.endswith('SKILL.md'):
        return os.path.dirname(path)
    elif os.path.isdir(path):
        return path
    else:
        return None

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 validate-skill.py <skill-directory> or <path/to/SKILL.md>")
        sys.exit(1)
    
    skill_dir = resolve_skill_dir(sys.argv[1])
    
    if skill_dir is None:
        print(f"ERROR: {sys.argv[1]} is not a valid skill directory or SKILL.md file")
        sys.exit(1)
    
    print(f"Validating: {skill_dir}")
    print("=" * 50)
    
    errors, warnings = validate_skill(skill_dir)
    
    if warnings:
        print("\nWARNINGS:")
        for w in warnings:
            print(f"  ⚠️  {w}")
    
    if errors:
        print("\nERRORS:")
        for e in errors:
            print(f"  ❌ {e}")
        print(f"\nValidation FAILED ({len(errors)} errors)")
        sys.exit(1)
    else:
        print("\n✅ Validation PASSED")
        sys.exit(0)

if __name__ == "__main__":
    main()
