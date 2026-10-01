#!/usr/bin/env bash
set -euo pipefail

MODE="block"
YES="no"
TARGET="$HOME/AGENTS.md"

while [ $# -gt 0 ]; do
  case "$1" in
    --mode)
      MODE="${2:?missing mode}"
      shift 2
      ;;
    --target)
      TARGET="${2:?missing target}"
      shift 2
      ;;
    --yes)
      YES="yes"
      shift
      ;;
    -h|--help)
      echo "Usage: $0 [--mode block|replace] [--target PATH] [--yes]"
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      exit 2
      ;;
  esac
done

if [ "$MODE" != "block" ] && [ "$MODE" != "replace" ]; then
  echo "--mode must be block or replace" >&2
  exit 2
fi

PLUGIN_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SOURCE="$PLUGIN_ROOT/templates/AGENTS.global.md"
STAMP="$(date +%Y%m%d%H%M%S)"

if [ "$YES" != "yes" ]; then
  echo "Dry confirmation: would install $SOURCE -> $TARGET using mode=$MODE"
  echo "Re-run with --yes to apply."
  exit 0
fi

mkdir -p "$(dirname "$TARGET")"
if [ -f "$TARGET" ]; then
  cp "$TARGET" "$TARGET.bak.$STAMP"
fi

if [ "$MODE" = "replace" ]; then
  cp "$SOURCE" "$TARGET"
  echo "Replaced $TARGET with $SOURCE"
  exit 0
fi

python3 - "$TARGET" "$SOURCE" <<'PY'
from pathlib import Path
import sys

target = Path(sys.argv[1])
source = Path(sys.argv[2])
start = "<!-- marketplace-zxgc:start -->"
end = "<!-- marketplace-zxgc:end -->"
block = f"{start}\n{source.read_text(encoding='utf-8').rstrip()}\n{end}\n"

old = target.read_text(encoding="utf-8") if target.exists() else ""
if start in old and end in old:
    before, rest = old.split(start, 1)
    _, after = rest.split(end, 1)
    new = before.rstrip() + "\n\n" + block + after.lstrip()
else:
    new = old.rstrip() + "\n\n" + block if old.strip() else block
target.write_text(new, encoding="utf-8")
PY

echo "Installed managed marketplace-zxgc block into $TARGET"
