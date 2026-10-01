# 配置多智能体协作

本可选技能包提供规划与执行交接、限定范围的模型分工、依赖波次、重试状态保留和主代理验收。脚本本身不启动模型。真实并行执行需要支持原生委派的 Codex 环境；工具或模型不受支持时，任务交回主代理。把技能文件复制到其他应用，不等于该应用支持相同的原生参数。

所有 Markdown 产物以简体中文作为主要说明语言；必要的术语、字段名、命令和链接可保持英文。

## 将四个技能安装为同级目录

从 `plugins/marketplace-zxgc/skills/` 将以下目录复制到所选技能根目录：`engineer-router`、`requirement-to-plan`、`code-exec`、`multi-agent-orchestrator`。

保留目录名和随附的脚本、参考说明及测试。更新前备份已有安装并审阅差异；本包没有自动覆盖用户技能的安装器。仅在仓库内试用时，可直接使用当前目录。需要 Python 3.9+。

执行入口只保留 code-exec。原有规划和执行技能仍可单独使用；启用本协作模式时，需安装完整四技能集合。本包不安装全局 AGENTS、hook、供应商服务或凭证。

## 配置模型

编辑已安装副本中的 `code-exec/references/tiered-execution-policy.json`：

- `strong`：主代理职责档位，不会自动切换当前主代理模型。
- `worker`：限定范围的实现任务，填写当前工具支持且能力足够的模型 ID。
- `scout`：限定范围的只读取证，填写当前工具支持且成本合适的模型 ID。
- `max_attempts`：包含失败调用在内的总尝试次数，默认 2。
- `max_context_chars`：序列化输入的字符上限，不是 token 或费用统计。

随附模型 ID 均为占位符，不能发送给供应商。应根据当前工具填写 `available_models`，并核验其是否支持 `model`、`agent_type=default`、`reasoning_effort=medium` 和 `fork_turns=none`。不支持的参数交回主代理处理，不得静默切换供应商。本包不创建原生角色；路由器给出的角色标签仅表示建议职责。

## 可复现的只读演练

在仓库根目录运行以下命令，示例中的 shell 变量仅用于本次调用：

```bash
skills_root="$PWD/plugins/marketplace-zxgc/skills"
python3 "$skills_root/engineer-router/scripts/route_engineer_task.py" \
  'Inspect two independent documentation files' --workspace "$PWD" \
  --product-line shared > /tmp/opc-example-context.json
python3 "$skills_root/multi-agent-orchestrator/scripts/make_example.py" \
  --context /tmp/opc-example-context.json --model your-scout-model \
  > /tmp/opc-example-workflow.json
python3 "$skills_root/multi-agent-orchestrator/scripts/orchestrate.py" \
  --workflow /tmp/opc-example-workflow.json \
  --product-context /tmp/opc-example-context.json \
  --active-module-key example-collaboration --format json
```

示例刻意保持未确认：预期输出 blocked 和空波次，退出码为 2，不产生可派发任务。只有获得真实授权后，才能配置实际模型 ID、核验文件范围和运行时容量、设置 `confirmed=true` 并重新计算。不得将样例视为授权。

主代理在派工前登记 running 并增加 attempts，且独自负责写入状态。前置任务同时满足 passed 和 accepted 才能释放下游。恢复已有 running 任务，不重新派发；未知用量继续标记 unknown。

## 不调用模型的验证

```bash
python3 -m pytest plugins/marketplace-zxgc/skills/engineer-router/tests \
  plugins/marketplace-zxgc/skills/code-exec/tests \
  plugins/marketplace-zxgc/skills/requirement-to-plan/tests \
  plugins/marketplace-zxgc/skills/multi-agent-orchestrator/tests
```

测试证明确定性合同成立，不证明 LLM 质量或 token 节省。真实工具烟测及配对用量评测需在使用者环境进行。仓库旧版 `validate-pack.sh` 可能因缺失既有 marketplace 文件而中止；本包不补建这些无关文件，也不宣称整包安装已验证。

回滚时恢复已备份的四个技能目录，或回退发布 PR。已有任务状态和证据应保留，以便审计与恢复。
