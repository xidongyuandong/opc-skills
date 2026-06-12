#!/usr/bin/env bash
set -euo pipefail

MODE="dry-run"
TARGET="${CODEX_HOME:-$HOME/.codex}/hooks.json"

while [ $# -gt 0 ]; do
  case "$1" in
    --apply)
      MODE="apply"
      shift
      ;;
    --dry-run)
      MODE="dry-run"
      shift
      ;;
    --target)
      TARGET="${2:?missing target}"
      shift 2
      ;;
    -h|--help)
      echo "Usage: $0 [--dry-run|--apply] [--target PATH]"
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      exit 2
      ;;
  esac
done

PLUGIN_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SOURCE="$PLUGIN_ROOT/hooks.json"
TEMPLATE="$PLUGIN_ROOT/hooks.json.template"
STAMP="$(date +%Y%m%d%H%M%S)"

echo "Mode: $MODE"
echo "Template: $TEMPLATE"
echo "Target: $TARGET"

if [ "$MODE" = "dry-run" ]; then
  jq empty "$TEMPLATE"
  sed "s#{{PLUGIN_ROOT}}#$PLUGIN_ROOT#g" "$TEMPLATE" | jq empty
  echo "Would render hooks template with PLUGIN_ROOT=$PLUGIN_ROOT, then back up and replace hooks.json."
  exit 0
fi

mkdir -p "$(dirname "$TARGET")"
if [ -f "$TARGET" ]; then
  cp "$TARGET" "$TARGET.bak.$STAMP"
fi
sed "s#{{PLUGIN_ROOT}}#$PLUGIN_ROOT#g" "$TEMPLATE" > "$TARGET"
jq empty "$TARGET"
echo "Installed rendered hooks from $TEMPLATE -> $TARGET"
