---
name: auto-issue
description: Create, update, or draft GitLab issues from user-provided information or current context. Use when the user asks to submit/create/file an issue, gives a GitLab issue URL or repository URL, asks Codex to turn context into an issue, or requests the standard issue format with task/background/dependencies/expected result/evaluation.
---

# Auto Issue

Use this skill to turn context into a structured GitLab issue. Extract only evidence-backed information; do not invent product facts, root causes, owners, or deadlines.

## Workflow

1. Classify the target:
   - GitLab issue URL containing `/-/issues/<id>`: existing issue target. Ask before editing/commenting if the user did not explicitly request an update.
   - GitLab repository URL without `/-/issues/<id>`: new issue target.
   - No GitLab URL: read the current context, then ask the user for the target repo or issue URL before submission.
2. Build the issue draft with exactly these sections:
   - `任务`
   - `背景描述`
   - `依赖`
   - `预期效果`
   - `评测`
3. Use `scripts/format_issue.py` when deterministic formatting or URL classification is useful.
4. Submit only when the target and permission are clear and a GitLab-capable tool/API/browser workflow is available. If submission is unavailable, return the draft, target status, and exact next action. Never claim an issue was submitted unless the submission result was observed.
5. If the workflow needs detailed target handling, read `references/gitlab_issue_workflow.md`.

## Drafting Rules

- Prefer concrete file paths, commands, logs, links, and acceptance checks from context.
- Put uncertain or missing information in a short `待确认` note outside the issue body; do not hide uncertainty inside the issue.
- Keep `依赖` focused on required files, repositories, skills, systems, credentials/permissions, and external services. Do not expose credential values.
- Keep `评测` executable: commands, checks, expected UI/API result, metric, or review criterion.
- If the user supplies an existing issue URL, distinguish “update/comment existing issue” from “create related new issue”.

## Safety

- Do not print tokens, cookies, private keys, authorization headers, or raw credential files.
- Do not use a guessed GitLab project. Ask for the URL if the target is absent or ambiguous.
- Do not perform destructive issue operations such as closing, deleting, or changing labels unless the user explicitly requests them.

## Useful Commands

```bash
python3 "$CODEX_HOME/skills/auto-issue/scripts/format_issue.py" \
  --text "修复日志路径混乱；需要统一 logs 分组；验证 bash -n" \
  --url "https://gitlab.chehejia.com/lilizhao/cov-evalution" \
  --json
```
