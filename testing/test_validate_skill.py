#!/usr/bin/env python3
"""
Unit tests for SKILL.md validator (scripts/validate-skill.py).

Run with:
  cd /home/josh/team-ai-warehouse && python3 -m pytest testing/test_validate_skill.py -v
"""

import os
import sys
import tempfile
import unittest

# Add scripts/ to path so we can import validate_skill
_SCRIPTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'scripts'))
if _SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, _SCRIPTS_DIR)
import importlib.util
_spec = importlib.util.spec_from_file_location("validate_skill", os.path.join(_SCRIPTS_DIR, "validate-skill.py"))
_validate_skill_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_validate_skill_mod)
validate_skill = _validate_skill_mod.validate_skill


def write_skill_md(directory, name=None, description=None, extra_yaml=None, body=""):
    """Helper: write a SKILL.md file into *directory* and return the path."""
    lines = ["---"]
    if name is not None:
        lines.append(f"name: {name!r}")
    if description is not None:
        lines.append(f"description: {description!r}")
    if extra_yaml:
        lines.append(extra_yaml)
    lines.append("---")
    lines.append(body)
    path = os.path.join(directory, "SKILL.md")
    with open(path, "w") as f:
        f.write("\n".join(lines) + "\n")
    return path


class TestValidSkills(unittest.TestCase):
    """Skills that should pass validation."""

    def test_valid_skill(self):
        """Skill with all required fields passes."""
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = os.path.join(tmpdir, "my-skill")
            os.makedirs(skill_dir)
            write_skill_md(skill_dir, name="my-skill", description="A valid skill", body="Some body text")
            errors, warnings = validate_skill(skill_dir)
            self.assertEqual(errors, [])
            self.assertEqual(warnings, [])

    def test_minimal_skill(self):
        """Skill with only name + description passes."""
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = os.path.join(tmpdir, "minimal")
            os.makedirs(skill_dir)
            write_skill_md(skill_dir, name="minimal", description="Short")
            errors, warnings = validate_skill(skill_dir)
            self.assertEqual(errors, [])
            self.assertEqual(warnings, [])


class TestInvalidSkills(unittest.TestCase):
    """Skills that should fail validation."""

    def test_missing_skill_md(self):
        """Directory without SKILL.md returns error."""
        with tempfile.TemporaryDirectory() as tmpdir:
            errors, warnings = validate_skill(tmpdir)
            self.assertEqual(len(errors), 1)
            self.assertIn("MISSING", errors[0])

    def test_missing_name(self):
        """Frontmatter missing 'name' field."""
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = os.path.join(tmpdir, "test-skill")
            os.makedirs(skill_dir)
            write_skill_md(skill_dir, name=None, description="Has desc but no name")
            errors, _ = validate_skill(skill_dir)
            self.assertTrue(any("'name'" in e and "required" in e for e in errors))

    def test_missing_description(self):
        """Frontmatter missing 'description' field."""
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = os.path.join(tmpdir, "test-skill")
            os.makedirs(skill_dir)
            write_skill_md(skill_dir, name="test-skill", description=None)
            errors, _ = validate_skill(skill_dir)
            self.assertTrue(any("'description'" in e and "required" in e for e in errors))

    def test_invalid_name_chars(self):
        """Name with uppercase letters should fail."""
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = os.path.join(tmpdir, "BadName")
            os.makedirs(skill_dir)
            write_skill_md(skill_dir, name="BadName", description="Uppercase name")
            errors, _ = validate_skill(skill_dir)
            self.assertTrue(any("lowercase" in e for e in errors))

    def test_name_too_long(self):
        """Name > 64 chars should fail."""
        with tempfile.TemporaryDirectory() as tmpdir:
            long_name = "a" * 65
            skill_dir = os.path.join(tmpdir, long_name)
            os.makedirs(skill_dir)
            write_skill_md(skill_dir, name=long_name, description="Name too long")
            errors, _ = validate_skill(skill_dir)
            self.assertTrue(any("64" in e for e in errors))

    def test_description_too_long(self):
        """Description > 1024 chars should fail."""
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = os.path.join(tmpdir, "test-skill")
            os.makedirs(skill_dir)
            long_desc = "x" * 1025
            write_skill_md(skill_dir, name="test-skill", description=long_desc)
            errors, _ = validate_skill(skill_dir)
            self.assertTrue(any("1024" in e for e in errors))

    def test_name_starts_with_hyphen(self):
        """Name starting with hyphen should fail."""
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = os.path.join(tmpdir, "-bad")
            os.makedirs(skill_dir)
            write_skill_md(skill_dir, name="-bad", description="Starts with hyphen")
            errors, _ = validate_skill(skill_dir)
            self.assertTrue(any("start" in e.lower() for e in errors))

    def test_name_ends_with_hyphen(self):
        """Name ending with hyphen should fail."""
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = os.path.join(tmpdir, "bad-")
            os.makedirs(skill_dir)
            write_skill_md(skill_dir, name="bad-", description="Ends with hyphen")
            errors, _ = validate_skill(skill_dir)
            self.assertTrue(any("end" in e.lower() for e in errors))

    def test_name_consecutive_hyphens(self):
        """Name with consecutive hyphens should fail."""
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = os.path.join(tmpdir, "bad--name")
            os.makedirs(skill_dir)
            write_skill_md(skill_dir, name="bad--name", description="Consecutive hyphens")
            errors, _ = validate_skill(skill_dir)
            self.assertTrue(any("consecutive" in e.lower() for e in errors))


if __name__ == "__main__":
    unittest.main()
