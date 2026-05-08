#!/usr/bin/env python3
"""
setup.py — Bootstrap the team-ai-warehouse on a new machine.

Usage:
    python3 scripts/setup.py [--repo-url URL] [--target-dir DIR]
"""

import os
import sys
import argparse
import subprocess


DEFAULT_REPO_URL = "https://github.com/team/team-ai-warehouse.git"
DEFAULT_TARGET_DIR = "team-ai-warehouse"


def clone_repo(repo_url, target_dir):
    """Clone the warehouse repo if the target directory doesn't exist."""
    if os.path.isdir(target_dir):
        print(f"Warehouse directory '{target_dir}' already exists — skipping clone.")
        return False

    print(f"Cloning warehouse from {repo_url} ...")
    subprocess.run(["git", "clone", repo_url, target_dir], check=True)
    return True


def init_warehouse(target_dir):
    """Run uaa init in the target directory."""
    uaa_script = os.path.join(target_dir, "scripts", "uaa")
    print("Initialising warehouse...")
    subprocess.run(
        [sys.executable, uaa_script, "init", "--path", target_dir],
        check=True,
    )


def sync_skills(target_dir):
    """Run uaa sync --all in the target directory."""
    uaa_script = os.path.join(target_dir, "scripts", "uaa")
    print("Syncing skills...")
    subprocess.run(
        [sys.executable, uaa_script, "sync", "--all"],
        cwd=target_dir,
        check=True,
    )


def main():
    parser = argparse.ArgumentParser(description="Bootstrap team-ai-warehouse")
    parser.add_argument(
        "--repo-url",
        default=os.environ.get("UAA_REPO_URL", DEFAULT_REPO_URL),
        help="Repository URL to clone",
    )
    parser.add_argument(
        "--target-dir",
        default=os.environ.get("UAA_TARGET_DIR", DEFAULT_TARGET_DIR),
        help="Target directory for the warehouse",
    )
    args = parser.parse_args()

    clone_repo(args.repo_url, args.target_dir)
    init_warehouse(args.target_dir)
    sync_skills(args.target_dir)

    print("")
    print("Setup complete! Run 'python3 scripts/uaa status' to verify.")


if __name__ == "__main__":
    main()
