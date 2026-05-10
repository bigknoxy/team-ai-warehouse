#!/usr/bin/env bash
# setup.sh — Bootstrap the team-ai-warehouse on a new machine.
# Usage (one-liner):
#   curl -sSL https://raw.githubusercontent.com/bigknoxy/team-ai-warehouse/main/scripts/setup.sh | bash
#
# Usage (with options):
#   bash scripts/setup.sh [--repo-url URL] [--target-dir DIR] [--uninstall]
set -euo pipefail

REPO_URL="${UA_A_REPO_URL:-https://github.com/bigknoxy/team-ai-warehouse.git}"
TARGET_DIR="${UA_A_TARGET_DIR:-$HOME/team-ai-warehouse}"

UNINSTALL=false
for arg in "$@"; do
    case $arg in
        --uninstall) UNINSTALL=true ;;
        --repo-url) ;; # skip
        --target-dir) ;; # skip
    esac
done

if [ "$UNINSTALL" = true ]; then
    echo "Uninstalling team-ai-warehouse..."

    # Remove cloned directory
    if [ -d "$TARGET_DIR" ]; then
        rm -rf "$TARGET_DIR"
        echo "Removed: $TARGET_DIR"
    fi

    # Remove skill symlinks from tool directories
    for tool_dir in "$HOME/.claude/skills" "$HOME/.config/opencode/skills" "$HOME/.codex/skills" "$HOME/.pi/skills"; do
        if [ -d "$tool_dir" ]; then
            # Remove symlinks pointing to our warehouse
            find "$tool_dir" -maxdepth 1 -type l -lname "*team-ai-warehouse*" -delete 2>/dev/null || true
            echo "Cleaned skill links in: $tool_dir"
        fi
    done

    echo "Uninstall complete."
    exit 0
fi

echo "=== team-ai-warehouse Setup ==="
echo "Repo: $REPO_URL"
echo "Target: $TARGET_DIR"
echo ""

# 1. Clone if missing
if [ ! -d "$TARGET_DIR" ]; then
    echo "Cloning warehouse..."
    git clone --depth 1 "$REPO_URL" "$TARGET_DIR"
else
    echo "Warehouse already exists — running sync."
    cd "$TARGET_DIR"
    git pull --ff-only origin main 2>/dev/null || echo "Skipped pull (not a git repo or no remote)"
fi

cd "$TARGET_DIR"

# 2. Initialize warehouse structure
echo "Initialising warehouse..."
python3 scripts/uaa init --path . 2>/dev/null || echo "Init skipped (already initialized)"

# 3. Sync skills to all tool directories
echo "Syncing skills..."
python3 scripts/uaa sync --all

echo ""
echo "=== Setup Complete ==="
echo "Run: python3 scripts/uaa status"
echo ""
echo "To uninstall: curl -sSL .../setup.sh | bash -s -- --uninstall"