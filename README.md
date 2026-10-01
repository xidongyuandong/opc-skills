# opc-skills

**简体中文** | [English](README.en.md)

OPC 本地 Codex 技能市场。

本仓库将 OPC 个人级、用户级 Codex 资源打包为技能市场：

- `plugins/marketplace-zxgc/skills/`：精选自定义技能
- `plugins/marketplace-zxgc/templates/`：AGENTS.md、规则和配置模板
- `plugins/marketplace-zxgc/hooks/`：钩子脚本
- `plugins/marketplace-zxgc/scripts/`：安装、同步和验证脚本
- `.agents/plugins/marketplace.json`：技能市场目录清单

本仓库采用本地优先原则。请勿添加认证文件、令牌、Cookie、私钥或原始凭证输出。

## 旧版运行时名称

本公开仓库以 `opc-skills` 为名发布。部分运行时标识有意保持旧版兼容：

- 本地源码目录示例仍可能使用 `marketplace-zxgc`；
- 插件和技能路径仍可能使用 `plugins/marketplace-zxgc`；
- 继续支持 `MARKETPLACE_ZXGC_HOME`、`ZXGC_SKILLS` 等环境变量；
- 为保持兼容，`task2zxgc` 应用名称保持不变。

在没有独立迁移计划的情况下，请勿重命名这些运行时标识。

## 在其他机器上安装

分步指南涵盖克隆、验证、技能市场注册、技能同步、AGENTS.md、规则、钩子、核验、升级和回滚，详见 [docs/install-on-other-machines.md](docs/install-on-other-machines.md)。

当前中文版自动安装指南见[操作指导.md](操作指导.md)。推荐团队使用以下入口：

```bash
"$MARKETPLACE_ZXGC_HOME/scripts/install-marketplace-zxgc.sh" --dry-run
"$MARKETPLACE_ZXGC_HOME/scripts/install-marketplace-zxgc.sh" --apply
```

已打包技能及其适用场景的中文概览见[技能介绍.md](技能介绍.md)。

需要快速了解本技能市场的维护者和智能体可参考：

- [docs/marketplace-architecture.md](docs/marketplace-architecture.md)：梳理清单文件、技能、脚本、模板、钩子、工具、验证及同步流程。
- [docs/skills-catalog.md](docs/skills-catalog.md)：列出每个已打包技能、用途，以及它是默认同步还是按需启用。
- [docs/marketplace-standards-gap.md](docs/marketplace-standards-gap.md)：对比本地技能市场与公开技能市场模式，记录尚未补齐的发布差距。

## 注册到 Codex

```bash
codex plugin marketplace add "$HOME/marketplace-zxgc"
```

修改后升级：

```bash
codex plugin marketplace upgrade marketplace-zxgc
```

## 验证

```bash
"$HOME/marketplace-zxgc/plugins/marketplace-zxgc/scripts/validate-pack.sh"
```

## 提交更新

旧版内部仓库的远端地址为：

```bash
https://gitlab.chehejia.com/zhengyuyu/marketplace-zxgc.git
```

以下流程会验证本地技能市场改动、创建分支、提交、推送，并创建 GitLab 议题或合并请求（MR）：

```bash
"$HOME/marketplace-zxgc/scripts/auto-submit-marketplace-change.sh" --dry-run --title "update marketplace"
"$HOME/marketplace-zxgc/scripts/auto-submit-marketplace-change.sh" --apply --title "update marketplace"
```

脚本根据自身路径定位仓库根目录，按内容推导分支名，并使用已打包的 `code-refactor` 自动创建合并请求辅助工具。GitLab 认证可使用以下任一方式：

- 在 Shell 中导出 `GITLAB_PERSONAL_ACCESS_TOKEN` 或 `GITLAB_TOKEN`。
- 将 `MARKETPLACE_ZXGC_ENV_FILE` 指向包含上述任一变量的本地环境文件。
- 将本地环境文件存放在 `$HOME/.config/marketplace-zxgc/env` 或 `$HOME/.marketplace-zxgc.env`。
- 为 GitLab 远端配置 Git 凭证助手。

请勿提交本地环境文件、令牌、Cookie、私钥或原始凭证输出。

如果只需提交并推送当前分支，可使用以下简化备用方式：

```bash
"$HOME/marketplace-zxgc/scripts/push-marketplace.sh"
```

## 安全安装操作

预览技能同步：

```bash
"$HOME/marketplace-zxgc/plugins/marketplace-zxgc/scripts/sync-skills.sh" --dry-run
```

预览 AGENTS.md 安装：

```bash
"$HOME/marketplace-zxgc/plugins/marketplace-zxgc/scripts/install-agents-md.sh" --mode replace
```

预览钩子安装：

```bash
"$HOME/marketplace-zxgc/plugins/marketplace-zxgc/scripts/install-hooks.sh" --dry-run
```

预览规则安装：

```bash
"$HOME/marketplace-zxgc/plugins/marketplace-zxgc/scripts/install-rules.sh" --dry-run
```

规则模板经过筛选，用于可移植的用户级行为规范。本地绝对路径和特定仓库命令应保留在本地配置中，或在打包前改写为可复用的指导。

## 包含的技能

初始技能包包含：

- `requirement-to-plan`
- `code-exec`
- `self-improvement-session`
- `marketplace-zxgc`
- `session-self-improvement`
- `session-self-improvement-eval`
- `twin-agent-zyy`
- `continuous-agent-loop`
- `enterprise-agent-ops`
- `self-improving-agent`
- `continuous-learning-v2`
- `codex-hooks`
- `codex-hook`
- `codex-remote-container`
- `codex-ssh-remote-config`
- `c250`
- `algorithm-engineer-workflow`
- `algorithm-data-diagnosis`
- `algorithm-tensorboard-analysis`
- `algorithm-training-debug`
- `algorithm-training-review`
- `algorithm-rl-debug`
- `algorithm-eval-diagnosis`
- `algorithm-eval-closure`
- `algorithm-agent-trace-analysis`
- `kg-code`
- `agent-memory-mcp`
- `task2zxgc`

通用的规划、执行与复盘链路打包为以下技能：

1. `requirement-to-plan`：将模糊需求或文档驱动的工作转化为一份需要确认后执行的计划与待办。
2. `code-exec`：通过限定范围的实现、验证和证据收尾，执行此前已确认的计划与待办。
3. `self-improvement-session`：归档事实性经验，并起草会影响行为的改进建议，不在未告知的情况下修改规则、技能、角色、记忆或知识库。

这三个技能是可移植的衍生版本，有意排除了特定机器的绝对路径、私有仓库引用、组织特定工作流和特定领域示例。

`task2zxgc` 保留在技能市场本地，作为唯一真源，默认不同步到 `~/.codex/skills`。
`kg-code` 用于跨仓库代码图谱的创建和查询，按需显式同步，默认不同步。其辅助工具可从本技能包自动安装缺失的依赖技能；打包 `c250` 是为了支持这条按需启用的依赖路径，它不属于默认同步集。
`agent-memory-mcp` 随附 MCP 服务端源码，但需按需启用，因为安装会向目标机器本地的 `config.toml` 写入 MCP 配置块。请在每台目标机器上使用 `plugins/marketplace-zxgc/scripts/install-agent-memory-mcp.sh`。

技能同步会将被替换的技能备份到 `$CODEX_HOME/backups/skills/<timestamp>/`，并将已知废弃的技能占位目录移出当前启用的技能目录。

## Clash Verge 静态 IP 订阅

`clash-verge-add-static-ip` 收集 Clash Verge 配置文件的绝对路径，以及静态代理的协议、端点、认证信息和地区，然后指导创建独立订阅，订阅名称由原订阅名称和静态 IP 地区组成。
远程订阅使用针对该配置的专用脚本，使自定义设置在刷新后仍然保留；本地订阅是独立快照。图形界面注册和实时出口验证是两项独立的完成检查。

将以下两个同级目录都安装到智能体的技能目录下：

```bash
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
cp -R plugins/marketplace-zxgc/skills/clash-verge-add-static-ip "${CODEX_HOME:-$HOME/.codex}/skills/"
cp -R plugins/marketplace-zxgc/skills/clash-verge-static-ip "${CODEX_HOME:-$HOME/.codex}/skills/"
```

这些复制命令适用于全新安装。如果任一目标目录已经存在，更新前请先检查并备份。上述操作不改变默认同步设置。
第二个目录提供共享构建工具和模板，仅安装入口技能并不足够。构建工具需要 Ruby；离线 sidecar 测试使用 Node.js。

示例：“使用 `$clash-verge-add-static-ip`，读取我的配置文件绝对路径和私有供应商参考文件。创建一个新加坡订阅，但不要切换我当前的连接。”

离线验证：

```bash
ruby plugins/marketplace-zxgc/skills/clash-verge-static-ip/scripts/test_static_ip_workflow.rb
ruby plugins/marketplace-zxgc/skills/clash-verge-static-ip/scripts/test_sidecar_workflow.rb
```

这些测试使用合成输入，不能证明图形界面注册成功、供应商可访问、实际公网出口身份正确或 IP 长期稳定。刷新时的名称冲突必须对照下载的源配置检查；当前核心逻辑不会自动拒绝此类冲突。
绝不向本仓库加入真实配置文件、订阅 URL、凭证或生成的私有 sidecar 文件。

## 应用：task2zxgc

`task2zxgc` 将当前 Codex 会话导出为结构化任务报告，并推送到配置的报告仓库。报告包含独立的 `用户原始输入` 章节，用于存放经过脱敏的需求文件摘录、命令行提示词和用户聊天消息，便于审查者评估用户是否提供了有效的任务上下文。

默认报告仓库：

```text
https://gitlab.chehejia.com/ep/ai/ai-coding-zxgc-managment.git
```

默认 GitLab 报告 URL 格式：

```text
https://gitlab.chehejia.com/ep/ai/ai-coding-zxgc-managment/-/blob/master/{username}/{YYYY-MM-DD-HH}-{task-title}.md
```

运行时配置保存在每台机器本地：

```bash
export TASK2ZXGC_REPO_URL="https://gitlab.chehejia.com/ep/ai/ai-coding-zxgc-managment.git"
export TASK2ZXGC_REPO_DIR="${CODEX_HOME:-$HOME/.codex}/task2zxgc/ai-coding-zxgc-managment"
export TASK2ZXGC_USERNAME="$(git config user.name 2>/dev/null || whoami)"
```

手动流程：

```bash
TASK2ZXGC_SCRIPT="${MARKETPLACE_ZXGC_HOME:-$HOME/marketplace-zxgc}/plugins/marketplace-zxgc/skills/task2zxgc/scripts/task2zxgc.py"
python3 "$TASK2ZXGC_SCRIPT" --dump-context > /tmp/task2zxgc-context.json
python3 "$TASK2ZXGC_SCRIPT" --dry-run --agent-summary-file /tmp/task2zxgc-summary.json
python3 "$TASK2ZXGC_SCRIPT" --push --agent-summary-file /tmp/task2zxgc-summary.json
```

团队安装、后置钩子用法和凭证说明见 [docs/install-on-other-machines.md](docs/install-on-other-machines.md#9-task2zxgc-应用说明)。

## 多智能体协作技能包

使用 `engineer-router` 绑定明确的任务上下文，`requirement-to-plan` 生成稳定的任务拆解，`code-exec` 在限定范围内执行，`multi-agent-orchestrator` 管理依赖波次和验收。请配置当前工具实际支持的模型 ID。

详见[安装配置、使用边界和只读演练](docs/multi-agent-setup.md)。本可选包不改变默认同步集。Markdown 说明与产物默认使用简体中文，必要术语、字段、命令和链接可保持英文。
