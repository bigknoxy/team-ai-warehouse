#!/bin/bash
# One-command team setup
# Usage: curl -sSL https://raw.githubusercontent.com/team/warehouse/main/scripts/setup.sh | bash
# OR: bash scripts/setup.sh [warehouse-path] [--tools claude,opencode,codex,pi]

set -e
WAREHOUSE_PATH=${1:-$HOME/team-ai-warehouse}
TOOLS=${2:---tools claude,opencode,codex,pi}

echo "=== UAASP Team Setup ==="
echo "Warehouse: $WAREHOUSE_PATH"

# Clone if missing
if [ ! -d "$WAREHOUSE_PATH" ]; then
    echo "Cloning warehouse..."
    git clone <warehouse-url> "$WAREHOUSE_PATH"
else
    echo "Warehouse already exists, skipping clone."
fi

cd "$WAREHOUSE_PATH"

# Run uaa init if needed
python3 scripts/uaa init

# Sync to all tools
python3 scripts/uaa sync $TOOLS

# Verify
python3 scripts/uaa status

echo "✅ Setup complete! Start your AI agent and try /list-skills"
