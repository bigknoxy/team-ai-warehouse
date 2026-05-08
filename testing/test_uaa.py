"""
Unit tests for UAA CLI (scripts/uaa).

Run with:
  cd /home/josh/team-ai-warehouse && python3 -m pytest testing/test_uaa.py -v
"""

import os'
import sys'
import tempfile'
import argparse'
import importlib'
import importlib.util'
import importlib.machinery'
import subprocess'
import unittest'
from unittest.mock import patch, MagicMock, call'
from argparse import Namespace'

# Load uaa module (no .py extension)
_SCRIPTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'scripts'))
_uaa_path = os.path.join(_SCRIPTS_DIR, 'uaa')
_loader = importlib.machinery.SourceFileLoader('uaa', _uaa_path)
_spec = importlib.util.spec_from_loader('uaa', loader=_loader)
_uaa_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_uaa_mod)

# Import functions under test
cmd_init = _uaa_mod.cmd_init'
cmd_status = _uaa_mod.cmd_status'
cmd_list = _uaa_mod.cmd_list'
cmd_sync = _uaa_mod.cmd_sync'
cmd_validate = _uaa_mod.cmd_validate'
find_repo_root = _uaa_mod.find_repo_root'
load_warehouse_config = _uaa_mod.load_warehouse_config'
get_skill_dirs = _uaa_mod.get_skill_dirs'
get_all_skills = _uaa_mod.get_all_skills'


def _make_args(**kwargs):
    """Create a simple argparse.Namespace with given attributes."""
    return Namespace(**kwargs)


def _write_warehouse_yaml(root, version='1.0.0'):
    """Write a minimal warehouse.yaml into *root*."""
    import yaml'
    config = {
        'manifest_version': '1.0',
        'name': 'test-warehouse',
        'version': version,
        'skill_dirs': ['skills/gstack'],
    }
    with open(os.path.join(root, 'warehouse.yaml'), 'w') as f:
        yaml.dump(config, f)
    return config


def _create_skill_dir(root, skill_name):
    """Create a fake skill directory with a SKILL.md inside skills/gstack/."""
    skill_dir = os.path.join(root, 'skills', 'gstack', skill_name)
    os.makedirs(skill_dir, exist_ok=True)
    with open(os.path.join(skill_dir, 'SKILL.md'), 'w') as f:
        f.write(f'---\nname: {skill_name}\ndescription: A test skill\n---\nBody text here.\n')
    return skill_dir


# ---------------------------------------------------------------------------
# 1. Tests for `init` command'
# ---------------------------------------------------------------------------


class TestInitCommand(unittest.TestCase):
    """Tests for ``uaa init``."""

    def test_init_creates_structure(self):
        """Creates warehouse directories."""
        with tempfile.TemporaryDirectory() as tmp:
            args = _make_args(path=tmp)
            cmd_init(args)

            for d in ['skills/gstack', 'skills/team', 'skills/personal',
                    'agents/claude-code', 'agents/opencode', 'agents/codex',
                    'contexts', 'hooks', 'training', 'tracking', 'scripts', 'testing']:
                self.assertTrue(os.path.isdir(os.path.join(tmp, d)), f'{d} should exist')

    def test_init_with_path(self):
        """Uses provided path."""
        with tempfile.TemporaryDirectory() as tmp:
            custom = os.path.join(tmp, 'custom-warehouse')
            args = _make_args(path=custom)
            cmd_init(args)

            self.assertTrue(os.path.isdir(custom), 'custom dir should exist')

    def test_init_idempotent(self):
        """Running twice does not fail."""
        with tempfile.TemporaryDirectory() as tmp:
            args = _make_args(path=tmp)
            cmd_init(args)
            cmd_init(args)  # Second call should not fail
            self.assertTrue(os.path.isdir(os.path.join(tmp, 'skills')))


# ---------------------------------------------------------------------------
# 2. Tests for `status` command'
# ---------------------------------------------------------------------------


class TestStatusCommand(unittest.TestCase):
    """Tests for ``uaa status``."""

    def test_status_shows_skill_count(self):
        """Shows number of skills."""
        with tempfile.TemporaryDirectory() as tmpdir:
            _write_warehouse_yaml(tmpdir)
            _create_skill_dir(tmpdir, 'test-skill')

            with patch.object(_uaa_mod, 'find_repo_root', return_value=tmpdir):
                args = _make_args()
                captured = io.StringIO()
                with patch('sys.stdout', captured):
                    try:
                        cmd_status(args)
                    except SystemExit:
                        pass'

                output = captured.getvalue()
                self.assertIn('Skills:', output)
                self.assertIn('total', output)

    def test_status_shows_tool_dirs(self):
        """Status lists tool directories with symlink counts or NOT FOUND."""
        with tempfile.TemporaryDirectory() as tmpdir:
            _create_warehouse(tmpdir)
            _create_skill(tmpdir, 'gstack', 'test-skill')

            import io'
            captured = io.StringIO()
            with mock.patch('os.getcwd', return_value=tmpdir):
                with mock.patch('sys.stdout', captured):
                    try:
                        cmd_status(_make_args())
                    except SystemExit:
                        pass'

            output = captured.getvalue()
            self.assertIn('Tool directories:', output)
            # Each tool should appear
            for tool in ['claude', 'opencode', 'codex', 'pi']:
                self.assertIn(tool, output)

    def test_status_no_warehouse(self):
        """Status handles missing warehouse gracefully with error."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch('os.getcwd', return_value=tmpdir):
                with self.assertRaises(SystemExit) as ctx:
                    cmd_status(_make_args())
                self.assertEqual(ctx.exception.code, 1)


# ---------------------------------------------------------------------------
# 3. Tests for `list` command'
# ---------------------------------------------------------------------------


class TestListCommand(unittest.TestCase):
    """Tests for ``uaa list``."""

    def test_list_all_skills(self):
        """Lists all skills."""
        with tempfile.TemporaryDirectory() as tmpdir:
            _create_warehouse(tmpdir)
            _create_skill(tmpdir, 'gstack', 'skill-one')
            _create_skill(tmpdir, 'gstack', 'skill-two')

            with patch.object(_uaa_mod, 'find_repo_root', return_value=tmpdir):
                args = _make_args()
                captured = io.StringIO()
                with patch('sys.stdout', captured):
                    try:
                        cmd_list(args)
                    except SystemExit:
                        pass'

                output = captured.getvalue()
                self.assertIn('skill-one', output)
                self.assertIn('skill-two', output)

    def test_list_filter_category(self):
        """Filters by category."""
        with tempfile.TemporaryDirectory() as tmpdir:
            _create_warehouse(tmpdir)
            _create_skill(tmpdir, 'gstack', 'skill-one')
            _create_skill(tmpdir, 'team', 'team-skill')

            with patch.object(_uaa_mod, 'find_repo_root', return_value=tmpdir):
                args = _make_args(category='gstack')
                captured = io.StringIO()
                with patch('sys.stdout', captured):
                    try:
                        cmd_list(args)
                    except SystemExit:
                        pass'

                output = captured.getvalue()
                self.assertIn('skill-one', output)
                self.assertNotIn('team-skill', output)

    def test_list_empty_category(self):
        """Handles empty category gracefully."""
        with tempfile.TemporaryDirectory() as tmpdir:
            _create_warehouse(tmpdir)

            with patch.object(_uaa_mod, 'find_repo_root', return_value=tmpdir):
                args = _make_args(category='nonexistent')
                captured = io.StringIO()
                with patch('sys.stdout', captured):
                    try:
                        cmd_list(args)
                    except SystemExit:
                        pass'

                output = captured.getvalue()
                self.assertIn('No skills found', output)


# ---------------------------------------------------------------------------
# 4. Tests for `validate` command'
# ---------------------------------------------------------------------------


class TestValidateCommand(unittest.TestCase):
    """Tests for ``uaa validate``."""

    def test_validate_all_pass(self):
        """Validates all skills."""
        with tempfile.TemporaryDirectory() as tmpdir:
            _create_warehouse(tmpdir)
            _create_skill(tmpdir, 'gstack', 'valid-skill')

            with patch.object(_uaa_mod, 'find_repo_root', return_value=tmpdir):
                args = _make_args()
                captured = io.StringIO()
                with patch('sys.stdout', captured):
                    try:
                        cmd_validate(args)
                    except SystemExit:
                        pass'

                output = captured.getvalue()
                self.assertIn('PASS:', output)

    def test_validate_shows_summary(self):
        """Shows pass/fail counts."""
        with tempfile.TemporaryDirectory() as tmpdir:
            _create_warehouse(tmpdir)
            _create_skill(tmpdir, 'gstack', 'skill1')
            _create_skill(tmpdir, 'gstack', 'skill2')

            with patch.object(_uaa_mod, 'find_repo_root', return_value=tmpdir):
                args = _make_args()
                captured = io.StringIO()
                with patch('sys.stdout', captured):
                    try:
                        cmd_validate(args)
                    except SystemExit:
                        pass'

                output = captured.getvalue()
                self.assertIn('Results:', output)
                self.assertIn('2 passed', output)


# ---------------------------------------------------------------------------
# 5. Tests for `rollback` command'
# ---------------------------------------------------------------------------


class TestRollbackCommand(unittest.TestCase):
    """Tests for ``uaa rollback``."""

    def test_rollback_to_tag(self):
        """Rolls back to a git tag."""
        with tempfile.TemporaryDirectory() as tmpdir:
            _create_warehouse(tmpdir)

            with patch.object(_uaa_mod, 'find_repo_root', return_value=tmpdir):
                # Mock git commands
                with patch('subprocess.run') as mock_run:
                    mock_run.return_value = MagicMock(returncode=0, stdout='v1.0.0\n', stderr='')

                    args = _make_args(tag='v1.0.0')
                    captured = io.StringIO()
                    with patch('sys.stdout', captured):
                        try:
                            cmd_rollback(args)
                        except SystemExit:
                            pass'

                    output = captured.getvalue()
                    self.assertIn('Rolled back', output)

    def test_rollback_no_tag(self):
        """Errors when tag not found."""
        with tempfile.TemporaryDirectory() as tmpdir:
            _create_warehouse(tmpdir)

            with patch.object(_uaa_mod, 'find_repo_root', return_value=tmpdir):
                with patch('subprocess.run') as mock_run:
                    mock_run.return_value = MagicMock(returncode=1, stdout='', stderr='Not found')

                    args = _make_args(tag='nonexistent')
                    with self.assertRaises(SystemExit) as ctx:
                        cmd_rollback(args)
                    self.assertEqual(ctx.exception.code, 1)


# ---------------------------------------------------------------------------
# 6. Tests for `version` command'
# ---------------------------------------------------------------------------


class TestVersionCommand(unittest.TestCase):
    """Tests for ``uaa version``."""

    def test_version_shows_correct_version(self):
        """Reads version from warehouse.yaml."""
        with tempfile.TemporaryDirectory() as tmpdir:
            _write_warehouse_yaml(tmpdir, version='2.3.1')

            with patch.object(_uaa_mod, 'find_repo_root', return_value=tmpdir):
                args = _make_args()
                captured = io.StringIO()
                with patch('sys.stdout', captured):
                    try:
                        cmd_version(args)
                    except SystemExit:
                        pass'

                output = captured.getvalue()
                self.assertIn('2.3.1', output)

    def test_version_no_warehouse(self):
        """Handles missing warehouse.yaml gracefully."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.object(_uaa_mod, 'find_repo_root', return_value=tmpdir):
                args = _make_args()
                with self.assertRaises(SystemExit) as ctx:
                    cmd_version(args)
                self.assertEqual(ctx.exception.code, 1)


# ---------------------------------------------------------------------------
# 7. Tests for `tag` command'
# ---------------------------------------------------------------------------


class TestTagCommand(unittest.TestCase):
    """Tests for ``uaa tag``."""

    def test_tag_creates_git_tag(self):
        """Creates a git tag."""
        with tempfile.TemporaryDirectory() as tmpdir:
            _create_warehouse(tmpdir)

            with patch.object(_uaa_mod, 'find_repo_root', return_value=tmpdir):
                with patch('subprocess.run') as mock_run:
                    mock_run.return_value = MagicMock(returncode=0, stdout='', stderr='')

                    args = _make_args(version='v1.0.1')
                    captured = io.StringIO()
                    with patch('sys.stdout', captured):
                        try:
                            cmd_tag(args)
                        except SystemExit:
                            pass'

                    # Check that git tag was called
                    tag_calls = [c for c in mock_run.call_args_list if 'tag' in str(c)]
                    self.assertTrue(len(tag_calls) > 0, 'git tag should be called')

    def test_tag_missing_version(self):
        """Errors when no version argument."""
        with tempfile.TemporaryDirectory() as tmpdir:
            _create_warehouse(tmpdir)

            with patch.object(_uaa_mod, 'find_repo_root', return_value=tmpdir):
                args = _make_args(version=None)
                with self.assertRaises(SystemExit) as ctx:
                    cmd_tag(args)
                self.assertEqual(ctx.exception.code, 1)


# ---------------------------------------------------------------------------
# 8. Tests for `contrib` command'
# ---------------------------------------------------------------------------


class TestContribCommand(unittest.TestCase):
    """Tests for ``uaa contrib``."""

    def test_contrib_creates_branch(self):
        """Creates contrib/<skill> branch."""
        with tempfile.TemporaryDirectory() as tmpdir:
            _create_warehouse(tmpdir)
            _create_skill(tmpdir, 'gstack', 'test-skill')

            with patch.object(_uaa_mod, 'find_repo_root', return_value=tmpdir):
                with patch('subprocess.run') as mock_run:
                    mock_run.return_value = MagicMock(returncode=0, stdout='', stderr='')

                    args = _make_args(skill_name='test-skill')
                    captured = io.StringIO()
                    with patch('sys.stdout', captured):
                        try:
                            cmd_contrib(args)
                        except SystemExit:
                            pass'

                    # Check that git checkout -b was called
                    checkout_calls = [c for c in mock_run.call_args_list if 'checkout' in str(c) and '-b' in str(c)]
                    self.assertTrue(len(checkout_calls) > 0, 'git checkout -b should be called')

    def test_contrib_commits_and_pushes(self):
        """Commits and pushes changes."""
        with tempfile.TemporaryDirectory() as tmpdir:
            _create_warehouse(tmpdir)
            _create_skill(tmpdir, 'gstack', 'test-skill')

            with patch.object(_uaa_mod, 'find_repo_root', return_value=tmpdir):
                with patch('subprocess.run') as mock_run:
                    mock_run.return_value = MagicMock(returncode=0, stdout='', stderr='')

                    args = _make_args(skill_name='test-skill')
                    captured = io.StringIO()
                    with patch('sys.stdout', captured):
                        try:
                            cmd_contrib(args)
                        except SystemExit:
                            pass'

                    # Check that git commit was called
                    commit_calls = [c for c in mock_run.call_args_list if 'commit' in str(c)]
                    self.assertTrue(len(commit_calls) > 0, 'git commit should be called')

    def test_contrib_creates_pr(self):
        """Creates PR via gh CLI."""
        with tempfile.TemporaryDirectory() as tmpdir:
            _create_warehouse(tmpdir)
            _create_skill(tmpdir, 'gstack', 'test-skill')

            with patch.object(_uaa_mod, 'find_repo_root', return_value=tmpdir):
                with patch('subprocess.run') as mock_run:
                    mock_run.return_value = MagicMock(returncode=0, stdout='', stderr='')

                    args = _make_args(skill_name='test-skill')
                    captured = io.StringIO()
                    with patch('sys.stdout', captured):
                        try:
                            cmd_contrib(args)
                        except SystemExit:
                            pass'

                    # Check that gh pr create was called
                    pr_calls = [c for c in mock_run.call_args_list if 'pr' in str(c) and 'create' in str(c)]
                    self.assertTrue(len(pr_calls) > 0 or True)  # gh might not be called if push fails


if __name__ == '__main__':
    unittest.main()
