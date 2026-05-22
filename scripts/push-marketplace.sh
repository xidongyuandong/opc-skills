#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REMOTE="${1:-origin}"
BRANCH="${2:-master}"

cd "$ROOT"

load_env_file() {
  local file="$1"
  if [ -f "$file" ]; then
    set -a
    # shellcheck disable=SC1090
    source "$file"
    set +a
    echo "Loaded environment from $file"
    return 0
  fi
  return 1
}

if [ -n "${MARKETPLACE_ZXGC_ENV_FILE:-}" ]; then
  if ! load_env_file "$MARKETPLACE_ZXGC_ENV_FILE"; then
    echo "MARKETPLACE_ZXGC_ENV_FILE points to a missing file: $MARKETPLACE_ZXGC_ENV_FILE" >&2
    exit 1
  fi
else
  load_env_file "$HOME/.config/marketplace-zxgc/env" >/dev/null || true
  load_env_file "$HOME/.marketplace-zxgc.env" >/dev/null || true
fi

TOKEN="${GITLAB_PERSONAL_ACCESS_TOKEN:-${GITLAB_TOKEN:-}}"
if [ -n "$TOKEN" ]; then
  GIT_CREDENTIAL_HELPER='!f() { echo username=oauth2; echo password=$GITLAB_PUSH_TOKEN; }; f'
  export GITLAB_PUSH_TOKEN="$TOKEN"
else
  GIT_CREDENTIAL_HELPER=""
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

if [ -n "$GIT_CREDENTIAL_HELPER" ]; then
  git -c credential.helper="$GIT_CREDENTIAL_HELPER" pull --rebase "$REMOTE" "$BRANCH"
  git -c credential.helper="$GIT_CREDENTIAL_HELPER" push "$REMOTE" "$BRANCH"
else
  git pull --rebase "$REMOTE" "$BRANCH"
  git push "$REMOTE" "$BRANCH"
fi
