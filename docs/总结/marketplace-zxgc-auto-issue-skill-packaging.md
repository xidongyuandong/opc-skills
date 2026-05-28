# marketplace-zxgc 打包 auto-issue 技能

## 核心主张

把本机 user-level skill 加入 `marketplace-zxgc` 时，不能只复制 `SKILL.md`。应把可复用的脚本、references 和轻量 agent 元数据一起打包，同时排除缓存、密钥、机器专属路径和默认激活副作用。

未来读者任务：当需要把 `$CODEX_HOME/skills/<name>` 迁入 `plugins/marketplace-zxgc/skills/<name>` 时，用本文理解并解决“只复制 SKILL.md 导致脚本或 references 缺失”的问题，检查目录完整性、可移植性和验证方式。

## 本轮证据

- 源技能：`$CODEX_HOME/skills/auto-issue/`
- 目标技能：`plugins/marketplace-zxgc/skills/auto-issue/`
- 需要打包的文件：
  - `SKILL.md`
  - `scripts/format_issue.py`
  - `references/gitlab_issue_workflow.md`
  - `agents/openai.yaml`
- 排除项：`scripts/__pycache__/format_issue.cpython-310.pyc`
- 验证命令：
  - `python3 -m py_compile skills/auto-issue/scripts/format_issue.py`
  - `python3 skills/auto-issue/scripts/format_issue.py --text ... --url ... --json`
  - `./scripts/validate-pack.sh`

## 打包流程

1. 先列源目录文件：

```bash
find "$CODEX_HOME/skills/auto-issue" -maxdepth 3 -type f -print | sort
```

2. 只复制可复用资产：

```bash
mkdir -p plugins/marketplace-zxgc/skills/auto-issue/{scripts,references,agents}
cp "$CODEX_HOME/skills/auto-issue/SKILL.md" plugins/marketplace-zxgc/skills/auto-issue/SKILL.md
cp "$CODEX_HOME/skills/auto-issue/scripts/format_issue.py" plugins/marketplace-zxgc/skills/auto-issue/scripts/format_issue.py
cp "$CODEX_HOME/skills/auto-issue/references/gitlab_issue_workflow.md" plugins/marketplace-zxgc/skills/auto-issue/references/gitlab_issue_workflow.md
cp "$CODEX_HOME/skills/auto-issue/agents/openai.yaml" plugins/marketplace-zxgc/skills/auto-issue/agents/openai.yaml
```

3. 清理缓存：

```bash
rm -rf plugins/marketplace-zxgc/skills/auto-issue/scripts/__pycache__
```

4. 验证：

```bash
cd plugins/marketplace-zxgc
python3 -m py_compile skills/auto-issue/scripts/format_issue.py
python3 skills/auto-issue/scripts/format_issue.py \
  --text "任务: 测试 auto issue; 评测: python3 -m py_compile" \
  --url "https://gitlab.chehejia.com/a/b" \
  --json
./scripts/validate-pack.sh
```

## 默认同步边界

新增 `skills/auto-issue/` 表示 marketplace 已打包该能力，不等于应自动加入默认同步或默认激活清单。是否把它写入默认安装列表，需要单独确认：

- 触发频率是否足够高。
- 是否会增加普通会话上下文成本。
- 是否涉及 GitLab API、浏览器、权限或提交副作用。
- 是否需要用户确认目标 issue/repo 后才能执行。

## 安全边界

- 不打包 `auth.json`、token、cookie、private key、credential 或本机登录态。
- 不打包 `__pycache__`、`.pyc`、临时输出和 smoke test 原始长日志。
- 不把本机绝对路径写入技能正文；脚本示例优先用 `$CODEX_HOME`。
- 不覆盖用户已有 `AGENTS.md`、`hooks.json` 或 active skills。

## Applied Skills And Agents

- Skills: `marketplace-zxgc`、`session-self-improvement`。
- MCP memory: `agentMemory`，记录 `marketplace-zxgc-skill-packaging-complete-directory`。
- Agents/sub-agents: None。
