# marketplace-zxgc 跨机器鲁棒安装

## 核心主张

`marketplace-zxgc` 在其他机器安装时，主要风险来自人工串联多个局部脚本导致漏步；应以一个可 dry-run、可 apply、可 smoke-test 的总控脚本作为团队安装入口，再用中文操作指导解释配置、验证和回滚。

未来读者任务：当团队成员需要在新机器、远程开发机或 c250/container 环境安装 marketplace-zxgc 时，先按本文理解风险边界，再使用 `scripts/install-marketplace-zxgc.sh` 和 `操作指导.md` 完成自动化安装与验证。

## 证据

- c250/container250 的 `CODEX_HOME` 是 `/data/jenkins/.codex/home`，不是默认 `$HOME/.codex`。如果安装脚本没有显式使用 `CODEX_HOME`，skills、rules、hooks 会落到错误目录。
- local marketplace 拉取新代码后，刷新方式依赖 Codex CLI 版本。旧 CLI 可能支持 `codex plugin add/list`，可用 `plugin remove marketplace-zxgc@marketplace-zxgc` 后再 `plugin add marketplace-zxgc@marketplace-zxgc`；当前本机 CLI 只支持 `codex plugin marketplace add/upgrade/remove`，且本地目录 marketplace 不是 Git marketplace，`marketplace upgrade` 会提示不可用。总控脚本应兼容检测：先 `plugin marketplace add <repo>`，旧 CLI 走 installed plugin remove/add，新 CLI 对本地 marketplace 允许 upgrade 失败后继续同步 assets。
- hooks 不能跨机器复制，因为 `hooks.json` 内需要目标机器真实的 plugin 脚本路径。必须在目标机器用模板重新渲染。
- c250 active skills 曾残留 `auto-merge-request.moved-to-code-refactor.20260521`，会被 Codex 扫描成可用 skill。同步脚本需要把已知废弃 skill stub 移到备份目录。
- 仅检查文件存在不够，需要 Codex smoke test 验证 hook 信任/启动路径不会阻断下一次会话。

## 实现入口

- 总控安装脚本：`scripts/install-marketplace-zxgc.sh`
- 中文操作说明：`操作指导.md`
- 分项脚本：
  - `plugins/marketplace-zxgc/scripts/validate-pack.sh`
  - `plugins/marketplace-zxgc/scripts/sync-skills.sh`
  - `plugins/marketplace-zxgc/scripts/install-agents-md.sh`
  - `plugins/marketplace-zxgc/scripts/install-rules.sh`
  - `plugins/marketplace-zxgc/scripts/install-hooks.sh`

## 标准安装流程

1. 设置目标机器环境变量：

```bash
export CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
export CODEX_BIN="${CODEX_BIN:-codex}"
export MARKETPLACE_ZXGC_HOME="${MARKETPLACE_ZXGC_HOME:-$HOME/marketplace-zxgc}"
```

2. 拉取仓库：

```bash
git clone https://gitlab.chehejia.com/zhengyuyu/marketplace-zxgc.git "$MARKETPLACE_ZXGC_HOME"
```

3. 先 dry-run：

```bash
"$MARKETPLACE_ZXGC_HOME/scripts/install-marketplace-zxgc.sh" --dry-run
```

4. 再 apply：

```bash
"$MARKETPLACE_ZXGC_HOME/scripts/install-marketplace-zxgc.sh" --apply
```

## 验证清单

- `validate-pack.sh` 通过。
- 若 CLI 支持 `codex plugin list`，确认显示 `marketplace-zxgc@marketplace-zxgc (installed, enabled)`；若当前 CLI 没有 `plugin list`，用 `codex plugin marketplace add "$MARKETPLACE_ZXGC_HOME"` 加文件验证作为替代。
- `$CODEX_HOME/AGENTS.md` 存在。
- `$CODEX_HOME/hooks.json` 存在且路径指向目标机器的 `MARKETPLACE_ZXGC_HOME`。
- `$CODEX_HOME/rules/default.rules` 存在。
- `$CODEX_HOME/skills/marketplace-zxgc/SKILL.md`、`code-refactor/SKILL.md`、`session-self-improvement/SKILL.md` 存在。
- `$CODEX_HOME/skills` 下没有 `bak`、`backup`、`moved`、`deprecated`、`auto-merge-request` 这类废弃 active skill。
- Codex smoke test 能输出 `marketplace-zxgc smoke ok`。

## 边界和风险

- 总控脚本默认 `--agents-mode block`，避免直接覆盖已有 `AGENTS.md`。干净机器需要全量替换时再使用 `--agents-mode replace`。
- smoke test 参数也依赖 Codex CLI 版本。旧 CLI 可用 `--dangerously-bypass-hook-trust --sandbox read-only`；当前 CLI 使用 `--dangerously-bypass-approvals-and-sandbox`。安装脚本应通过 `codex exec --help` 检测可用参数，不要硬编码单一版本。
- 安装流程不保存 GitLab token、Codex auth、cookie、私钥或任何机器登录态。
- 目标机器缺少 `jq` 时应先安装依赖，不应跳过 hooks/JSON 校验。

不持久化内容：不写入 c250 的一次性命令输出、Codex smoke test 原始长日志、个人 token 配置、`auth.json`、具体会话状态或临时备份目录；这些只作为本次验证证据，不进入全局 AGENTS 或用户级 rules。
