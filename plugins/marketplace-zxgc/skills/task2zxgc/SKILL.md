---
name: task2zxgc
description: Summarize the current Codex session into a task report and push it to the ai-coding-zxgc-managment GitLab repository.
version: 1.0.0
---

# task2zxgc

Use this skill when the user runs `/task2zxgc` or asks to export the current Codex session as a task summary.

## Behavior

The skill generates a Markdown report from the current full Codex session and pushes it to:

`https://gitlab.chehejia.com/ep/ai/ai-coding-zxgc-managment.git`

The output path in that repository is:

`{username}/{YYYY-MM-DD-HH}-{task-title}.md`

The report includes:

- 任务主题
- 需求描述
- 任务执行过程
- 完成的任务
- 执行结果
- 需求描述中的待优化点, summarized by the Agent instead of copied from raw prompts or tool logs
- 全方位诊断
- 会话证据摘要

## Manual Run

When the user invokes `/task2zxgc`, use the Agent-based flow. First dump the session context:

```bash
python3 $HOME/marketplace-zxgc/plugins/marketplace-zxgc/skills/task2zxgc/scripts/task2zxgc.py --dump-context
```

Then, as the Codex Agent, synthesize a JSON object with this shape:

```json
{
  "task_title": "任务051902",
  "task_theme": "用一段话说明此次任务的核心目标。",
  "core_requirement": "对原始需求描述的核心摘要。",
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

Use `$AI_INSIGHTS_REPO` as the diagnostic reference. Its useful patterns for this skill are: stable friction taxonomy, attribution/severity/confidence, effective patterns, outcome guidance, prompt-quality dimensions, and evidence sidecar thinking.

`reference_points_ai_insights` is injected by `--dump-context` as internal Agent guidance. Do not render it as a final report section. The final report should show its effect through better `core_requirement`, `raw_requirements`, `completed_tasks`, `execution_result`, `improvement_points`, and `diagnostics`.

`requirements` is a compatibility field. Prefer `core_requirement` and `raw_requirements` when generating new Agent summaries.

Finally push with the Agent-generated summary:

```bash
python3 $HOME/marketplace-zxgc/plugins/marketplace-zxgc/skills/task2zxgc/scripts/task2zxgc.py --push --agent-summary-file /path/to/agent-summary.json
```

Do not run `--push` without an Agent summary. The script refuses that by default so production reports do not fall back to rule-based extraction.

For validation without GitLab side effects, run:

```bash
python3 $HOME/marketplace-zxgc/plugins/marketplace-zxgc/skills/task2zxgc/scripts/task2zxgc.py --dry-run --agent-summary-file /path/to/agent-summary.json
```

## Posthook Mode

The Codex `Stop` hook is configured to call:

```bash
python3 $HOME/marketplace-zxgc/plugins/marketplace-zxgc/hooks/task2zxgc_posthook.py --event Stop
```

The posthook is intentionally idle by default. It only pushes when a pending marker exists, which can be created with:

```bash
python3 $HOME/marketplace-zxgc/plugins/marketplace-zxgc/skills/task2zxgc/scripts/task2zxgc.py --request-posthook --agent-summary-file /path/to/agent-summary.json
```

This prevents every session stop from creating a Git commit.
