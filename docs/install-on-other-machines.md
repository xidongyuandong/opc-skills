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

## 1. 拉取仓库

推荐放在用户目录下，避免使用原机器的绝对路径：

```bash
cd ~
git clone https://gitlab.chehejia.com/zhengyuyu/marketplace-zxgc.git
cd ~/marketplace-zxgc
```

如果目标机器已配置 GitLab SSH，也可以使用 SSH remote：

```bash
cd ~
git clone git@gitlab.chehejia.com:zhengyuyu/marketplace-zxgc.git
cd ~/marketplace-zxgc
```

## 2. 校验 marketplace 包

先校验包结构、脚本语法和 skill 基本格式：

```bash
~/marketplace-zxgc/plugins/marketplace-zxgc/scripts/validate-pack.sh
```

预期看到：

```text
marketplace-zxgc validation passed
```

如果失败，先不要安装。根据报错修复缺失文件、脚本语法或 Codex 版本问题。

## 3. 注册 Codex marketplace

把本地仓库注册为 Codex marketplace：

```bash
codex plugin marketplace add ~/marketplace-zxgc
```

查看是否已注册：

```bash
codex plugin marketplace list
codex plugin list
```

后续仓库更新后，在目标机器执行：

```bash
cd ~/marketplace-zxgc
git pull --ff-only
codex plugin marketplace upgrade marketplace-zxgc
```

## 4. 同步 skills

先 dry-run：

```bash
~/marketplace-zxgc/plugins/marketplace-zxgc/scripts/sync-skills.sh --dry-run
```

确认输出符合预期后再应用：

```bash
~/marketplace-zxgc/plugins/marketplace-zxgc/scripts/sync-skills.sh --apply
```

默认会同步这些 skills：

```text
marketplace-zxgc session-self-improvement self-improving-agent continuous-learning-v2 code-refactor codex-hooks codex-hook codex-remote-container codex-ssh-remote-config
```

如只想同步一部分：

```bash
ZXGC_SKILLS="marketplace-zxgc session-self-improvement code-refactor" \
  ~/marketplace-zxgc/plugins/marketplace-zxgc/scripts/sync-skills.sh --apply
```

如希望某些 skill 以软链接方式安装，便于仓库更新后立即生效：

```bash
ZXGC_LINK_SKILLS="marketplace-zxgc code-refactor" \
  ~/marketplace-zxgc/plugins/marketplace-zxgc/scripts/sync-skills.sh --apply
```

注意：脚本会在覆盖已有 skill 前生成时间戳备份。

## 5. 安装 AGENTS.md 模板

AGENTS.md 会影响 Codex 的用户级行为约束。先预览：

```bash
~/marketplace-zxgc/plugins/marketplace-zxgc/scripts/install-agents-md.sh --mode replace
```

确认后应用：

```bash
~/marketplace-zxgc/plugins/marketplace-zxgc/scripts/install-agents-md.sh --mode replace --yes
```

原则：

- 只安装通用、稳定、用户级约束。
- 不把具体仓库总结、具体机器路径、临时任务要求写入全局 AGENTS.md。
- 如果目标机器已有重要 AGENTS.md，先阅读备份文件再决定是否迁移差异。

## 6. 安装 rules 模板

rules 会影响 Codex 对命令执行的自动许可判断。先 dry-run：

```bash
~/marketplace-zxgc/plugins/marketplace-zxgc/scripts/install-rules.sh --dry-run
```

确认后应用：

```bash
~/marketplace-zxgc/plugins/marketplace-zxgc/scripts/install-rules.sh --apply
```

rules 同步原则：

- 可以同步不涉及绝对路径、具体仓库、凭据和一次性任务的通用规则。
- 涉及绝对路径或具体仓库的规则，不直接同步；只抽取指导性信息进入文档或模板。
- 不原样复制本机 runtime rules。

## 7. 安装 hooks

hooks 可能引用本机安装路径，因此必须在目标机器本地生成。先 dry-run：

```bash
~/marketplace-zxgc/plugins/marketplace-zxgc/scripts/install-hooks.sh --dry-run
```

确认后应用：

```bash
~/marketplace-zxgc/plugins/marketplace-zxgc/scripts/install-hooks.sh --apply
```

应用后重新启动 Codex，使 hooks 配置生效。

## 8. 验证安装结果

检查文件：

```bash
ls ~/.codex/skills
test -f ~/.codex/AGENTS.md && echo "AGENTS.md installed"
test -f ~/.codex/rules/default.rules && echo "rules installed"
test -f ~/.codex/hooks.json && echo "hooks installed"
```

检查 Codex 内 skill 是否可用：

```text
$marketplace-zxgc
$session-self-improvement
$code-refactor
```

如果 skill 只被命名而没有明确任务，Codex 应只解释或使用该 skill 处理当前显式任务，不应推断为允许执行无关副作用操作。

## 9. 日常使用

常用命令：

```bash
cd ~/marketplace-zxgc
git pull --ff-only
codex plugin marketplace upgrade marketplace-zxgc
~/marketplace-zxgc/plugins/marketplace-zxgc/scripts/validate-pack.sh
```

更新后按需重新同步：

```bash
~/marketplace-zxgc/plugins/marketplace-zxgc/scripts/sync-skills.sh --dry-run
~/marketplace-zxgc/plugins/marketplace-zxgc/scripts/sync-skills.sh --apply
```

如更新了 AGENTS.md、rules 或 hooks 模板，分别重新执行对应 dry-run 和 apply。

## 10. 卸载或回滚

从 Codex marketplace 移除注册：

```bash
codex plugin marketplace remove marketplace-zxgc
```

恢复被安装脚本备份的文件：

```bash
ls ~/.codex/*.bak.*
ls ~/.codex/skills/*.bak.*
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
