---
name: engineer-router
description: 在编译任务契约或恢复工作流前，将任务绑定到明确的项目工作区，并建议通用工程角色。
---

# 可移植工程路由器

任务需要按项目范围交接给 `code-exec` 或 `multi-agent-orchestrator` 时，使用本技能。独立生成 `product_context` 和 `primary_role`：项目与工作区身份约束恢复和文件引用，角色只是建议标签，不表示已安装对应运行时角色。

本技能生成的 Markdown 文档默认使用简体中文。字段名、代码标识、命令、必要术语和链接保持原样；用户明确要求其他语言时遵从用户要求。

## 工作流程

1. 确定目标工作区已存在，并提供明确的项目标识。标识允许字母、数字、`_`、`.` 和 `-`，最多 128 个字符。默认标识为 `shared`，不授予工作区外访问权限。
2. 在本技能目录运行路由器，将工作区替换为实际路径：

   ```bash
   python3 scripts/route_engineer_task.py --task "审查数据集导入器" \
     --product-line sample-project --workspace /absolute/project > route.json
   ```

3. 检查结果，将完整的 `product_context` 传入契约与工作流。为恢复操作保留独立获取的预期上下文；禁止用待恢复记录本身作为预期身份的依据。
4. 恢复校验时另行传入预期模块标识。上下文缺失、项目或工作区身份变化、模块不一致，都会阻止恢复。
5. 交接任务前校验明确的绝对文件路径。解析符号链接后，文件必须仍位于规范工作区内。现有目录、特殊文件、相对路径以及父目录不存在的路径均被拒绝。

## 公开范围与限制

这是功能收敛的独立公开路由器，不包含私有项目注册表、特定业务角色路由、历史导入、全局资产发现或自动安装能力。项目名称与角色建议不代表已经验证所有权。调用方显式绑定身份，任务文本中的关键词仅用于建议角色。

脚本不启动子代理、不调用模型 API、不选择模型、不执行 shell 命令、不创建归档、不授予权限，只向标准输出打印 JSON。重定向输出是调用方明确执行的操作。模型可用性与执行授权由调用方负责。

这些检查属于工作流校验，不是操作系统沙箱。它们不能阻止后续文件系统变化、硬链接别名、任意执行代码或检查与使用之间的竞态。执行前应重新校验，对不可信工作负载应使用真实沙箱。不同项目共享工作区时仍共享文件系统；需要文件系统隔离时，应使用独立工作区。

## Python 兼容接口

`scripts/product_scope.py` 提供 `resolve_context`、`validate_context`、`validate_recovery`、`validate_execution_paths` 和 `load_context`。即使省略 `require_workspace`，所有公开上下文仍要求工作区已存在且采用规范路径。`load_context` 接受直接的上下文对象，或包含 `product_context` 的 JSON 对象。

运行针对性检查：

```bash
python3 -m unittest discover -s tests -v
```
