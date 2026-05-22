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
if [ -f "$MARKETPLACE_ROOT/scripts/auto-submit-marketplace-change.sh" ]; then
  bash -n "$MARKETPLACE_ROOT/scripts/auto-submit-marketplace-change.sh"
fi

if command -v rg >/dev/null 2>&1 && [ -f "$MARKETPLACE_ROOT/操作指导.md" ]; then
  if rg -n '【人工】验证未合并 MR 分支|把 `?master`? 换成对应分支名|【人工】正式提交|手动兜底创建或更新 GitLab MR|【人工】如果环境不能执行 Codex smoke test|【人工】如果目标机器是全新 Codex 环境' "$MARKETPLACE_ROOT/操作指导.md"; then
    echo "操作指导.md contains obsolete manual markers for automatable marketplace steps." >&2
    exit 1
  fi
  if rg -n '【人工】.*(MR|GitLab|源分支|source branch|删除.*分支)' "$MARKETPLACE_ROOT/操作指导.md" | rg -v 'GitLab 网页端|网页端不可用|不要删除仍有未合并提交的分支'; then
    echo "操作指导.md contains GitLab/manual branch wording without explicit GitLab web UI context." >&2
    exit 1
  fi
fi

if command -v rg >/dev/null 2>&1 && [ -f "$PLUGIN_ROOT/skills/code-refactor/scripts/gitlab_auto_mr.py" ]; then
  rg -q 'Change Summary' "$PLUGIN_ROOT/skills/code-refactor/scripts/gitlab_auto_mr.py"
  rg -q 'Diff Stat' "$PLUGIN_ROOT/skills/code-refactor/scripts/gitlab_auto_mr.py"
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
