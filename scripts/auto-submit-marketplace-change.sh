#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REMOTE="origin"
TARGET_BRANCH="master"
PROJECT_URL="https://gitlab.chehejia.com/zhengyuyu/marketplace-zxgc.git"
TITLE=""
ISSUE_TITLE=""
ISSUE_DESCRIPTION=""
MR_IID=""
ISSUE_IID=""
BRANCH=""
COMMIT_MESSAGE=""
APPLY=0
NO_VALIDATE=0
EXCLUDES=()

usage() {
  cat <<'USAGE'
Usage:
  scripts/auto-submit-marketplace-change.sh --dry-run [--title "..."]
  scripts/auto-submit-marketplace-change.sh --apply --title "..."

Options:
  --apply                     Create/switch branch, commit, push, and create/update GitLab MR.
  --dry-run                   Preview the inferred branch, validations, commit, and MR command. Default.
  --title TEXT                Human-readable change title. Used for branch, commit, issue, and MR.
  --issue-title TEXT          GitLab issue title. Defaults to --title.
  --issue-description TEXT    GitLab issue description.
  --mr-iid IID                Update an existing GitLab MR.
  --issue-iid IID             Reuse/update an existing GitLab issue.
  --branch NAME               Source branch. Defaults to content-based branch inference.
  --commit-message TEXT       Commit message. Defaults to inferred conventional message.
  --exclude PATH              Exclude a changed path from this automated submission. Repeatable.
  --target-branch NAME        MR target branch. Default: master.
  --project-url URL           GitLab HTTPS project URL.
  --remote NAME               Git remote. Default: origin.
  --no-validate               Skip local validation. Not recommended.

Environment:
  MARKETPLACE_ZXGC_ENV_FILE   Optional env file containing GITLAB_TOKEN or GITLAB_PERSONAL_ACCESS_TOKEN.
  If MARKETPLACE_ZXGC_ENV_FILE is unset, the script checks:
    $HOME/.config/marketplace-zxgc/env
    $HOME/.marketplace-zxgc.env
    $HOME/.claude/feishu.env
  GITLAB_TOKEN                GitLab API token for MR creation.
  GITLAB_PERSONAL_ACCESS_TOKEN Alternative token name; mapped to GITLAB_TOKEN when needed.
USAGE
}

die() {
  echo "error: $*" >&2
  exit 1
}

run() {
  if [ "$APPLY" -eq 1 ]; then
    "$@"
  else
    printf '+'
    printf ' %q' "$@"
    printf '\n'
  fi
}

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

slugify() {
  printf '%s' "$1" |
    tr '[:upper:]' '[:lower:]' |
    sed -E 's/[^a-z0-9]+/-/g; s/^-+//; s/-+$//; s/-+/-/g' |
    cut -c 1-48
}

changed_files() {
  git status --porcelain |
    sed -E 's/^...//' |
    sed -E 's/^(.+) -> (.+)$/\2/' |
    sort -u
}

filter_files() {
  local file
  while IFS= read -r file; do
    [ -n "$file" ] || continue
    local excluded=0
    local pattern
    if [ "${#EXCLUDES[@]}" -gt 0 ]; then
      for pattern in "${EXCLUDES[@]}"; do
        if [ "$file" = "$pattern" ]; then
          excluded=1
          break
        fi
      done
    fi
    if [ "$excluded" -eq 0 ]; then
      printf '%s\n' "$file"
    fi
  done
}

run_gitlab_mr() {
  local source_branch="$1"
  local mr_title="$2"
  local issue_title="$3"
  local issue_description="$4"
  local mr_cmd=(
    python3 "$ROOT/plugins/marketplace-zxgc/skills/code-refactor/scripts/gitlab_auto_mr.py"
    --project-url "$PROJECT_URL"
    --source-branch "$source_branch"
    --target-branch "$TARGET_BRANCH"
    --mr-title "$mr_title"
    --issue-title "$issue_title"
    --issue-description "$issue_description"
  )
  if [ -n "$MR_IID" ]; then
    mr_cmd+=(--mr-iid "$MR_IID")
  fi
  if [ -n "$ISSUE_IID" ]; then
    mr_cmd+=(--issue-iid "$ISSUE_IID")
  fi

  if [ "$APPLY" -eq 1 ]; then
    "${mr_cmd[@]}"
  else
    printf '+'
    printf ' %q' "${mr_cmd[@]}"
    printf '\n'
  fi
}

infer_branch() {
  local files="$1"
  local title_slug
  title_slug="$(slugify "$TITLE")"

  if [ -z "$title_slug" ]; then
    if printf '%s\n' "$files" | grep -Eq '(^|/)操作指导\.md$|(^|/)README\.md$|(^|/)docs/|(^|/)技能介绍\.md$'; then
      title_slug="update-marketplace-docs"
    elif printf '%s\n' "$files" | grep -Eq '(^|/)scripts/|hooks|install|sync'; then
      title_slug="automate-marketplace-maintenance"
    elif printf '%s\n' "$files" | grep -Eq '(^|/)skills/'; then
      title_slug="update-marketplace-skills"
    else
      title_slug="update-marketplace"
    fi
  fi

  if printf '%s\n' "$files" | grep -Eqv '(^|/)操作指导\.md$|(^|/)README\.md$|(^|/)docs/|(^|/)技能介绍\.md$'; then
    if printf '%s\n' "$files" | grep -Eq '(^|/)scripts/|hooks|install|sync|validate'; then
      printf 'fix/%s\n' "$title_slug"
    elif printf '%s\n' "$files" | grep -Eq '(^|/)skills/'; then
      printf 'feat/%s\n' "$title_slug"
    else
      printf 'chore/%s\n' "$title_slug"
    fi
  else
    printf 'docs/%s\n' "$title_slug"
  fi
}

infer_commit_message() {
  local files="$1"
  local summary="$TITLE"
  if [ -z "$summary" ]; then
    summary="update marketplace automation"
  fi

  if printf '%s\n' "$files" | grep -Eqv '(^|/)操作指导\.md$|(^|/)README\.md$|(^|/)docs/|(^|/)技能介绍\.md$'; then
    if printf '%s\n' "$files" | grep -Eq '(^|/)scripts/|hooks|install|sync|validate'; then
      printf 'fix: %s\n' "$summary"
    elif printf '%s\n' "$files" | grep -Eq '(^|/)skills/'; then
      printf 'feat: %s\n' "$summary"
    else
      printf 'chore: %s\n' "$summary"
    fi
  else
    printf 'docs: %s\n' "$summary"
  fi
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --apply)
      APPLY=1
      shift
      ;;
    --dry-run)
      APPLY=0
      shift
      ;;
    --title)
      TITLE="${2:-}"
      shift 2
      ;;
    --issue-title)
      ISSUE_TITLE="${2:-}"
      shift 2
      ;;
    --issue-description)
      ISSUE_DESCRIPTION="${2:-}"
      shift 2
      ;;
    --mr-iid)
      MR_IID="${2:-}"
      shift 2
      ;;
    --issue-iid)
      ISSUE_IID="${2:-}"
      shift 2
      ;;
    --branch)
      BRANCH="${2:-}"
      shift 2
      ;;
    --commit-message)
      COMMIT_MESSAGE="${2:-}"
      shift 2
      ;;
    --exclude)
      EXCLUDES+=("${2:-}")
      shift 2
      ;;
    --target-branch)
      TARGET_BRANCH="${2:-}"
      shift 2
      ;;
    --project-url)
      PROJECT_URL="${2:-}"
      shift 2
      ;;
    --remote)
      REMOTE="${2:-}"
      shift 2
      ;;
    --no-validate)
      NO_VALIDATE=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      die "unknown option: $1"
      ;;
  esac
done

cd "$ROOT"

git rev-parse --is-inside-work-tree >/dev/null
git remote get-url "$REMOTE" >/dev/null 2>&1 || die "missing git remote: $REMOTE"

if [ -n "${MARKETPLACE_ZXGC_ENV_FILE:-}" ]; then
  load_env_file "$MARKETPLACE_ZXGC_ENV_FILE" || die "MARKETPLACE_ZXGC_ENV_FILE points to a missing file: $MARKETPLACE_ZXGC_ENV_FILE"
else
  load_env_file "$HOME/.config/marketplace-zxgc/env" >/dev/null || true
  load_env_file "$HOME/.marketplace-zxgc.env" >/dev/null || true
  load_env_file "$HOME/.claude/feishu.env" >/dev/null || true
fi

if [ -n "${GITLAB_PERSONAL_ACCESS_TOKEN:-}" ] && [ -z "${GITLAB_TOKEN:-}" ]; then
  export GITLAB_TOKEN="$GITLAB_PERSONAL_ACCESS_TOKEN"
fi

files="$(changed_files | filter_files)"
if [ -z "$files" ]; then
  if [ -z "$BRANCH" ]; then
    BRANCH="$(git branch --show-current)"
  fi
  if git rev-parse --verify "$REMOTE/$TARGET_BRANCH" >/dev/null 2>&1 &&
      [ -n "$(git log --oneline "$REMOTE/$TARGET_BRANCH..HEAD")" ]; then
    if [ -z "$TITLE" ]; then
      TITLE="submit existing marketplace commits"
    fi
    if [ -z "$ISSUE_TITLE" ]; then
      ISSUE_TITLE="$TITLE"
    fi
    if [ -z "$ISSUE_DESCRIPTION" ]; then
      ISSUE_DESCRIPTION="Automated marketplace-zxgc submission for existing commits on $BRANCH.

Commits:
$(git log --oneline "$REMOTE/$TARGET_BRANCH..HEAD" | sed 's/^/- /')"
    fi
    echo "No file changes after exclusions; submitting existing commits on $BRANCH."
    if [ -n "${GITLAB_TOKEN:-}" ]; then
      export GITLAB_PUSH_TOKEN="$GITLAB_TOKEN"
      helper='!f() { echo username=oauth2; echo password=$GITLAB_PUSH_TOKEN; }; f'
      run git -c credential.helper="$helper" push -u "$REMOTE" "$BRANCH"
    else
      run git push -u "$REMOTE" "$BRANCH"
    fi
    run_gitlab_mr "$BRANCH" "$TITLE" "$ISSUE_TITLE" "$ISSUE_DESCRIPTION"
    exit 0
  fi
  if [ -n "$MR_IID" ] || [ -n "$ISSUE_IID" ]; then
    if [ -z "$TITLE" ]; then
      TITLE="update marketplace MR"
    fi
    if [ -z "$ISSUE_TITLE" ]; then
      ISSUE_TITLE="$TITLE"
    fi
    if [ -z "$ISSUE_DESCRIPTION" ]; then
      ISSUE_DESCRIPTION="Automated marketplace-zxgc MR metadata update."
    fi
    echo "No marketplace file changes after exclusions; updating GitLab issue/MR metadata only."
    run_gitlab_mr "$BRANCH" "$TITLE" "$ISSUE_TITLE" "$ISSUE_DESCRIPTION"
    exit 0
  fi
  echo "No marketplace changes to submit after exclusions."
  exit 0
fi

if [ -z "$BRANCH" ]; then
  BRANCH="$(infer_branch "$files")"
fi
if [ -z "$COMMIT_MESSAGE" ]; then
  COMMIT_MESSAGE="$(infer_commit_message "$files")"
fi
if [ -z "$TITLE" ]; then
  TITLE="${COMMIT_MESSAGE#*: }"
fi
if [ -z "$ISSUE_TITLE" ]; then
  ISSUE_TITLE="$TITLE"
fi
if [ -z "$ISSUE_DESCRIPTION" ]; then
  ISSUE_DESCRIPTION="Automated marketplace-zxgc maintenance submission.

Changed files:
$(printf '%s\n' "$files" | sed 's/^/- /')"
fi

cat <<PLAN
marketplace-zxgc auto submit plan
root: $ROOT
remote: $REMOTE
target_branch: $TARGET_BRANCH
source_branch: $BRANCH
commit_message: $COMMIT_MESSAGE
project_url: $PROJECT_URL
mode: $([ "$APPLY" -eq 1 ] && echo apply || echo dry-run)

changed_files:
$(printf '%s\n' "$files" | sed 's/^/- /')

PLAN

if [ "$NO_VALIDATE" -eq 0 ]; then
  "$ROOT/plugins/marketplace-zxgc/scripts/validate-pack.sh"
  "$ROOT/scripts/install-marketplace-zxgc.sh" --dry-run >/tmp/marketplace-zxgc-install-dryrun.out
  tail -5 /tmp/marketplace-zxgc-install-dryrun.out
  git diff --check
  if command -v rg >/dev/null 2>&1; then
    rg -n '/Users/|feishu.env|https://[^ ]+@|token=|password=|secret=|authorization|cookie|private key' \
      README.md docs 操作指导.md scripts plugins || true
  fi
fi

current_branch="$(git branch --show-current)"
if [ "$current_branch" != "$BRANCH" ]; then
  if git show-ref --verify --quiet "refs/heads/$BRANCH"; then
    run git switch "$BRANCH"
  else
    run git switch -c "$BRANCH"
  fi
fi

while IFS= read -r file; do
  [ -n "$file" ] || continue
  run git add -- "$file"
done <<< "$files"

if [ "$APPLY" -eq 1 ] && git diff --cached --quiet; then
  echo "No staged marketplace changes to submit."
  exit 0
fi

run git commit -m "$COMMIT_MESSAGE"

if [ -n "${GITLAB_TOKEN:-}" ]; then
  export GITLAB_PUSH_TOKEN="$GITLAB_TOKEN"
  helper='!f() { echo username=oauth2; echo password=$GITLAB_PUSH_TOKEN; }; f'
  run git -c credential.helper="$helper" push -u "$REMOTE" "$BRANCH"
else
  run git push -u "$REMOTE" "$BRANCH"
fi

run_gitlab_mr "$BRANCH" "$TITLE" "$ISSUE_TITLE" "$ISSUE_DESCRIPTION"
