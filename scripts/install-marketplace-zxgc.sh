#!/usr/bin/env bash
set -euo pipefail

MODE="dry-run"
SMOKE_TEST="yes"
AGENTS_MODE="block"

usage() {
  cat <<'EOF'
Usage:
  scripts/install-marketplace-zxgc.sh [--dry-run|--apply] [--smoke-test|--no-smoke-test] [--agents-mode block|replace]

Environment:
  CODEX_HOME              Codex home. Defaults to $HOME/.codex.
  CODEX_BIN               Codex executable. Defaults to codex.
  MARKETPLACE_ZXGC_HOME   marketplace-zxgc repository root. Defaults to this script's repository root.
  ZXGC_SKILLS             Optional space-separated skill allowlist for sync-skills.sh.
  ZXGC_LINK_SKILLS        Optional space-separated skills to install as symlinks.
  ZXGC_REMOVED_SKILLS     Optional space-separated deprecated skills to move out of active skills.

The script is dry-run by default. Use --apply to mutate Codex configuration.
EOF
}

while [ $# -gt 0 ]; do
  case "$1" in
    --dry-run)
      MODE="dry-run"
      shift
      ;;
    --apply)
      MODE="apply"
      shift
      ;;
    --smoke-test)
      SMOKE_TEST="yes"
      shift
      ;;
    --no-smoke-test)
      SMOKE_TEST="no"
      shift
      ;;
    --agents-mode)
      AGENTS_MODE="${2:?missing agents mode}"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

if [ "$MODE" != "dry-run" ] && [ "$MODE" != "apply" ]; then
  echo "Invalid mode: $MODE" >&2
  exit 2
fi

if [ "$AGENTS_MODE" != "block" ] && [ "$AGENTS_MODE" != "replace" ]; then
  echo "--agents-mode must be block or replace" >&2
  exit 2
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="${MARKETPLACE_ZXGC_HOME:-$(cd "$SCRIPT_DIR/.." && pwd)}"
PLUGIN_ROOT="$REPO_ROOT/plugins/marketplace-zxgc"
CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
CODEX_BIN="${CODEX_BIN:-codex}"
export CODEX_HOME
export CODEX_BIN
export MARKETPLACE_ZXGC_HOME="$REPO_ROOT"

require_command() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "Missing required command: $1" >&2
    exit 1
  fi
}

run_step() {
  echo
  echo "==> $*"
  "$@"
}

preflight() {
  require_command git
  require_command bash
  require_command python3
  require_command jq

  if [ ! -x "$CODEX_BIN" ] && ! command -v "$CODEX_BIN" >/dev/null 2>&1; then
    echo "CODEX_BIN is not executable and not on PATH: $CODEX_BIN" >&2
    exit 1
  fi

  if [ ! -d "$REPO_ROOT/.git" ]; then
    echo "MARKETPLACE_ZXGC_HOME is not a git repository root: $REPO_ROOT" >&2
    exit 1
  fi

  if [ ! -f "$REPO_ROOT/.agents/plugins/marketplace.json" ]; then
    echo "Missing marketplace manifest: $REPO_ROOT/.agents/plugins/marketplace.json" >&2
    exit 1
  fi

  if [ ! -f "$PLUGIN_ROOT/.codex-plugin/plugin.json" ]; then
    echo "Missing plugin manifest: $PLUGIN_ROOT/.codex-plugin/plugin.json" >&2
    exit 1
  fi
}

print_context() {
  echo "Mode: $MODE"
  echo "Repository: $REPO_ROOT"
  echo "Plugin root: $PLUGIN_ROOT"
  echo "CODEX_HOME: $CODEX_HOME"
  echo "CODEX_BIN: $CODEX_BIN"
  echo "AGENTS mode: $AGENTS_MODE"
  echo "Smoke test: $SMOKE_TEST"
}

verify_installation() {
  echo
  echo "==> verify installed files"
  test -f "$CODEX_HOME/AGENTS.md"
  test -f "$CODEX_HOME/hooks.json"
  test -f "$CODEX_HOME/rules/default.rules"
  test -f "$CODEX_HOME/skills/marketplace-zxgc/SKILL.md"
  test -f "$CODEX_HOME/skills/code-refactor/SKILL.md"
  test -f "$CODEX_HOME/skills/session-self-improvement/SKILL.md"

  stale_count="$(
    { find "$CODEX_HOME/skills" -maxdepth 2 -name SKILL.md -print 2>/dev/null |
      grep -E 'bak|backup|moved|deprecated|auto-merge-request' || true; } |
      wc -l |
      tr -d ' '
  )"
  if [ "$stale_count" != "0" ]; then
    echo "Found stale/deprecated active skills: $stale_count" >&2
    find "$CODEX_HOME/skills" -maxdepth 2 -name SKILL.md -print 2>/dev/null |
      grep -E 'bak|backup|moved|deprecated|auto-merge-request' >&2
    exit 1
  fi

  "$CODEX_BIN" plugin list | grep -q 'marketplace-zxgc@marketplace-zxgc (installed, enabled)'
  echo "Installation verification passed"
}

run_smoke_test() {
  if [ "$SMOKE_TEST" != "yes" ]; then
    return 0
  fi
  echo
  echo "==> codex smoke test"
  CODEX_HOME="$CODEX_HOME" "$CODEX_BIN" exec \
    --dangerously-bypass-hook-trust \
    --skip-git-repo-check \
    --sandbox read-only \
    "只输出 marketplace-zxgc smoke ok"
}

preflight
print_context

run_step "$PLUGIN_ROOT/scripts/validate-pack.sh"

if [ "$MODE" = "dry-run" ]; then
  echo
  echo "==> dry-run marketplace registration"
  echo "Would run: $CODEX_BIN plugin marketplace add $REPO_ROOT"
  echo "Would run: $CODEX_BIN plugin remove marketplace-zxgc@marketplace-zxgc"
  echo "Would run: $CODEX_BIN plugin add marketplace-zxgc@marketplace-zxgc"
  CODEX_HOME="$CODEX_HOME" run_step "$PLUGIN_ROOT/scripts/sync-skills.sh" --dry-run
  run_step "$PLUGIN_ROOT/scripts/install-agents-md.sh" --mode "$AGENTS_MODE" --target "$CODEX_HOME/AGENTS.md"
  CODEX_HOME="$CODEX_HOME" run_step "$PLUGIN_ROOT/scripts/install-rules.sh" --dry-run
  CODEX_HOME="$CODEX_HOME" run_step "$PLUGIN_ROOT/scripts/install-hooks.sh" --dry-run
  echo
  echo "Dry run passed. Re-run with --apply to install."
  exit 0
fi

run_step "$CODEX_BIN" plugin marketplace add "$REPO_ROOT"
"$CODEX_BIN" plugin remove marketplace-zxgc@marketplace-zxgc >/dev/null 2>&1 || true
run_step "$CODEX_BIN" plugin add marketplace-zxgc@marketplace-zxgc
CODEX_HOME="$CODEX_HOME" run_step "$PLUGIN_ROOT/scripts/sync-skills.sh" --apply
run_step "$PLUGIN_ROOT/scripts/install-agents-md.sh" --mode "$AGENTS_MODE" --target "$CODEX_HOME/AGENTS.md" --yes
CODEX_HOME="$CODEX_HOME" run_step "$PLUGIN_ROOT/scripts/install-rules.sh" --apply
CODEX_HOME="$CODEX_HOME" run_step "$PLUGIN_ROOT/scripts/install-hooks.sh" --apply
verify_installation
run_smoke_test

echo
echo "marketplace-zxgc automated installation completed"
