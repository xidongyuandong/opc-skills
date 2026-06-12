#!/usr/bin/env bash
set -euo pipefail

MODE="dry-run"
TARGET="${CODEX_HOME:-$HOME/.codex}/rules/default.rules"
SOURCE=""

usage() {
  cat <<'EOF'
Usage:
  install-rules.sh [--dry-run|--apply] [--target PATH] [--source PATH]

Installs the marketplace-zxgc rules template with a timestamped backup.
The template is intentionally curated and does not mirror local runtime rules.
EOF
}

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
    --source)
      SOURCE="${2:?missing source}"
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

PLUGIN_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if [ -z "$SOURCE" ]; then
  SOURCE="$PLUGIN_ROOT/templates/rules/default.rules"
fi
STAMP="$(date +%Y%m%d%H%M%S)"

if [ ! -f "$SOURCE" ]; then
  echo "Missing rules source: $SOURCE" >&2
  exit 1
fi

echo "Mode: $MODE"
echo "Source: $SOURCE"
echo "Target: $TARGET"

if grep -E -n 'sk-[A-Za-z0-9_-]{20,}|AKIA[0-9A-Z]{16}|AIza[0-9A-Za-z_-]{20,}|xox[baprs]-[0-9A-Za-z-]+|token=|password=|secret=' "$SOURCE" >/dev/null; then
  echo "Potential secret-like value found in $SOURCE; refusing to install." >&2
  exit 1
fi

if [ "$MODE" = "dry-run" ]; then
  echo "Would back up and replace $TARGET with $SOURCE."
  echo "Re-run with --apply to install."
  exit 0
fi

mkdir -p "$(dirname "$TARGET")"
if [ -f "$TARGET" ]; then
  cp "$TARGET" "$TARGET.bak.$STAMP"
fi

cp "$SOURCE" "$TARGET"
echo "Installed $SOURCE -> $TARGET"
