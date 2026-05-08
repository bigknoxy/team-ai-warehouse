#!/usr/bin/env python3
"""
Unit tests for UAA CLI (scripts/uaa).

Run with:
  cd /home/josh/team-ai-warehouse && python3 -m pytest testing/test_uaa.py -v
"""

import os
import sys
import tempfile
import argparse
import importlib.util
import importlib.machinery
import subprocess
import unittest
from unittest import mock

# Load uaa module from scripts/ (no .py extension)
_SCRIPTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'scripts'))
_uaa_path = os.path.join(_SCRIPTS_DIR, "uaa")
_loader = importlib.machinery.SourceFileLoader("uaa", _uaa_path)
_spec = importlib.util.spec_from_loader("uaa", loader=_loader)
_uaa_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_uaa_mod)

# Import functions under test
cmd_init = _uaa_mod.cmd_init
cmd_status = _uaa_mod.cmd_status
cmd_list = _uaa_mod.cmd_list
cmd_sync = _uaa_mod.cmd_sync
cmd_validate = _uaa_mod.cmd_validate
find_repo_root = _uaa_mod.find_repo_root
load_warehouse_config = _uaa_mod.load_warehouse_config
get_skill_dirs = _uaa_mod.get_skill_dirs
get_all_skills = _uaa_mod.get_all_skills


def _make_args(**kwargs):
    """Create a simple argparse.Namespace with given attributes."""
    return argparse.Namespace(**kwargs)


def _write_skill_md(directory, name="test-skill", description="A test skill"):
    """Helper: write a minimal SKILL.md into *directory*."""
    content = f"---\nname: {name!r}\ndescription: {description!r}\n---\nBody text here.\n"
    path = os.path.join(directory, "SKILL.md")
    with open(path, "w") as f:
        f.write(content)
    return path


def _create_warehouse(root, skill_dirs=None):
    """Create a minimal warehouse.yaml at *root* with optional skill_dirs."""
    import yaml
    config = {
        'manifest_version': '1.0',
        'name': 'test-warehouse',
        'description': 'Test warehouse',
        'version': '1.0.0',
        'skill_dirs': skill_dirs or ['skills/gstack', 'skills/team', 'skills/personal'],
    }
    config_path = os.path.join(root, 'warehouse.yaml')
    with open(config_path, 'w') as f:
        yaml.dump(config, f)
    return config_path


def _create_skill(root, category, name, description="A test skill"):
    """Create a skill directory with SKILL.md under root/skills/<category>/<name>."""
    skill_dir = os.path.join(root, 'skills', category, name)
    os.makedirs(skill_dir, exist_ok=True)
    _write_skill_md(skill_dir, name=name, description=description)
    return skill_dir


# ──────────────────────────────────────────────
# 1. Tests for `init` command
# ──────────────────────────────────────────────

class TestInitCommand(unittest.TestCase):
    """Tests for cmd_init: creates warehouse directory structure."""

    def test_init_creates_structure(self):
        """Init creates all required directories and warehouse.yaml."""
        with tempfile.TemporaryDirectory() as tmpdir:
            args = _make_args(path=tmpdir)
            cmd_init(args)

            # Verify all required dirs exist
            expected_dirs = [
                'skills/gstack', 'skills/team', 'skills/personal',
                'agents/claude-code', 'agents/opencode', 'agents/codex',
                'contexts', 'hooks', 'training', 'tracking', 'scripts', 'testing',
            ]
            for d in expected_dirs:
                full = os.path.join(tmpdir, d)
                self.assertTrue(os.path.isdir(full), f"Missing directory: {d}")

            # Verify warehouse.yaml was created
            config_path = os.path.join(tmpdir, 'warehouse.yaml')
            self.assertTrue(os.path.isfile(config_path))

            # Verify config content
            import yaml
            with open(config_path) as f:
                config = yaml.safe_load(f)
            self.assertEqual(config['name'], 'team-ai-warehouse')
            self.assertIn('skills/gstack', config['skill_dirs'])

    def test_init_with_path(self):
        """Init creates structure at a custom path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            custom = os.path.join(tmpdir, 'custom-warehouse')
            args = _make_args(path=custom)
            cmd_init(args)

            self.assertTrue(os.path.isdir(os.path.join(custom, 'skills/gstack')))
            self.assertTrue(os.path.isfile(os.path.join(custom, 'warehouse.yaml')))

    def test_init_idempotent(self):
        """Running init twice doesn't fail or overwrite warehouse.yaml."""
        with tempfile.TemporaryDirectory() as tmpdir:
            args = _make_args(path=tmpdir)

            # First init
            cmd_init(args)
            config_path = os.path.join(tmpdir, 'warehouse.yaml')
            mtime_first = os.path.getmtime(config_path)

            # Second init
            cmd_init(args)
            mtime_second = os.path.getmtime(config_path)

            # warehouse.yaml should NOT have been overwritten
            self.assertEqual(mtime_first, mtime_second)

            # All dirs should still exist
            self.assertTrue(os.path.isdir(os.path.join(tmpdir, 'skills/gstack')))
            self.assertTrue(os.path.isdir(os.path.join(tmpdir, 'testing')))


# ──────────────────────────────────────────────
# 2. Tests for `status` command
# ──────────────────────────────────────────────

class TestStatusCommand(unittest.TestCase):
    """Tests for cmd_status: shows warehouse status."""

    def test_status_shows_skill_count(self):
        """Status correctly counts and lists skills."""
        with tempfile.TemporaryDirectory() as tmpdir:
            _create_warehouse(tmpdir)
            _create_skill(tmpdir, 'gstack', 'skill-one')
            _create_skill(tmpdir, 'team', 'skill-two')

            import io
            captured = io.StringIO()
            with mock.patch('os.getcwd', return_value=tmpdir):
                with mock.patch('sys.stdout', captured):
                    cmd_status(_make_args())

            output = captured.getvalue()
            self.assertIn('Skills: 2 total', output)
            self.assertIn('skill-one', output)
            self.assertIn('skill-two', output)

    def test_status_shows_tool_dirs(self):
        """Status lists tool directories with symlink counts or NOT FOUND."""
        with tempfile.TemporaryDirectory() as tmpdir:
            _create_warehouse(tmpdir)
            _create_skill(tmpdir, 'gstack', 'test-skill')

            import io
            captured = io.StringIO()
            with mock.patch('os.getcwd', return_value=tmpdir):
                with mock.patch('sys.stdout', captured):
                    try:
                        cmd_status(_make_args())
                    except SystemExit:
                        pass

            output = captured.getvalue()
            self.assertIn('Tool directories:', output)
            # Each tool should appear
            for tool in ['claude', 'opencode', 'codex', 'pi']:
                self.assertIn(tool, output)

    def test_status_no_warehouse(self):
        """Status handles missing warehouse gracefully with error."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with mock.patch('os.getcwd', return_value=tmpdir):
                with self.assertRaises(SystemExit) as ctx:
                    cmd_status(_make_args())
            self.assertEqual(ctx.exception.code, 1)


# ──────────────────────────────────────────────
# 3. Tests for `list` command
# ──────────────────────────────────────────────

class TestListCommand(unittest.TestCase):
    """Tests for cmd_list: lists skills with optional category filter."""

    def test_list_all_skills(self):
        """List shows all skills across categories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            _create_warehouse(tmpdir)
            _create_skill(tmpdir, 'gstack', 'browse')
            _create_skill(tmpdir, 'team', 'deploy')
            _create_skill(tmpdir, 'personal', 'notes')

            import io
            captured = io.StringIO()
            with mock.patch('os.getcwd', return_value=tmpdir):
                with mock.patch('sys.stdout', captured):
                    cmd_list(_make_args(category=None))

            output = captured.getvalue()
            self.assertIn('Skills (3):', output)
            self.assertIn('browse', output)
            self.assertIn('deploy', output)
            self.assertIn('notes', output)

    def test_list_filter_category(self):
        """List filters skills by category (gstack, team, personal)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            _create_warehouse(tmpdir)
            _create_skill(tmpdir, 'gstack', 'browse')
            _create_skill(tmpdir, 'gstack', 'qa')
            _create_skill(tmpdir, 'team', 'deploy')
            _create_skill(tmpdir, 'personal', 'notes')

            import io
            captured = io.StringIO()
            with mock.patch('os.getcwd', return_value=tmpdir):
                with mock.patch('sys.stdout', captured):
                    cmd_list(_make_args(category='gstack'))

            output = captured.getvalue()
            self.assertIn('Skills (2):', output)
            self.assertIn('browse', output)
            self.assertIn('qa', output)
            self.assertNotIn('deploy', output)
            self.assertNotIn('notes', output)

    def test_list_empty_category(self):
        """List handles empty category gracefully."""
        with tempfile.TemporaryDirectory() as tmpdir:
            _create_warehouse(tmpdir)
            # No skills created

            import io
            captured = io.StringIO()
            with mock.patch('os.getcwd', return_value=tmpdir):
                with mock.patch('sys.stdout', captured):
                    cmd_list(_make_args(category='gstack'))

            output = captured.getvalue()
            self.assertIn('No skills found', output)


# ──────────────────────────────────────────────
# 4. Tests for `sync` command
# ──────────────────────────────────────────────

class TestSyncCommand(unittest.TestCase):
    """Tests for cmd_sync: creates symlinks to tool directories."""

    def test_sync_creates_symlinks(self):
        """Sync creates symlinks from warehouse skills to tool dirs."""
        with tempfile.TemporaryDirectory() as tmpdir:
            _create_warehouse(tmpdir)
            _create_skill(tmpdir, 'gstack', 'browse')

            # Mock tool config to use temp dirs instead of ~/.claude etc.
            fake_tool_dir = os.path.join(tmpdir, 'fake-claude', 'skills')

            with mock.patch('os.getcwd', return_value=tmpdir):
                with mock.patch.object(_uaa_mod, 'TOOL_CONFIGS', {
                    'claude': {'dir': os.path.join(tmpdir, 'fake-claude'), 'skills': 'skills'}
                }):
                    with mock.patch('sys.stdout', new_callable=lambda: __import__('io').StringIO()):
                        cmd_sync(_make_args(tools='claude', all=False))

            # Verify symlink was created
            link_path = os.path.join(fake_tool_dir, 'browse')
            self.assertTrue(os.path.islink(link_path), f"Expected symlink at {link_path}")
            target = os.readlink(link_path)
            self.assertIn('browse', target)

    def test_sync_idempotent(self):
        """Running sync twice doesn't fail."""
        with tempfile.TemporaryDirectory() as tmpdir:
            _create_warehouse(tmpdir)
            _create_skill(tmpdir, 'gstack', 'qa')

            fake_tool_dir = os.path.join(tmpdir, 'fake-claude', 'skills')

            with mock.patch('os.getcwd', return_value=tmpdir):
                with mock.patch.object(_uaa_mod, 'TOOL_CONFIGS', {
                    'claude': {'dir': os.path.join(tmpdir, 'fake-claude'), 'skills': 'skills'}
                }):
                    with mock.patch('sys.stdout', new_callable=lambda: __import__('io').StringIO()):
                        cmd_sync(_make_args(tools='claude', all=False))
                        cmd_sync(_make_args(tools='claude', all=False))

            # Symlink should still exist and be valid
            link_path = os.path.join(fake_tool_dir, 'qa')
            self.assertTrue(os.path.islink(link_path))

    def test_sync_no_tool_dirs(self):
        """Sync creates tool directories if they don't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            _create_warehouse(tmpdir)
            _create_skill(tmpdir, 'team', 'deploy')

            fake_tool_dir = os.path.join(tmpdir, 'new-tool', 'skills')
            self.assertFalse(os.path.isdir(fake_tool_dir))

            with mock.patch('os.getcwd', return_value=tmpdir):
                with mock.patch.object(_uaa_mod, 'TOOL_CONFIGS', {
                    'codex': {'dir': os.path.join(tmpdir, 'new-tool'), 'skills': 'skills'}
                }):
                    with mock.patch('sys.stdout', new_callable=lambda: __import__('io').StringIO()):
                        cmd_sync(_make_args(tools='codex', all=False))

            self.assertTrue(os.path.isdir(fake_tool_dir))
            link_path = os.path.join(fake_tool_dir, 'deploy')
            self.assertTrue(os.path.islink(link_path))


# ──────────────────────────────────────────────
# 5. Tests for `validate` command
# ──────────────────────────────────────────────

class TestValidateCommand(unittest.TestCase):
    """Tests for cmd_validate: validates skills against SKILL.md spec."""

    def test_validate_all_pass(self):
        """All valid skills pass validation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            _create_warehouse(tmpdir)
            _create_skill(tmpdir, 'gstack', 'browse', description='Browse the web')
            _create_skill(tmpdir, 'team', 'deploy', description='Deploy to production')

            # Create a mock validator that always passes
            validator_path = os.path.join(tmpdir, 'scripts', 'validate-skill.py')
            os.makedirs(os.path.dirname(validator_path), exist_ok=True)
            with open(validator_path, 'w') as f:
                f.write("#!/usr/bin/env python3\nimport sys; sys.exit(0)\n")

            import io
            captured = io.StringIO()
            with mock.patch('os.getcwd', return_value=tmpdir):
                with mock.patch('sys.stdout', captured):
                    try:
                        cmd_validate(_make_args(all=False))
                    except SystemExit as e:
                        # Should exit 0 when all pass
                        self.assertEqual(e.code, 0)

            output = captured.getvalue()
            self.assertIn('PASS: browse', output)
            self.assertIn('PASS: deploy', output)
            self.assertIn('2 passed', output)
            self.assertIn('0 failed', output)

    def test_validate_shows_summary(self):
        """Validate shows pass/fail summary counts."""
        with tempfile.TemporaryDirectory() as tmpdir:
            _create_warehouse(tmpdir)
            _create_skill(tmpdir, 'gstack', 'good-skill', description='A good skill')
            _create_skill(tmpdir, 'team', 'bad-skill', description='A bad skill')

            # Create a mock validator: passes for good-skill, fails for bad-skill
            validator_path = os.path.join(tmpdir, 'scripts', 'validate-skill.py')
            os.makedirs(os.path.dirname(validator_path), exist_ok=True)
            with open(validator_path, 'w') as f:
                f.write(
                    "#!/usr/bin/env python3\n"
                    "import sys, os\n"
                    "name = os.path.basename(sys.argv[1])\n"
                    "if 'bad' in name:\n"
                    "    print('ERROR: missing required field')\n"
                    "    sys.exit(1)\n"
                    "sys.exit(0)\n"
                )

            import io
            captured = io.StringIO()
            with mock.patch('os.getcwd', return_value=tmpdir):
                with mock.patch('sys.stdout', captured):
                    try:
                        cmd_validate(_make_args(all=False))
                    except SystemExit as e:
                        # Should exit 1 when any fail
                        self.assertEqual(e.code, 1)

            output = captured.getvalue()
            self.assertIn('PASS: good-skill', output)
            self.assertIn('FAIL: bad-skill', output)
            self.assertIn('1 passed', output)
            self.assertIn('1 failed', output)


# ──────────────────────────────────────────────
# 6. Tests for helper functions
# ──────────────────────────────────────────────

class TestHelperFunctions(unittest.TestCase):
    """Tests for find_repo_root, load_warehouse_config, get_skill_dirs, get_all_skills."""

    def test_find_repo_root_finds_warehouse(self):
        """find_repo_root locates warehouse.yaml walking up from cwd."""
        with tempfile.TemporaryDirectory() as tmpdir:
            _create_warehouse(tmpdir)
            nested = os.path.join(tmpdir, 'a', 'b', 'c')
            os.makedirs(nested)

            with mock.patch('os.getcwd', return_value=nested):
                result = find_repo_root()
            self.assertEqual(result, tmpdir)

    def test_find_repo_root_returns_none(self):
        """find_repo_root returns None when no warehouse.yaml exists."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with mock.patch('os.getcwd', return_value=tmpdir):
                result = find_repo_root()
            self.assertIsNone(result)

    def test_load_warehouse_config_returns_dict(self):
        """load_warehouse_config returns parsed YAML dict."""
        with tempfile.TemporaryDirectory() as tmpdir:
            _create_warehouse(tmpdir)
            config = load_warehouse_config(tmpdir)
            self.assertIsNotNone(config)
            self.assertEqual(config['name'], 'test-warehouse')
            self.assertIn('skills/gstack', config['skill_dirs'])

    def test_load_warehouse_config_returns_none(self):
        """load_warehouse_config returns None when file missing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = load_warehouse_config(tmpdir)
            self.assertIsNone(config)

    def test_get_skill_dirs_returns_existing(self):
        """get_skill_dirs returns only directories that exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            _create_warehouse(tmpdir)
            # Only create gstack dir, not team or personal
            os.makedirs(os.path.join(tmpdir, 'skills/gstack'))

            config = load_warehouse_config(tmpdir)
            dirs = get_skill_dirs(tmpdir, config)
            self.assertEqual(len(dirs), 1)
            self.assertIn('skills/gstack', dirs[0])

    def test_get_all_skills_finds_skills(self):
        """get_all_skills returns sorted list of skill directories with SKILL.md."""
        with tempfile.TemporaryDirectory() as tmpdir:
            _create_warehouse(tmpdir)
            _create_skill(tmpdir, 'gstack', 'browse')
            _create_skill(tmpdir, 'gstack', 'qa')
            _create_skill(tmpdir, 'team', 'deploy')

            config = load_warehouse_config(tmpdir)
            skills = get_all_skills(tmpdir, config)
            self.assertEqual(len(skills), 3)
            # Full paths are sorted (by directory then name)
            self.assertEqual(skills, sorted(skills))
            names = [os.path.basename(s) for s in skills]
            self.assertIn('browse', names)
            self.assertIn('deploy', names)
            self.assertIn('qa', names)

    def test_get_all_skills_ignores_dirs_without_skill_md(self):
        """get_all_skills skips directories that lack SKILL.md."""
        with tempfile.TemporaryDirectory() as tmpdir:
            _create_warehouse(tmpdir)
            _create_skill(tmpdir, 'gstack', 'valid-skill')
            # Create a dir without SKILL.md
            empty_dir = os.path.join(tmpdir, 'skills/gstack', 'no-skill-md')
            os.makedirs(empty_dir)

            config = load_warehouse_config(tmpdir)
            skills = get_all_skills(tmpdir, config)
            self.assertEqual(len(skills), 1)
            self.assertIn('valid-skill', os.path.basename(skills[0]))


if __name__ == '__main__':
    unittest.main()
