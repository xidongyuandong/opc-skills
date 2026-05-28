# auto-merge-request

## Purpose

Create and manage a review-ready GitLab merge request from a local repository, including branch push, issue creation, issue/MR closing-link association, and verification that merge will close the issue.

## Required Inputs

- Target repository path.
- Target branch. Infer from context only when the branch is unambiguous; otherwise ask.
- Issue title and problem-focused issue description. Generate them from the diff when the user asks you to handle the whole flow.

## Rules

- Do not print tokens, `auth.json`, or unredacted credential files.
- Prefer HTTPS GitLab remotes with `git credential fill`.
- A completed MR must be `opened`, not Draft/WIP, have a pushed source branch, and have a related issue.
- A completed MR must include a readable Chinese overview that explains the intent, main changes, impact scope, and verification suggestions. Do not use the overview to merely repeat diff stat; GitLab already shows file-level statistics in the Changes tab.
- `approve` does not close issues. GitLab closes issues after merge when the MR description or commit message contains `Closes #N`, `Fixes #N`, or `Resolves #N`.
- Target the GitLab project default branch by default. If a requested target branch is not the project default branch, stop and explain that issue auto-close may not run unless the user explicitly accepts a non-default target.
- Do not reuse an existing issue or MR from memory, branch history, or an earlier session. Reuse only when the current user request explicitly provides an issue/MR URL or IID, or explicitly says to update a named existing issue/MR. Otherwise create a new issue and a new MR.
- For multiple repositories or worktrees, complete the full checklist per path. Do not count a worktree as done until its intended branch has committed changes, an upstream remote branch, and a matching MR.
- Preserve unrelated user changes. Stage only files intended for the requested MR.

## Workflow

1. Inspect the repository:
   ```bash
   git rev-parse --show-toplevel
   git rev-parse --git-dir
   git rev-parse --git-common-dir
   git remote -v
   git branch --show-current
   git status --short --branch
   git log -1 --oneline
   ```

2. Commit intended changes when the user has confirmed they should be included:
   ```bash
   git add <intended-files>
   git commit -m "<message>"
   ```

3. Ensure credential helper works. In devcontainers with a broken injected helper, reset locally:
   ```bash
   git config --local --add credential.helper ''
   git config --local --add credential.helper store
   ```
   For GitLab REST API calls, prefer a real API token from `GITLAB_TOKEN`, `GITLAB_PERSONAL_ACCESS_TOKEN`, `MARKETPLACE_ZXGC_ENV_FILE`, or the approved local env source `~/.claude/feishu.env`. Git HTTPS credentials may push successfully but still return `401 Unauthorized` from the GitLab API.

4. Push and verify upstream:
   ```bash
   git push -u origin HEAD
   git rev-parse --abbrev-ref --symbolic-full-name '@{u}'
   git ls-remote --heads origin "$(git branch --show-current)"
   ```

5. Use the helper script for GitLab API operations:
   ```bash
   python3 <skill-dir>/scripts/gitlab_auto_mr.py \
     --issue-title "<issue title>" \
     --issue-description "<issue body>"
   ```

   Pass `--target-branch <target-branch>` only when the requested target is explicit. The helper defaults to the GitLab project default branch and rejects non-default targets unless `--allow-non-default-target` is provided.
   The helper automatically appends Chinese overview sections built from local Git commits and changed-file categories. If the local Git range is unavailable or a more domain-specific summary is needed, pass `--change-summary` or `--change-summary-file`.

   Reuse existing objects when appropriate:
   ```bash
   python3 <skill-dir>/scripts/gitlab_auto_mr.py \
     --issue-iid <issue-iid> \
     --mr-iid <mr-iid> \
     --issue-title "<issue title>" \
     --issue-description "<issue body>"
   ```

6. Verify output:
   - Issue state is `opened` when the MR is expected to close a currently open problem.
   - MR state is `opened`.
   - MR is not Draft/WIP.
   - `detailed_merge_status` is acceptable or reported as a blocker.
   - `related_merge_requests` contains the MR.
   - MR description includes both a readable issue title and `Closes #N`.
   - MR description includes `变更概览`, `主要改动`, `影响范围`, and `验证建议`.
   - MR overview does not include `Diff Stat`; reviewers can inspect file-level statistics in the GitLab Changes tab.
   - `target_branch` equals `default_branch` unless a non-default target was explicitly accepted.
   - `warnings` is empty, or any warning is explained in the final response.

## MR Description Pattern

```text
Related issue: #ISSUE_IID Issue title here

Closes #ISSUE_IID

Source branch: source/name
Target branch: target/name

HEAD: abc1234 commit subject

## 变更概览

本次 MR 从 `source/name` 合入 `target/name`，主要处理：脚本/自动化流程。
摘要聚焦变更目的和 review 关注点；文件级增删统计请在 GitLab Changes 页查看。

## 主要改动

- add meaningful behavior summary here

## 影响范围

- 影响模块：脚本/自动化流程。

## 验证建议

- 检查 MR Changes 页确认文件级 diff 符合预期。

## 相关提交

```text
abc1234 commit subject
```
```

GitLab may need a few seconds to index a new closing reference; retry related-MR verification before declaring failure.
