---
name: task2zxgc
description: Summarize the current Codex session into a task report and push it to a configured task report Git repository.
metadata:
  version: 1.1.0
---

# task2zxgc

Use this skill when the user runs `/task2zxgc` or asks to export the current Codex session as a task summary.

## Behavior

The skill generates a Markdown report from the current full Codex session and pushes it to the configured task report repository.

Default target repository:

`https://gitlab.chehejia.com/ep/ai/ai-coding-zxgc-managment.git`

Override it on other machines with `TASK2ZXGC_REPO_URL` or `--repo-url`.

The output path in that repository is:

`{username}/{YYYY-MM-DD-HH}-{task-title}.md`

`username` defaults to `TASK2ZXGC_USERNAME`, then `TASK2ZXGC_AUTHOR`, then `git config user.name`, then OS user. Use `--username` for a one-off override.

The report includes:

- 任务主题
- 用户原始输入, as an independent module for需求文件内容、命令行输入、会话用户消息等可追溯摘录
- 需求描述
- 用户输入逐条记录，按顺序包含上传会话里的每一句用户输入，并用代码块尽量保留原文格式；单条过长时缩略，敏感信息必须脱敏
- 任务执行过程
- 完成的任务
- 执行结果
- 需求描述中的待优化点, summarized by the Agent instead of copied from raw prompts or tool logs
- 全方位诊断
- 会话证据摘要

For long sessions or sessions with multiple independent topics, do not select only one focus. Split the session into the minimum number of independent reports and push all of them. Each report must have one core claim and must be independently readable.

Topic split rules:

- First try one report: if one sentence can express the whole session's object, judgment, value, and boundary, keep one report.
- Split when the session contains independent troubleshooting, feature implementation, research/decision, repository analysis, general workflow, or algorithm-direction chains that cannot be governed by one claim.
- Use the smallest number of reports that preserves completeness; do not over-split related work.
- Each report must choose one main material type and one reader task: understand a mechanism, complete a task, troubleshoot a failure, understand an implementation, make a technical decision, or reuse a workflow.
- Preserve evidence boundaries: distinguish session facts, Agent inference, and recommended next steps.
- Keep raw chat logs, long tool dumps, secrets, credentials, and unrelated transient progress out of every report.

## Manual Run

When the user invokes `/task2zxgc`, use the Agent-based flow. First dump the session context:

```bash
TASK2ZXGC_SCRIPT="${MARKETPLACE_ZXGC_HOME:-$HOME/marketplace-zxgc}/plugins/marketplace-zxgc/skills/task2zxgc/scripts/task2zxgc.py"
python3 "$TASK2ZXGC_SCRIPT" --dump-context
```

Then, as the Codex Agent, synthesize a JSON object. For a single-topic session, use this shape:

```json
{
  "task_title": "任务051902",
  "task_theme": "用一段话说明此次任务的核心目标。",
  "core_requirement": "对原始需求描述的核心摘要。",
  "user_original_inputs": [
    {
      "source": "需求文件内容 | 命令行输入 | 会话用户消息",
      "content": "用户原始输入的脱敏摘录。",
      "note": "可选：文件路径、命令入口或上下文说明。"
    }
  ],
  "raw_requirements": ["所有用户输入的可追溯摘要"],
  "requirements": ["兼容字段：归纳后的需求描述"],
  "execution_process": ["按阶段归纳的任务执行过程"],
  "completed_tasks": ["归纳后的完成事项"],
  "execution_result": ["执行结果和完成度诊断"],
  "improvement_points": ["Agent 归纳后的待优化点，不复制原始信息"],
  "diagnostics": [
    {
      "category": "incomplete-requirements | context-loss | tooling-limitation | effective-pattern | outcome",
      "attribution": "user-actionable | ai-capability | environmental | collaborative",
      "severity": "low | medium | high",
      "confidence": 90,
      "description": "中性描述诊断结论。",
      "suggested_action": "可执行改进建议。"
    }
  ],
  "evidence": ["少量会话证据摘要"]
}
```

For a multi-topic session, use this shape and fill each `reports[]` item with the same single-report fields:

```json
{
  "reports": [
    {
      "task_title": "主题一短标题",
      "task_theme": "围绕一个核心主张总结主题一。",
      "core_requirement": "主题一的核心需求摘要。",
      "user_original_inputs": [
        {
          "source": "需求文件内容 | 命令行输入 | 会话用户消息",
          "content": "主题一相关用户原始输入的脱敏摘录。",
          "note": "可选来源说明。"
        }
      ],
      "raw_requirements": ["主题一相关用户输入的可追溯摘要"],
      "requirements": ["兼容字段：主题一归纳后的需求描述"],
      "execution_process": ["主题一的执行过程"],
      "completed_tasks": ["主题一完成事项"],
      "execution_result": ["主题一执行结果"],
      "improvement_points": ["主题一待优化点"],
      "diagnostics": [],
      "evidence": ["主题一证据摘要"]
    },
    {
      "task_title": "主题二短标题",
      "task_theme": "围绕另一个独立核心主张总结主题二。",
      "core_requirement": "主题二的核心需求摘要。",
      "user_original_inputs": [
        {
          "source": "需求文件内容 | 命令行输入 | 会话用户消息",
          "content": "主题二相关用户原始输入的脱敏摘录。",
          "note": "可选来源说明。"
        }
      ],
      "raw_requirements": ["主题二相关用户输入的可追溯摘要"],
      "requirements": ["兼容字段：主题二归纳后的需求描述"],
      "execution_process": ["主题二的执行过程"],
      "completed_tasks": ["主题二完成事项"],
      "execution_result": ["主题二执行结果"],
      "improvement_points": ["主题二待优化点"],
      "diagnostics": [],
      "evidence": ["主题二证据摘要"]
    }
  ]
}
```

Use `$AI_INSIGHTS_REPO` as the diagnostic reference. Its useful patterns for this skill are: stable friction taxonomy, attribution/severity/confidence, effective patterns, outcome guidance, prompt-quality dimensions, and evidence sidecar thinking.

`reference_points_ai_insights` is injected by `--dump-context` as internal Agent guidance. Do not render it as a final report section. The final report should show its effect through better `core_requirement`, `user_original_inputs`, `raw_requirements`, `completed_tasks`, `execution_result`, `improvement_points`, and `diagnostics`.

`user_original_inputs` is the independent module for user-provided source material. Use it to preserve脱敏后的需求文件内容、命令行输入、关键会话用户消息等原始输入摘录 so reviewers can evaluate whether the user described the task effectively. Do not put secrets, full raw long chats, or unbounded tool output there.

`requirements` is a compatibility field. Prefer `core_requirement`, `user_original_inputs`, and `raw_requirements` when generating new Agent summaries.

Finally push with the Agent-generated summary:

```bash
TASK2ZXGC_SCRIPT="${MARKETPLACE_ZXGC_HOME:-$HOME/marketplace-zxgc}/plugins/marketplace-zxgc/skills/task2zxgc/scripts/task2zxgc.py"
python3 "$TASK2ZXGC_SCRIPT" --push --agent-summary-file /path/to/agent-summary.json
```

When the JSON contains `reports`, the script renders every report and commits all generated Markdown files together.

Do not run `--push` without an Agent summary. The script refuses that by default so production reports do not fall back to rule-based extraction.

For validation without GitLab side effects, run:

```bash
TASK2ZXGC_SCRIPT="${MARKETPLACE_ZXGC_HOME:-$HOME/marketplace-zxgc}/plugins/marketplace-zxgc/skills/task2zxgc/scripts/task2zxgc.py"
python3 "$TASK2ZXGC_SCRIPT" --dry-run --agent-summary-file /path/to/agent-summary.json
```

## Team Configuration

Use environment variables for machine-specific configuration. Do not commit credentials or absolute local paths into this skill.

- `CODEX_HOME`: Codex home used to find sessions; defaults to `$HOME/.codex`.
- `TASK2ZXGC_CODEX_HOME`: task2zxgc-specific override for Codex home.
- `TASK2ZXGC_STATE_DIR`: pending marker and cloned report repo state; defaults to `$CODEX_HOME/task2zxgc`.
- `TASK2ZXGC_REPO_URL`: target report repository URL; overrides the built-in default.
- `TASK2ZXGC_REPO_DIR`: local clone directory for the target report repository.
- `TASK2ZXGC_USERNAME` / `TASK2ZXGC_AUTHOR`: output namespace under the report repository.
- `AI_INSIGHTS_REPO`: optional diagnostic reference repository; defaults to `$HOME/ai-insights`.

Example:

```bash
export CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
export MARKETPLACE_ZXGC_HOME="${MARKETPLACE_ZXGC_HOME:-$HOME/marketplace-zxgc}"
export TASK2ZXGC_REPO_URL="https://gitlab.chehejia.com/ep/ai/ai-coding-zxgc-managment.git"
export TASK2ZXGC_REPO_DIR="$CODEX_HOME/task2zxgc/ai-coding-zxgc-managment"
export TASK2ZXGC_USERNAME="$(git config user.name 2>/dev/null || whoami)"
```

GitLab authentication must come from the user's Git credential helper, SSH key, or local environment. Never put tokens in the repository URL inside committed files.

## Posthook Mode

The Codex `Stop` hook is configured to call:

```bash
python3 "$MARKETPLACE_ZXGC_HOME/plugins/marketplace-zxgc/hooks/task2zxgc_posthook.py" --event Stop
```

The posthook is intentionally idle by default. It only pushes when a pending marker exists, which can be created with:

```bash
TASK2ZXGC_SCRIPT="${MARKETPLACE_ZXGC_HOME:-$HOME/marketplace-zxgc}/plugins/marketplace-zxgc/skills/task2zxgc/scripts/task2zxgc.py"
python3 "$TASK2ZXGC_SCRIPT" --request-posthook --agent-summary-file /path/to/agent-summary.json
```

This prevents every session stop from creating a Git commit.
