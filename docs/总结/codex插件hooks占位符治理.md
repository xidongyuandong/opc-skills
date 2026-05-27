# Codex 插件 hooks 占位符治理

## 核心结论

`marketplace-zxgc` 的插件级 `hooks.json` 不能包含 `{{PLUGIN_ROOT}}` 这类安装期占位符；Codex 可能直接加载插件包内的 hook manifest，未渲染占位符会在远端容器里变成不存在的脚本路径并阻断 `SessionStart` 或 `UserPromptSubmit`。

核心主张：用“空插件级 manifest + 安装脚本渲染到 `CODEX_HOME/hooks.json`”解决插件可移植模板和 Codex 运行时直接加载之间的冲突。

## 读者任务

未来维护 `marketplace-zxgc` hooks、安装脚本或 c250 远端插件缓存时，读者应能判断哪些 hook 配置可以被 Codex 直接加载，如何把模板渲染到真正的 `CODEX_HOME/hooks.json`，以及如何排查远端 hook 路径错误。

## 证据

- c250 远端会话曾报错：`python3: can't open file '/data/jenkins/{{PLUGIN_ROOT}}/hooks/codex_learning_hook.py'`。
- 远端 `CODEX_HOME/hooks.json` 已经是正确的 `/data/jenkins/marketplace-zxgc/...` 路径，但安装缓存里的 `plugins/cache/.../hooks.json` 仍包含 `{{PLUGIN_ROOT}}`。
- 将插件源和安装缓存内的 `hooks.json` 改为空 manifest 后，真实 hooks 仍由 `CODEX_HOME/hooks.json` 提供，`c250-codex` 冒烟会话可以正常收到并回复提示词。

## 维护规则

- `hooks.json.template` 可以保留 `{{PLUGIN_ROOT}}`，只供 `scripts/install-hooks.sh` 渲染。
- 插件包声明的 `hooks.json` 必须是空 manifest，或已经渲染成当前机器可执行的绝对路径。
- 真实生效的用户 hooks 应安装到 `CODEX_HOME/hooks.json`。
- 修复 hook 故障时同时检查两个位置：`CODEX_HOME/hooks.json` 和 `CODEX_HOME/plugins/cache/<marketplace>/<plugin>/<version>/hooks.json`。
- Hook 脚本必须先完整消费 Codex 写入的 stdin，再执行空闲判断或提前返回。尤其是 `Stop` hook，即使当前没有待处理任务，也不能在读取 stdin 前直接退出，否则 Codex 可能报 `failed to write hook stdin: Broken pipe`。

## 检查清单

1. 先确认报错路径来自 `CODEX_HOME/hooks.json` 还是插件缓存里的 `hooks.json`。
2. 如果路径含 `{{PLUGIN_ROOT}}`，不要只改安装脚本；还要处理已安装插件缓存。
3. 保留 `hooks.json.template` 作为可移植模板，把插件级 `hooks.json` 置为空 manifest。
4. 重新运行 `scripts/install-hooks.sh --apply` 或等价渲染步骤，把真实绝对路径写入 `CODEX_HOME/hooks.json`。
5. 启动一个短 Codex 会话，确认 `SessionStart` 和 `UserPromptSubmit` 不再被 hook 阻断。
6. 对每个会提前返回的 hook 做大 stdin 管道测试，确认空闲路径也会返回 0 且不触发 Broken pipe。

## 不写入范围

- 不把某次远端任务的完整日志、TUI transcript 或用户提示词写入本总结。
- 不把机器特定的 hook trust hash 作为仓库规则持久化；它属于各机器的 `config.toml` 运行状态。
- 不把 token、auth 文件或私有凭据写入 hook manifest 或总结。

## 验证命令

```bash
python3 -m json.tool plugins/marketplace-zxgc/hooks.json >/dev/null
bash -n plugins/marketplace-zxgc/scripts/install-hooks.sh
grep -RIn '{{PLUGIN_ROOT}}' "$CODEX_HOME/hooks.json" "$CODEX_HOME/plugins/cache" 2>/dev/null
```

远端 c250 可用：

```bash
c250-exec 'grep -RIn "{{PLUGIN_ROOT}}" /data/jenkins/.codex/home/hooks.json /data/jenkins/.codex/home/plugins/cache 2>/dev/null || echo "no active hook placeholders"'
c250-codex --sync-strict --session hook-smoke --force -- "只回复 OK"
```

Stop hook stdin 测试：

```bash
python3 - <<'PY' | python3 plugins/marketplace-zxgc/hooks/task2zxgc_posthook.py --event Stop
import json
print(json.dumps({"hook_event_name": "Stop", "payload": "x" * 200000}))
PY
```

## 边界与风险

- 不要把 token、auth 文件或私有凭据写入 hook manifest。
- 不要用插件级 `hooks.json` 和 `CODEX_HOME/hooks.json` 同时注册同一批 hooks，否则会重复执行。
- 本规则只约束插件 hook manifest；普通技能、AGENTS 模板和安装脚本仍可保留占位符，只要不会被 Codex 运行时直接当作 hook 配置加载。
