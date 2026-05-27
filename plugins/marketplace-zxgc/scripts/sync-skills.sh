#!/usr/bin/env bash
set -euo pipefail

MODE="dry-run"
if [ "${1:-}" = "--apply" ]; then
  MODE="apply"
elif [ "${1:-}" = "--dry-run" ] || [ $# -eq 0 ]; then
  MODE="dry-run"
else
  echo "Usage: $0 [--dry-run|--apply]" >&2
  exit 2
fi

PLUGIN_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
TARGET_ROOT="$CODEX_HOME/skills"
BACKUP_ROOT="$CODEX_HOME/backups/skills"
STAMP="$(date +%Y%m%d%H%M%S)"

DEFAULT_SKILLS="marketplace-zxgc session-self-improvement twin-agent-zyy self-improving-agent continuous-learning-v2 code-refactor codex-hooks codex-hook codex-remote-container codex-ssh-remote-config algorithm-engineer-workflow algorithm-data-diagnosis algorithm-tensorboard-analysis algorithm-training-debug algorithm-training-review algorithm-rl-debug algorithm-eval-diagnosis algorithm-eval-closure algorithm-agent-trace-analysis"
SKILLS="${ZXGC_SKILLS:-$DEFAULT_SKILLS}"
LINK_SKILLS="${ZXGC_LINK_SKILLS:-}"
REMOVED_SKILLS="${ZXGC_REMOVED_SKILLS:-auto-merge-request.moved-to-code-refactor.20260521}"

is_link_skill() {
  case " $LINK_SKILLS " in
    *" $1 "*) return 0 ;;
    *) return 1 ;;
  esac
}

echo "Mode: $MODE"
echo "Source: $PLUGIN_ROOT/skills"
echo "Target: $TARGET_ROOT"
echo "Backup: $BACKUP_ROOT/$STAMP"
echo "Skills: $SKILLS"
echo "Removed skills: ${REMOVED_SKILLS:-<none>}"

for skill in $REMOVED_SKILLS; do
  dst="$TARGET_ROOT/$skill"
  if [ ! -e "$dst" ]; then
    continue
  fi
  if [ "$MODE" = "dry-run" ]; then
    echo "Would remove deprecated skill $dst -> $BACKUP_ROOT/$STAMP/$skill"
    continue
  fi
  mkdir -p "$BACKUP_ROOT/$STAMP"
  backup="$BACKUP_ROOT/$STAMP/$skill"
  echo "Removing deprecated skill $dst -> $backup"
  mv "$dst" "$backup"
done

for skill in $SKILLS; do
  src="$PLUGIN_ROOT/skills/$skill"
  dst="$TARGET_ROOT/$skill"
  if [ ! -d "$src" ]; then
    echo "Skip missing packaged skill: $skill" >&2
    continue
  fi
  if [ "$MODE" = "dry-run" ]; then
    if [ -e "$dst" ]; then
      echo "Would back up $dst -> $BACKUP_ROOT/$STAMP/$skill"
    fi
    if is_link_skill "$skill"; then
      echo "Would link $dst -> $src"
    else
      echo "Would sync $src -> $dst"
    fi
    continue
  fi
  mkdir -p "$TARGET_ROOT"
  if [ -e "$dst" ]; then
    mkdir -p "$BACKUP_ROOT/$STAMP"
    backup="$BACKUP_ROOT/$STAMP/$skill"
    echo "Backing up $dst -> $backup"
    mv "$dst" "$backup"
  fi
  if is_link_skill "$skill"; then
    ln -s "$src" "$dst"
    echo "Linked $skill"
  else
    cp -R "$src" "$dst"
    echo "Synced $skill"
  fi
done
