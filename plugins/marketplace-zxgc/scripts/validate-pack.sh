#!/usr/bin/env bash
set -euo pipefail

PLUGIN_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MARKETPLACE_ROOT="$(cd "$PLUGIN_ROOT/../.." && pwd)"

echo "Validating marketplace-zxgc at $MARKETPLACE_ROOT"

if [ -f "$MARKETPLACE_ROOT/.agents/plugins/marketplace.json" ]; then
  jq empty "$MARKETPLACE_ROOT/.agents/plugins/marketplace.json"
else
  echo "Marketplace manifest not found at $MARKETPLACE_ROOT/.agents/plugins/marketplace.json; validating plugin root only"
fi
jq empty "$PLUGIN_ROOT/.codex-plugin/plugin.json"
jq empty "$PLUGIN_ROOT/.mcp.json"
jq empty "$PLUGIN_ROOT/.app.json"
jq empty "$PLUGIN_ROOT/hooks.json"

test -d "$PLUGIN_ROOT/skills"
test -d "$PLUGIN_ROOT/scripts"
test -d "$PLUGIN_ROOT/templates"
test -f "$PLUGIN_ROOT/templates/AGENTS.global.md"
test -f "$PLUGIN_ROOT/templates/rules/default.rules"

bash -n "$PLUGIN_ROOT/scripts/install-agents-md.sh"
bash -n "$PLUGIN_ROOT/scripts/install-hooks.sh"
bash -n "$PLUGIN_ROOT/scripts/install-rules.sh"
bash -n "$PLUGIN_ROOT/scripts/sync-skills.sh"
if [ -f "$MARKETPLACE_ROOT/scripts/install-marketplace-zxgc.sh" ]; then
  bash -n "$MARKETPLACE_ROOT/scripts/install-marketplace-zxgc.sh"
fi

if command -v python3 >/dev/null 2>&1 && [ -f "$HOME/.codex/skills/.system/skill-creator/scripts/quick_validate.py" ]; then
  python3 "$HOME/.codex/skills/.system/skill-creator/scripts/quick_validate.py" "$PLUGIN_ROOT/skills/marketplace-zxgc"
fi

if command -v rg >/dev/null 2>&1; then
  if rg -n "sk-[A-Za-z0-9_-]{20,}|AKIA[0-9A-Z]{16}|AIza[0-9A-Za-z_-]{20,}|xox[baprs]-[0-9A-Za-z-]+" "$PLUGIN_ROOT"; then
    echo "Potential secret-like value found; inspect before publishing." >&2
    exit 1
  fi
fi

echo "marketplace-zxgc validation passed"
