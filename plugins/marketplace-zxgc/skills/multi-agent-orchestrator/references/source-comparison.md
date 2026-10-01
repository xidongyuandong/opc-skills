# 设计取舍与公开参考

采用“一个任务编译器 + 薄层 DAG 调度器”，避免重复维护模型策略。主代理负责语义拆解与验收，脚本负责校验范围、依赖、所有权、重试次数和上下文长度。

参考的机制如下；这些项目不是运行时依赖，也没有将其第三方源码整包纳入：

- [独立代理派工](https://github.com/obra/superpowers/tree/main/skills/dispatching-parallel-agents)：限制上下文，形成可独立验收的输出。
- [子代理开发](https://github.com/obra/superpowers/tree/main/skills/subagent-driven-development)：区分实现完成与接受结果。
- [团队组成](https://github.com/wshobson/agents/tree/main/plugins/agent-teams/skills/team-composition-patterns)：选择足够完成任务的最小团队。
- [GSD 编排器](https://github.com/gsd-build/gsd-2/tree/main/gsd-orchestrator)：显式记录阻塞状态。

小任务仍由主代理直接完成。没有配对质量评测和完整用量证据时，不宣称某方案客观最强，也不宣称节省了 token。
