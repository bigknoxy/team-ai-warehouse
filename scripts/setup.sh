#!/usr/bin/env bash
# setup.sh — Bootstrap the team-ai-warehouse on a new machine.
# Usage: bash scripts/setup.sh [--repo-url URL] [--target-dir DIR]
set -euo pipefail

REPO_URL="${UA_A_REPO_URL:-https://github.com/team/team-ai-warehouse.git}"
TARGET_DIR="${UA_A_TARGET_DIR:-team-ai-warehouse}"

# 1. Clone if missing
if [ ! -d "$TARGET_DIR" ]; then
    echo "Cloning warehouse from $REPO_URL ..."
    git clone "$REPO_URL" "$TARGET_DIR"
else
    echo "Warehouse directory '$TARGET_DIR' already exists — skipping clone."
fi

cd "$TARGET_DIR"

# 2. Initialise warehouse structure (creates warehouse.yaml, dirs, etc.)
echo "Initialising warehouse..."
python3 scripts/uaa init --path .

# 3. Sync skills to all tool directories
echo "Syncing skills..."
python3 scripts/uaa sync --all

echo ""
echo "Setup complete! Run 'python3 scripts/uaa status' to verify."
