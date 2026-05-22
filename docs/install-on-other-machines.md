# marketplace-zxgc 其他机器安装指南

本文档用于在一台新机器上安装并启用 `marketplace-zxgc`。它不会同步任何凭据、token、cookie、私钥或机器专属配置。

## 作用

`marketplace-zxgc` 是一个本地优先的 Codex 能力包，用来把常用的用户级 Codex 能力集中维护和分发：

- skills：例如 `session-self-improvement`、`code-refactor`、`codex-hook`、`codex-remote-container`。
- AGENTS.md 模板：提供稳定的用户级约束和工作规范。
- rules 模板：提供经过裁剪的安全命令前缀规则。
- hooks：提供学习、复盘、导出等钩子能力。
- 安装/同步脚本：提供 dry-run、备份、校验，避免直接覆盖本机配置。

适用场景：

- 新电脑或远程开发机需要复用同一套 Codex 用户级工作流。
- 多台机器希望共享通用 skills、AGENTS.md、rules、hooks。
- 希望把本机经验沉淀为可维护、可验证、可回滚的 marketplace 资产。

不适用场景：

- 同步本机 secrets、登录态、auth 文件、cookie、API token。
- 原样复制带绝对路径、具体仓库路径、一次性任务命令的本地 rules。
- 覆盖目标机器上尚未备份或尚未审阅的 Codex 配置。

## 前置条件

目标机器需要具备：

- `git`
- `bash`
- `python3`
- `codex` CLI
- 能访问 `https://gitlab.chehejia.com/zhengyuyu/marketplace-zxgc.git`

检查命令：

```bash
git --version
bash --version
python3 --version
codex --version
```

如果 `codex` 不存在，先按当前 Codex 官方安装方式安装或升级 Codex CLI。

如果目标机器的 Codex home 不是默认 `$HOME/.codex`，先设置 `CODEX_HOME`。例如 c250/container250 使用：

```bash
export CODEX_HOME=/data/jenkins/.codex/home
export CODEX_BIN=/data/jenkins/.codex/bin/codex
export MARKETPLACE_ZXGC_HOME=/data/jenkins/marketplace-zxgc
```

普通机器可以使用默认值：

```bash
export CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
export CODEX_BIN="${CODEX_BIN:-codex}"
export MARKETPLACE_ZXGC_HOME="${MARKETPLACE_ZXGC_HOME:-$HOME/marketplace-zxgc}"
```

## 1. 拉取仓库

推荐放在用户目录下，避免使用原机器的绝对路径：

```bash
git clone https://gitlab.chehejia.com/zhengyuyu/marketplace-zxgc.git "$MARKETPLACE_ZXGC_HOME"
cd "$MARKETPLACE_ZXGC_HOME"
```

如果目标机器已配置 GitLab SSH，也可以使用 SSH remote：

```bash
git clone git@gitlab.chehejia.com:zhengyuyu/marketplace-zxgc.git "$MARKETPLACE_ZXGC_HOME"
cd "$MARKETPLACE_ZXGC_HOME"
```

## 2. 校验 marketplace 包

先校验包结构、脚本语法和 skill 基本格式：

```bash
"$MARKETPLACE_ZXGC_HOME/plugins/marketplace-zxgc/scripts/validate-pack.sh"
```

预期看到：

```text
marketplace-zxgc validation passed
```

如果失败，先不要安装。根据报错修复缺失文件、脚本语法或 Codex 版本问题。

## 3. 注册 Codex marketplace

把本地仓库注册为 Codex marketplace：

```bash
"$CODEX_BIN" plugin marketplace add "$MARKETPLACE_ZXGC_HOME"
```

查看是否已注册：

```bash
"$CODEX_BIN" plugin marketplace list
"$CODEX_BIN" plugin list
```

后续仓库更新后，在目标机器执行：

```bash
cd "$MARKETPLACE_ZXGC_HOME"
git pull --ff-only
"$CODEX_BIN" plugin remove marketplace-zxgc@marketplace-zxgc
"$CODEX_BIN" plugin add marketplace-zxgc@marketplace-zxgc
```

说明：local marketplace 更新后，部分 Codex 版本不会通过 `plugin marketplace upgrade` 刷新已安装插件缓存。更稳妥的方式是先 `plugin remove marketplace-zxgc@marketplace-zxgc`，再 `plugin add marketplace-zxgc@marketplace-zxgc`。

## 4. 同步 skills

先 dry-run：

```bash
CODEX_HOME="$CODEX_HOME" "$MARKETPLACE_ZXGC_HOME/plugins/marketplace-zxgc/scripts/sync-skills.sh" --dry-run
```

确认输出符合预期后再应用：

```bash
CODEX_HOME="$CODEX_HOME" "$MARKETPLACE_ZXGC_HOME/plugins/marketplace-zxgc/scripts/sync-skills.sh" --apply
```

默认会同步这些 skills：

```text
marketplace-zxgc session-self-improvement self-improving-agent continuous-learning-v2 code-refactor codex-hooks codex-hook codex-remote-container codex-ssh-remote-config algorithm-engineer-workflow algorithm-data-diagnosis algorithm-tensorboard-analysis algorithm-training-debug algorithm-training-review algorithm-rl-debug algorithm-eval-diagnosis algorithm-eval-closure algorithm-agent-trace-analysis
```

如只想同步一部分：

```bash
ZXGC_SKILLS="marketplace-zxgc session-self-improvement code-refactor" \
  CODEX_HOME="$CODEX_HOME" "$MARKETPLACE_ZXGC_HOME/plugins/marketplace-zxgc/scripts/sync-skills.sh" --apply
```

如希望某些 skill 以软链接方式安装，便于仓库更新后立即生效：

```bash
ZXGC_LINK_SKILLS="marketplace-zxgc code-refactor" \
  CODEX_HOME="$CODEX_HOME" "$MARKETPLACE_ZXGC_HOME/plugins/marketplace-zxgc/scripts/sync-skills.sh" --apply
```

注意：脚本会在覆盖已有 skill 前生成时间戳备份，备份位置是 `$CODEX_HOME/backups/skills/<timestamp>/`。备份不会放在 `$CODEX_HOME/skills` 下，避免旧 skill 被误发现或污染扫描结果。

## 5. 安装 AGENTS.md 模板

AGENTS.md 会影响 Codex 的用户级行为约束。先预览：

```bash
"$MARKETPLACE_ZXGC_HOME/plugins/marketplace-zxgc/scripts/install-agents-md.sh" --mode replace --target "$CODEX_HOME/AGENTS.md"
```

确认后应用：

```bash
"$MARKETPLACE_ZXGC_HOME/plugins/marketplace-zxgc/scripts/install-agents-md.sh" --mode replace --target "$CODEX_HOME/AGENTS.md" --yes
```

原则：

- 只安装通用、稳定、用户级约束。
- 不把具体仓库总结、具体机器路径、临时任务要求写入全局 AGENTS.md。
- 如果目标机器已有重要 AGENTS.md，先阅读备份文件再决定是否迁移差异。

## 6. 安装 rules 模板

rules 会影响 Codex 对命令执行的自动许可判断。先 dry-run：

```bash
CODEX_HOME="$CODEX_HOME" "$MARKETPLACE_ZXGC_HOME/plugins/marketplace-zxgc/scripts/install-rules.sh" --dry-run
```

确认后应用：

```bash
CODEX_HOME="$CODEX_HOME" "$MARKETPLACE_ZXGC_HOME/plugins/marketplace-zxgc/scripts/install-rules.sh" --apply
```

rules 同步原则：

- 可以同步不涉及绝对路径、具体仓库、凭据和一次性任务的通用规则。
- 涉及绝对路径或具体仓库的规则，不直接同步；只抽取指导性信息进入文档或模板。
- 不原样复制本机 runtime rules。

## 7. 安装 hooks

hooks 可能引用本机安装路径，因此必须在目标机器本地生成。先 dry-run：

```bash
CODEX_HOME="$CODEX_HOME" "$MARKETPLACE_ZXGC_HOME/plugins/marketplace-zxgc/scripts/install-hooks.sh" --dry-run
```

确认后应用：

```bash
CODEX_HOME="$CODEX_HOME" "$MARKETPLACE_ZXGC_HOME/plugins/marketplace-zxgc/scripts/install-hooks.sh" --apply
```

应用后重新启动 Codex，使 hooks 配置生效。首次交互式启动时，Codex 可能显示 `Hooks need review`。这不是安装失败，而是 Codex 的 hook 信任机制。人工交互时应先 review，确认 hooks 来源是当前 `marketplace-zxgc` 本地仓库后按提示信任。

自动化 smoke test 可以使用一次性绕过信任选项，但只应在已经校验 hooks 模板和路径后使用：

```bash
CODEX_HOME="$CODEX_HOME" "$CODEX_BIN" exec \
  --dangerously-bypass-hook-trust \
  --skip-git-repo-check \
  --sandbox read-only \
  "只输出 marketplace-zxgc smoke ok"
```

不要把 `--dangerously-bypass-hook-trust` 当作普通日常使用默认值；它只适合受控环境里的安装验证。

## 8. 验证安装结果

检查文件：

```bash
ls "$CODEX_HOME/skills"
test -f "$CODEX_HOME/AGENTS.md" && echo "AGENTS.md installed"
test -f "$CODEX_HOME/rules/default.rules" && echo "rules installed"
test -f "$CODEX_HOME/hooks.json" && echo "hooks installed"
```

检查 Codex 内 skill 是否可用：

```text
$marketplace-zxgc
$session-self-improvement
$code-refactor
```

如果 skill 只被命名而没有明确任务，Codex 应只解释或使用该 skill 处理当前显式任务，不应推断为允许执行无关副作用操作。

## 9. task2zxgc 应用说明

`task2zxgc` 用于把当前 Codex 会话整理为结构化任务报告，并提交到团队任务沉淀仓库。它适合在完成一次实现、排障、调研、代码梳理或流程优化后，把“需求、执行过程、完成结果、待优化点、诊断和证据摘要”沉淀为可检索 Markdown。

默认提交目标：

```text
https://gitlab.chehejia.com/ep/ai/ai-coding-zxgc-managment.git
```

默认文件路径：

```text
{username}/{YYYY-MM-DD-HH}-{task-title}.md
```

报告元信息会把本机 Codex session 路径显示为 `$CODEX_HOME/...` 或 `$HOME/...`，避免把个人机器绝对路径提交到团队仓库。

`username` 默认来自 `TASK2ZXGC_USERNAME`、`TASK2ZXGC_AUTHOR`、`git config user.name` 或系统用户名。团队成员可以在本机显式配置，避免不同机器或容器里用户名不稳定：

```bash
export TASK2ZXGC_REPO_URL="https://gitlab.chehejia.com/ep/ai/ai-coding-zxgc-managment.git"
export TASK2ZXGC_REPO_DIR="$CODEX_HOME/task2zxgc/ai-coding-zxgc-managment"
export TASK2ZXGC_USERNAME="$(git config user.name 2>/dev/null || whoami)"
export AI_INSIGHTS_REPO="${AI_INSIGHTS_REPO:-$HOME/ai-insights}"
```

如果团队使用另一个报告仓库，只改本机 `TASK2ZXGC_REPO_URL` 和 `TASK2ZXGC_REPO_DIR`，不要修改并提交个人配置。

一次完整手动使用流程：

```bash
TASK2ZXGC_SCRIPT="$MARKETPLACE_ZXGC_HOME/plugins/marketplace-zxgc/skills/task2zxgc/scripts/task2zxgc.py"
python3 "$TASK2ZXGC_SCRIPT" --dump-context > /tmp/task2zxgc-context.json
```

把 `/tmp/task2zxgc-context.json` 交给当前 Codex Agent 归纳为 Agent summary JSON。单主题输出一个 JSON object；多主题输出 `{"reports":[...]}`。然后先 dry-run：

```bash
python3 "$TASK2ZXGC_SCRIPT" --dry-run --agent-summary-file /tmp/task2zxgc-summary.json
```

确认报告内容后推送：

```bash
python3 "$TASK2ZXGC_SCRIPT" --push --agent-summary-file /tmp/task2zxgc-summary.json
```

推送成功后，脚本会输出本次生成的本地文件路径；对应 GitLab URL 可按默认仓库和相对路径拼接，例如：

```text
https://gitlab.chehejia.com/ep/ai/ai-coding-zxgc-managment/-/blob/master/{username}/{YYYY-MM-DD-HH}-{task-title}.md
```

如果默认分支不是 `master`，以目标报告仓库实际默认分支为准。

使用 posthook 延迟到 Codex Stop 时执行：

```bash
python3 "$TASK2ZXGC_SCRIPT" --request-posthook --agent-summary-file /tmp/task2zxgc-summary.json
```

posthook 默认空闲，只有存在 `$TASK2ZXGC_STATE_DIR/pending.json` 时才会提交报告。这样不会让每次 Codex 退出都自动产生 Git commit。

GitLab 认证不由 `task2zxgc` 保存。目标机器需要提前配置 Git credential helper、SSH key，或在本机 shell 环境中提供凭据；不要把 token 写入仓库 URL、文档或 committed env 文件。

## 10. 日常使用

常用命令：

```bash
cd "$MARKETPLACE_ZXGC_HOME"
git pull --ff-only
"$CODEX_BIN" plugin remove marketplace-zxgc@marketplace-zxgc
"$CODEX_BIN" plugin add marketplace-zxgc@marketplace-zxgc
"$MARKETPLACE_ZXGC_HOME/plugins/marketplace-zxgc/scripts/validate-pack.sh"
```

更新后按需重新同步：

```bash
CODEX_HOME="$CODEX_HOME" "$MARKETPLACE_ZXGC_HOME/plugins/marketplace-zxgc/scripts/sync-skills.sh" --dry-run
CODEX_HOME="$CODEX_HOME" "$MARKETPLACE_ZXGC_HOME/plugins/marketplace-zxgc/scripts/sync-skills.sh" --apply
```

如更新了 AGENTS.md、rules 或 hooks 模板，分别重新执行对应 dry-run 和 apply。

## 11. 维护者推送配置

普通安装和使用不需要配置 GitLab token。只有需要从本机向 `marketplace-zxgc` 远端提交维护变更时，才需要配置推送凭据。

推送脚本会从自身位置自动识别仓库根目录，不依赖原机器绝对路径：

```bash
"$MARKETPLACE_ZXGC_HOME/scripts/push-marketplace.sh"
```

凭据识别优先级：

- 当前 shell 已导出的 `GITLAB_PERSONAL_ACCESS_TOKEN` 或 `GITLAB_TOKEN`。
- `MARKETPLACE_ZXGC_ENV_FILE` 指向的本机 env 文件。
- `$HOME/.config/marketplace-zxgc/env`。
- `$HOME/.marketplace-zxgc.env`。
- Git 已配置的 credential helper。

推荐配置：

```bash
mkdir -p "$HOME/.config/marketplace-zxgc"
cp "$MARKETPLACE_ZXGC_HOME/docs/marketplace-zxgc.env.example" "$HOME/.config/marketplace-zxgc/env"
chmod 600 "$HOME/.config/marketplace-zxgc/env"
```

然后编辑 `$HOME/.config/marketplace-zxgc/env`，填入本机自己的 token。不要把真实 token、cookie、私钥或登录态文件提交到仓库。

也可以临时指定 env 文件：

```bash
MARKETPLACE_ZXGC_ENV_FILE="$HOME/private/marketplace-zxgc.env" \
  "$MARKETPLACE_ZXGC_HOME/scripts/push-marketplace.sh"
```

## 12. 卸载或回滚

从 Codex marketplace 移除注册：

```bash
"$CODEX_BIN" plugin marketplace remove marketplace-zxgc
```

恢复被安装脚本备份的文件：

```bash
ls "$CODEX_HOME"/*.bak.*
find "$CODEX_HOME/backups/skills" -maxdepth 2 -type d 2>/dev/null
```

选择需要恢复的备份后手动 `mv` 回原路径。不要直接删除当前配置，除非确认已有可用备份。

## 常见问题

### 注册 marketplace 后还需要 sync-skills 吗？

需要。`codex plugin marketplace add` 负责让 Codex 识别 marketplace；`sync-skills.sh` 负责把选定 skill 同步到目标机器的 `~/.codex/skills`，方便普通 Codex 会话直接使用。

### 为什么 hooks 不能直接复制？

hooks 通常需要包含目标机器上的实际仓库路径和脚本路径。共享仓库只保存模板和生成脚本，目标机器应通过 `install-hooks.sh` 生成本地配置。

### 为什么 rules 模板不包含具体脚本绝对路径？

共享 rules 应只表达可移植的用户级规则。绝对路径和具体仓库命令只适合目标机器本地配置，否则换机器后会失效，也可能误授权无关命令。

### 是否会同步 token？

不会。该 marketplace 明确排除 `auth.json`、API token、cookie、私钥、原始凭据输出和机器专属登录态。
