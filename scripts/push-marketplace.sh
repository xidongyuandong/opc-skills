#!/bin/zsh
set -euo pipefail

ROOT="/Users/zhengyuyu/marketplace-zxgc"
ENV_FILE="/Users/zhengyuyu/.claude/feishu.env"
REMOTE="${1:-origin}"
BRANCH="${2:-main}"

cd "$ROOT"

if [[ ! -f "$ENV_FILE" ]]; then
  echo "Missing env file: $ENV_FILE" >&2
  exit 1
fi

set -a
source "$ENV_FILE"
set +a

if [[ -z "${GITLAB_PERSONAL_ACCESS_TOKEN:-}" ]]; then
  echo "GITLAB_PERSONAL_ACCESS_TOKEN is not set in $ENV_FILE" >&2
  exit 1
fi

if ! git remote get-url "$REMOTE" >/dev/null 2>&1; then
  echo "Missing git remote: $REMOTE" >&2
  exit 1
fi

plugins/marketplace-zxgc/scripts/validate-pack.sh
git diff --check

if [[ -z "$(git status --porcelain)" ]]; then
  echo "No marketplace changes to push."
  exit 0
fi

git add .

if git diff --cached --quiet; then
  echo "No staged marketplace changes to push."
  exit 0
fi

timestamp="$(date '+%Y-%m-%d %H:%M')"
git commit -m "chore: update marketplace-zxgc ${timestamp}"

git -c credential.helper='!f() { echo username=oauth2; echo password=$GITLAB_PERSONAL_ACCESS_TOKEN; }; f' \
  pull --rebase "$REMOTE" "$BRANCH"
git -c credential.helper='!f() { echo username=oauth2; echo password=$GITLAB_PERSONAL_ACCESS_TOKEN; }; f' \
  push "$REMOTE" "$BRANCH"
