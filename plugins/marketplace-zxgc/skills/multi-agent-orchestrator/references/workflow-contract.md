# 工作流输入与状态合同

按仓库 README 将四个技能安装为同级目录。需要 Python 3.9+；运行脚本仅使用标准库，编译器测试另需 pytest。

## 独立身份与授权

使用 engineer-router 为当前规范化工作区生成独立的 `product_context`，调用 `orchestrate.py` 时另外传入该上下文及 `active_module_key`。不得从待恢复工作流自身提取预期身份，以免自证归属。

顶层字段必须恰好包含：`product_context`、`active_module_key`、`confirmed`、`available_models`、`capacity`、`tasks`、`state`。

- `confirmed` 必须反映真实授权；样例不代表批准。
- `available_models` 必须来自当前原生工具实际支持的模型，不能直接使用供应商模型目录。
- `capacity` 包含主代理占用，`root_slots` 必须为 1。

## 任务字段

每个任务包含 `id`、`kind`、`difficulty`、`risk`、`goal`、`dependencies`、`allowed_files`、`evidence_refs`、`acceptance`、`constraints`。

- `kind`：planning / implementation / evaluation / research / query。
- `difficulty`：low / medium / high；`risk`：low / high。
- 文件路径必须是工作区内的绝对路径，父目录必须存在。只有 implementation 任务可以指定写入文件。
- 拒绝软链接越界、重复 ID、缺失依赖和依赖环。
- 目标、验收和约束使用清楚的简体中文，字段名与必要技术标识保留英文。

## 状态与单写责任

`state` 必须与所有任务一一对应；每项包含 `status`、`accepted`、`attempts`、`failure_reason`、`usage`。

- `status` 为 pending / running / passed / failed。
- 只有 passed 状态才能 `accepted=true`；接受结果必须经过主代理审阅。
- failed 必须填写失败原因；passed 的失败原因必须为空。
- `usage` 为 null，或实测累计的 `{input_tokens, output_tokens}`。

只有主代理可以更新状态。派工前标记 running 并增加 attempts；失败调用也计入次数。主代理审阅后才能将失败任务改回 pending 重试，不清零 attempts，不丢弃证据。running 任务不重复派发。

未经接受的结果不能释放下游依赖。读写冲突使当前波次串行；必须通过显式依赖说明读取者需要修改前还是修改后的内容。

## 输出边界

调度器只输出建议：不调用模型、不写状态、不启动后台任务、不自动重试、不提供操作系统锁，也不强制执行费用预算。使用 `spawn_args` 前需检查当前原生工具兼容性，不支持的参数交回主代理处理。

生成的 Markdown 以简体中文解释状态和行动，必要字段及状态标签可保持英文。仓库中的 `docs/multi-agent-setup.md` 提供未确认的合成示例；不能用该示例代替真实任务授权。
