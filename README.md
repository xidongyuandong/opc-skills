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

下面按当前仓库文件区分可用技能与历史清单。安装并让客户端发现技能后，可引用技能名并提供表中输入；具体参数以对应 SKILL.md 为准。每项介绍（不含技能名）不超过100字。

### 当前仓库包含的技能

| 技能 | 功能价值与用法 |
|---|---|
| [engineer-router](plugins/marketplace-zxgc/skills/engineer-router/SKILL.md) | 绑定项目工作区并建议职责，减少跨项目误操作；提供任务、项目标识和工作区路径调用。 |
| [requirement-to-plan](plugins/marketplace-zxgc/skills/requirement-to-plan/SKILL.md) | 将模糊需求整理为可验收计划，减少返工；提供需求文件或目标，比较方案并生成待办。 |
| [code-exec](plugins/marketplace-zxgc/skills/code-exec/SKILL.md) | 按已确认计划实现、测试和审查，控制改动范围；提供计划及执行授权，输出结果证据。 |
| [multi-agent-orchestrator](plugins/marketplace-zxgc/skills/multi-agent-orchestrator/SKILL.md) | 按依赖与文件冲突安排协作，保留重试和验收；提供任务工作流及独立上下文，计算执行波次。 |
| [self-improvement-session](plugins/marketplace-zxgc/skills/self-improvement-session/SKILL.md) | 复盘任务并归档可复用经验，减少重复错误；提供结果或纠偏记录，行为规则变更另行确认。 |
| [marketplace-zxgc](plugins/marketplace-zxgc/skills/marketplace-zxgc/SKILL.md) | 维护技能包、目录和安装约定，保持兼容；在克隆仓库中提出更新、同步或校验需求。 |
| [clash-verge-add-static-ip](plugins/marketplace-zxgc/skills/clash-verge-add-static-ip/SKILL.md) | 创建独立静态IP订阅并核验出口；提供原配置路径和代理资料，与核心技能一起安装。 |
| [clash-verge-static-ip](plugins/marketplace-zxgc/skills/clash-verge-static-ip/SKILL.md) | 构建静态出口链与刷新扩展，减少更新丢失；提供配置和代理资料，先生成候选再验证。 |

### 历史清单（当前仓库未提供）

以下名称保留自原 README，介绍依据历史技能目录；当前没有对应发布目录，不能从本仓库直接安装，也未验证其运行效果。需先获取匹配实现，不要将历史能力视为当前可用功能。

| 技能 | 功能价值与用法 |
|---|---|
| `session-self-improvement` | 复盘会话并筛选规则、记忆或技能改进；补齐对应技能后，提供会话记录或改进想法。 |
| `session-self-improvement-eval` | 检查复盘摘要和交付质量，发现遗漏；补齐技能后，提供复盘产物及验收依据。 |
| `twin-agent-zyy` | 维护特定个人助手的目标与决策记忆；补齐技能并适配身份后，提供目标和历史决策。 |
| `continuous-agent-loop` | 管理长任务循环、检查点和恢复，减少中断丢失；补齐技能后，提供目标、停止条件和状态。 |
| `enterprise-agent-ops` | 管理长期代理的监控和运行边界；补齐技能后，提供部署环境、运行指标和运维目标。 |
| `self-improving-agent` | 兼容旧版自我改进入口，避免重复流程；补齐技能后，将实质复盘交给会话改进技能。 |
| `continuous-learning-v2` | 从会话提取带置信度的经验候选，积累项目知识；补齐技能后，提供会话证据和项目范围。 |
| `codex-hooks` | 设计、迁移和排查钩子，统一事件自动化；补齐技能后，提供目标事件、配置和预期动作。 |
| `codex-hook` | 创建或修复单个钩子，缩小排障范围；补齐技能后，提供钩子脚本、配置及错误信息。 |
| `codex-remote-container` | 配置远程容器中的Codex，隔离开发环境；补齐技能后，提供连接方式及容器配置。 |
| `codex-ssh-remote-config` | 配置SSH远程Codex及网络环境；补齐技能后，提供主机、目录和登录状态，定位连接问题。 |
| `c250` | 通过本地封装操作指定容器，支持同步和远程执行；补齐技能并适配容器后提供操作目标。 |
| `algorithm-engineer-workflow` | 统筹数据、训练和评测诊断，明确改进路径；补齐技能后，提供模型目标、代码和实验记录。 |
| `algorithm-data-diagnosis` | 检查数据质量、标签和泄漏，降低训练偏差；补齐技能后，提供样本、字段定义及异常表现。 |
| `algorithm-tensorboard-analysis` | 分析损失、奖励等训练曲线，判断收敛问题；补齐技能后，提供事件文件和实验背景。 |
| `algorithm-training-debug` | 排查训练报错、显存不足和数值异常；补齐技能后，提供脚本、配置、日志与复现步骤。 |
| `algorithm-training-review` | 审查训练流程、指标和检查点，发现改进项；补齐技能后，提供实验产物与目标。 |
| `algorithm-rl-debug` | 诊断强化学习奖励、KL和采样异常；补齐技能后，提供算法配置、轨迹和训练日志。 |
| `algorithm-eval-diagnosis` | 定位评测失败、得分回退和基准漂移；补齐技能后，提供样本、评分逻辑及前后结果。 |
| `algorithm-eval-closure` | 核对评测问题是否闭环，明确未完成项；补齐技能后，提供日志、验证结果和问题清单。 |
| `algorithm-agent-trace-analysis` | 分析工具调用与代理轨迹，定位循环或协议故障；补齐技能后，提供脱敏轨迹和失败样例。 |
| `kg-code` | 构建并查询代码图谱，加快定位和影响分析；补齐技能后，指定仓库索引或输入查询。 |
| `agent-memory-mcp` | 提供持久记忆服务，支持跨会话检索；补齐服务与技能后，在目标机器配置MCP连接。 |
| `task2zxgc` | 将会话整理为结构化报告，便于审阅追溯；补齐技能后先预览脱敏报告，获授权再推送。 |

通用的规划、执行与复盘链路打包为以下技能：

1. `requirement-to-plan`：将模糊需求或文档驱动的工作转化为一份需要确认后执行的计划与待办。
2. `code-exec`：通过限定范围的实现、验证和证据收尾，执行此前已确认的计划与待办。
3. `self-improvement-session`：归档事实性经验，并起草会影响行为的改进建议，不在未告知的情况下修改规则、技能、角色、记忆或知识库。

这三个技能是可移植的衍生版本，有意排除了特定机器的绝对路径、私有仓库引用、组织特定工作流和特定领域示例。

以下为历史打包与同步设计说明，不代表当前分支已包含相应技能或安装脚本。

`task2zxgc` 保留在技能市场本地，作为唯一真源，默认不同步到 `~/.codex/skills`。
`kg-code` 用于跨仓库代码图谱的创建和查询，按需显式同步，默认不同步。其辅助工具可从本技能包自动安装缺失的依赖技能；打包 `c250` 是为了支持这条按需启用的依赖路径，它不属于默认同步集。
`agent-memory-mcp` 随附 MCP 服务端源码，但需按需启用，因为安装会向目标机器本地的 `config.toml` 写入 MCP 配置块。请在每台目标机器上使用 `plugins/marketplace-zxgc/scripts/install-agent-memory-mcp.sh`。

技能同步会将被替换的技能备份到 `$CODEX_HOME/backups/skills/<timestamp>/`，并将已知废弃的技能占位目录移出当前启用的技能目录。

## Clash Verge 静态 IP 订阅

`clash-verge-add-static-ip` 先检测 Clash Verge 安装情况；未安装时引导使用官方渠道安装，无法判断时询问自定义路径，复检后再收集配置绝对路径及静态代理的协议、端点、认证和地区。新订阅名称由原订阅名称和静态 IP 地区组成。
远程订阅使用专属脚本以保留刷新后的自定义设置；本地订阅是独立快照。图形界面登记、运行态选择和实时出口验证是独立的完成检查。

只需将以下一个自包含目录安装到智能体的技能目录下：

```bash
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
cp -R plugins/marketplace-zxgc/skills/clash-verge-add-static-ip "${CODEX_HOME:-$HOME/.codex}/skills/"
```

上述命令适用于全新安装。如果目标目录已存在，请先检查并备份。构建器、模板与回归均已内置，无需相邻技能或运行时下载核心代码。Python 3.9+ 用于只读安装探测，Ruby 用于构建器，Node.js 用于 sidecar 合成及回归。默认同步设置不变。

旧双目录版本用户请按[迁移说明](plugins/marketplace-zxgc/skills/clash-verge-add-static-ip/references/migration.md)操作：备份两目录、单独验证新版、更新旧脚本路径，再检查自己的调用方并决定是否移除旧技能。本操作不会自动删除用户已安装的文件。

示例：“使用 `$clash-verge-add-static-ip`，读取我的配置文件绝对路径和私有供应商参考文件。创建一个新加坡订阅，但不要切换我当前的连接。”

在仓库根目录运行离线验证：

```bash
python3 -m unittest discover -s plugins/marketplace-zxgc/skills/clash-verge-add-static-ip/tests -v
```

测试会隔离复制这一个技能，运行两套核心回归及合成安装状态测试；不能证明三平台真实安装、应用启动、图形界面登记、供应商可访问、实际公网出口身份或 IP 长期稳定。探测器不会执行发现的二进制，文件证据也不是发行者身份鉴真。
刷新时的名称冲突必须对照下载的源配置检查；当前核心逻辑不会自动拒绝此类冲突。绝不向本仓库加入真实配置文件、订阅 URL、凭证或生成的私有 sidecar 文件。

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
