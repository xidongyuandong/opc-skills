# task2zxgc 多主题报告机制

## 核心主张

`task2zxgc` 面向长 Codex 会话时，不能由 Agent 主观挑选一个“重点主题”生成单篇报告；正确机制是先判断会话是否能被一个核心主张统摄，不能统摄时用 `reports[]` 拆成最少数量的独立报告，并一次性渲染、提交全部 Markdown。

## 背景

`task2zxgc` 用于把当前 Codex 会话总结成任务报告并推送到任务管理 Git 仓库。早期实现只接受单个 Agent summary JSON object，脚本一次只生成一个 Markdown。这个设计在短会话里足够，但长会话通常同时包含远端评测、插件开发、配置治理、技能创建、仓库修复等多条独立链路。

一次实际使用中，Agent 把报告聚焦到“后续新增的 Codex 自改进与约束体系”，遗漏了同一长会话中的 c250 评测、marketplace 跨机器安装、algorithm skills PR 等独立主题。用户明确纠正：如果会话很长或包含多个主题，应该拆分后提交多个报告，不能只处理片面信息。

## 主题拆分规则

生成报告前必须先做主题判断：

- 如果一个句子能完整表达整段会话的对象、判断、价值和边界，则保留单报告。
- 如果会话包含彼此独立的排障、功能实现、技术决策、仓库梳理、通用工作流或算法方向链路，则拆分为多报告。
- 拆分数量取最小值，相关内容应合并，不应为了形式过度拆分。
- 每篇报告必须能独立阅读，不依赖其他报告才能理解背景、需求、执行过程和结果。
- 每篇报告只服务一个核心主张，并保留对应证据边界：会话事实、Agent 推断和后续建议要区分。

## 实现入口

相关文件：

- `plugins/marketplace-zxgc/skills/task2zxgc/SKILL.md`
- `plugins/marketplace-zxgc/skills/task2zxgc/scripts/task2zxgc.py`

`SKILL.md` 中已经写入单报告和多报告 schema。单主题继续使用原来的 JSON object；多主题使用：

```json
{
  "reports": [
    {
      "task_title": "主题一短标题",
      "task_theme": "围绕一个核心主张总结主题一。",
      "core_requirement": "主题一核心需求。",
      "raw_requirements": ["主题一相关用户输入摘要"],
      "execution_process": ["主题一执行过程"],
      "completed_tasks": ["主题一完成事项"],
      "execution_result": ["主题一结果"],
      "improvement_points": ["主题一待优化点"],
      "diagnostics": [],
      "evidence": ["主题一证据"]
    }
  ]
}
```

脚本关键函数：

- `agent_reports()`：兼容单 object、`reports[]` 和 `summaries[]`，并校验多报告列表非空且元素为 object。
- `render_markdown()`：仍负责单篇报告渲染。
- `report_relative_path()`：为多篇报告生成唯一文件名，避免同一小时、同名标题覆盖。
- `commit_and_push_many()`：一次 `git add` 多个报告并用一个 commit 推送。

## 验证方式

结构验证：

```bash
python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py \
  plugins/marketplace-zxgc/skills/task2zxgc
python3 -m py_compile \
  plugins/marketplace-zxgc/skills/task2zxgc/scripts/task2zxgc.py
```

多报告 dry-run 验证：

```bash
python3 plugins/marketplace-zxgc/skills/task2zxgc/scripts/task2zxgc.py \
  --dry-run \
  --agent-summary-file /path/to/multi-report-summary.json |
  rg -n '^<!-- task2zxgc report|^# '
```

预期输出应出现多个 `<!-- task2zxgc report X/N -->` 标记和多个一级标题。一次实测中，4 主题 JSON 成功渲染为：

- `c250评测执行与监控闭环`
- `marketplace跨机器安装与算法技能PR`
- `Codex约束自改进与恢复点`
- `task2zxgc多主题报告修复`

## 维护注意事项

- 不要重新引入“只生成单报告”的隐式假设；任何新校验、posthook 或 UI 包装都必须保留 `reports[]` 能力。
- 不要把主题拆分写成流水账分段。拆分依据是独立技术主张，不是时间顺序。
- 不要把长工具输出、原始聊天记录、token、cookie、私钥、认证 header 或机器个性化路径写进报告。
- 不写入与报告主题无关的临时进度、纯连接状态、重复命令输出、未验证猜测和只对当前机器有效的个性化配置。
- 若未来增加自动化校验，优先检查每个 report 是否包含 `task_title`、`task_theme`、`core_requirement`、`execution_result`、`diagnostics` 和 `evidence`。
- 若要为同一长会话生成报告索引，可在报告仓库增加 index 文件，但不能替代每篇独立报告。

## 使用检查清单

下一次维护或调用 `task2zxgc` 时，按这个流程检查：

- 先问：整段会话能否用一个核心主张解释清楚；如果不能，必须使用 `reports[]`。
- 再分：每个 report 是否对应一个独立读者任务，例如排障、实现、决策、仓库梳理或算法方向。
- 再查：每个 report 是否有可追溯 evidence，而不是只写 Agent 结论。
- 再排除：是否已经删除 raw chat log、长工具输出、认证信息、个性化路径和无关进度。
- 再验证：`--dry-run` 是否输出预期数量的报告标题，`--push` 是否一次提交全部 Markdown。
- 最后回看：报告是否能被未来维护者直接用于理解问题、复现判断、继续实现或定位风险。

## 后续优化

- 增加 `--validate-agent-summary`，在 push 前校验单报告或 `reports[]` 的必填字段、诊断结构和证据摘要。
- 在 `--dump-context` 输出中增加主题候选草案，帮助 Agent 少漏主题。
- 对多报告 push 返回更明确的 GitLab blob URL 列表，减少用户手动拼接链接。
