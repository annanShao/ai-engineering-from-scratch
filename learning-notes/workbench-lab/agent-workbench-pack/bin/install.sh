#!/usr/bin/env bash
# install.sh — drop the agent workbench pack into a target repo.
# Framework-agnostic. Refuses to overwrite an existing pack without --force.
set -euo pipefail

TARGET="${1:-.}"
FORCE="${2:-}"
PACK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
DEST="$TARGET/.agent-workbench"

if [ -d "$DEST" ] && [ "$FORCE" != "--force" ]; then
  echo "refusing: $DEST already exists (pass --force to overwrite)"
  exit 1
fi

mkdir -p "$DEST"
cp -r "$PACK_DIR/docs" "$PACK_DIR/schemas" "$PACK_DIR/scripts" "$PACK_DIR/VERSION" "$DEST/"

# Wire CI if the target has GitHub Actions
if [ -d "$TARGET/.github/workflows" ]; then
  echo "  (found .github/workflows — add a job that runs scripts/verify_agent.py)"
fi

echo "installed agent-workbench v$(cat "$PACK_DIR/VERSION") into $DEST"
echo "next steps:"
echo "  1. fill in task_board.json with the current backlog"
echo "  2. set acceptance commands in scope_contract.json"
echo "  3. run: python3 $DEST/scripts/init_agent.py"
