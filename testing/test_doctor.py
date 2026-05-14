"""
Unit tests for uaa doctor command - TDD approach.

Run with:
  cd /home/josh/projects/team-ai-warehouse && python3 -m pytest testing/test_doctor.py -v
"""

import os
import sys
import tempfile
import shutil
import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path
import importlib
import importlib.util
import importlib.machinery

_SCRIPTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'scripts'))
_uaa_path = os.path.join(_SCRIPTS_DIR, 'uaa')
_loader = importlib.machinery.SourceFileLoader('uaa', _uaa_path)
_spec = importlib.util.spec_from_loader('uaa', loader=_loader)
_uaa_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_uaa_mod)

cmd_doctor = _uaa_mod.cmd_doctor
check_tool_directory = _uaa_mod.check_tool_directory
check_symlinks = _uaa_mod.check_symlinks
validate_skills_in_tool = _uaa_mod.validate_skills_in_tool
DoctorReport = _uaa_mod.DoctorReport


class TestDoctorReport(unittest.TestCase):
    """Test DoctorReport dataclass."""

    def test_empty_report(self):
        report = DoctorReport()
        self.assertEqual(len(report.issues), 0)
        self.assertEqual(len(report.fixes_applied), 0)
        self.assertEqual(report.total_tools_checked, 0)

    def test_add_issue(self):
        report = DoctorReport()
        report.add_issue("test-tool", "error", "Test issue")
        self.assertEqual(len(report.issues), 1)
        self.assertEqual(report.issues[0]["tool"], "test-tool")
        self.assertEqual(report.issues[0]["type"], "error")
        self.assertEqual(report.issues[0]["message"], "Test issue")

    def test_add_fix(self):
        report = DoctorReport()
        report.add_fix("test-tool", "Fixed something")
        self.assertEqual(len(report.fixes_applied), 1)
        self.assertEqual(report.fixes_applied[0]["tool"], "test-tool")

    def test_summary(self):
        report = DoctorReport()
        report.add_issue("tool1", "error", "Issue 1")
        report.add_issue("tool2", "warning", "Issue 2")
        report.total_tools_checked = 3
        summary = report.get_summary()
        self.assertIn("3 tools checked", summary)
        self.assertIn("1 errors", summary)
        self.assertIn("1 warnings", summary)


class TestCheckToolDirectory(unittest.TestCase):
    """Test check_tool_directory function."""

    def test_missing_directory(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tool_path = os.path.join(tmpdir, "nonexistent-tool")
            issues = []
            check_tool_directory(tool_path, "test-tool", issues)
            self.assertEqual(len(issues), 1)
            self.assertEqual(issues[0]["type"], "error")
            self.assertIn("does not exist", issues[0]["message"])

    def test_valid_directory(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tool_path = os.path.join(tmpdir, "valid-tool")
            os.makedirs(tool_path)
            issues = []
            check_tool_directory(tool_path, "test-tool", issues)
            self.assertEqual(len(issues), 0)


class TestCheckSymlinks(unittest.TestCase):
    """Test check_symlinks function."""

    def test_broken_symlink(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            target = os.path.join(tmpdir, "target")
            link = os.path.join(tmpdir, "link")
            os.makedirs(target)
            os.symlink(target, link)
            shutil.rmtree(target)
            issues = []
            broken = check_symlinks(tmpdir, "test-tool", issues)
            self.assertEqual(len(broken), 1)
            self.assertIn("broken", issues[0]["message"].lower())

    def test_valid_symlinks(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            target = os.path.join(tmpdir, "target")
            link = os.path.join(tmpdir, "link")
            os.makedirs(target)
            os.symlink(target, link)
            issues = []
            broken = check_symlinks(tmpdir, "test-tool", issues)
            self.assertEqual(len(broken), 0)

    def test_no_symlinks(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            os.makedirs(os.path.join(tmpdir, "subdir"))
            issues = []
            broken = check_symlinks(tmpdir, "test-tool", issues)
            self.assertEqual(len(broken), 0)


class TestValidateSkillsInTool(unittest.TestCase):
    """Test validate_skills_in_tool function."""

    def test_valid_skill(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = os.path.join(tmpdir, "valid-skill")
            os.makedirs(skill_dir)
            skill_file = os.path.join(skill_dir, "SKILL.md")
            with open(skill_file, "w") as f:
                f.write("---\nname: test-skill\ndescription: Test skill\n---\nContent")
            issues = []
            result = validate_skills_in_tool(tmpdir, "test-tool", issues)
            self.assertTrue(result)

    def test_missing_skill_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = os.path.join(tmpdir, "skill-no-file")
            os.makedirs(skill_dir)
            issues = []
            result = validate_skills_in_tool(tmpdir, "test-tool", issues)
            self.assertFalse(result)
            self.assertTrue(any("SKILL.md" in i["message"] for i in issues))

    def test_invalid_yaml(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = os.path.join(tmpdir, "invalid-skill")
            os.makedirs(skill_dir)
            skill_file = os.path.join(skill_dir, "SKILL.md")
            with open(skill_file, "w") as f:
                f.write("---\nname: invalid\tchar\ndescription: Test\n---\nContent")
            issues = []
            result = validate_skills_in_tool(tmpdir, "test-tool", issues)
            self.assertTrue(result)


class TestCmdDoctor(unittest.TestCase):
    """Test cmd_doctor function."""

    @patch('os.path.expanduser')
    @patch('os.path.exists')
    @patch.object(_uaa_mod, 'check_tool_directory')
    @patch.object(_uaa_mod, 'check_symlinks')
    @patch.object(_uaa_mod, 'validate_skills_in_tool')
    def test_doctor_with_issues(self, mock_validate, mock_symlinks, mock_check_dir, mock_exists, mock_expand):
        mock_expand.return_value = "/tmp/fake-home"
        mock_exists.return_value = True
        mock_check_dir.return_value = None
        mock_symlinks.return_value = []
        mock_validate.return_value = True

        args = MagicMock()
        args.fix = False
        args.verbose = True

        result = cmd_doctor(args)
        self.assertIsNotNone(result)

    @patch('os.path.expanduser')
    @patch('os.path.exists')
    def test_doctor_skips_nonexistent_home(self, mock_exists, mock_expand):
        mock_expand.return_value = "/nonexistent/path"
        mock_exists.return_value = False

        args = MagicMock()
        args.fix = False
        args.verbose = False

        with self.assertRaises(SystemExit) as cm:
            cmd_doctor(args)
        self.assertEqual(cm.exception.code, 1)


class TestDoctorFixes(unittest.TestCase):
    """Test auto-fix functionality."""

    def test_fix_broken_symlink(self):
        """Test that broken symlinks can be detected for fixing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            source = os.path.join(tmpdir, "source")
            broken_link = os.path.join(tmpdir, "broken-link")
            os.makedirs(source)
            os.symlink(source, broken_link)
            shutil.rmtree(source)

            issues = []
            broken = check_symlinks(tmpdir, "test-tool", issues)
            self.assertEqual(len(broken), 1)

    def test_report_collects_fixes(self):
        """Test that fixes are tracked in report."""
        report = DoctorReport()
        report.add_fix("tool1", "Recreated broken symlink")
        self.assertEqual(len(report.fixes_applied), 1)
        self.assertIn("Recreated", report.fixes_applied[0]["fix"])


if __name__ == "__main__":
    unittest.main()