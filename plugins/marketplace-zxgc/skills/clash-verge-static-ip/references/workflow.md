# Clash Verge 静态 IP Workflow

## 目标链路

```text
进入 Mihomo 的流量
-> MATCH,🌐 静态IP出口
-> cliproxy-static
-> dialer-proxy: 🚀 Auto-Best
-> 普通订阅节点作为拨号上游
```

静态 SOCKS5 服务负责最终出口身份，订阅节点只负责连接该服务。普通菲律宾节点不能替代静态代理，即使 IP 检测也显示菲律宾。

## 前置检查

1. 参考配置必须是可解析 YAML，并包含名为 `cliproxy-static` 的代理。
2. 静态代理必须带 `dialer-proxy: 🚀 Auto-Best`。
3. 目标配置必须包含 `🚀 Auto-Best` 代理组，且该组能选择实际订阅节点。
4. 确认目标文件是否为 Clash Verge 当前使用的 profile；不要凭文件名猜测。
5. 记录 Clash Verge 当前系统代理、TUN 和 profile 类型。

## 构建候选配置

默认运行 `build_static_ip_profile.rb`，不传 `--apply`。脚本会：

- 从参考配置提取 `cliproxy-static`，保留其协议字段但不打印敏感值。
- 替换目标中同名代理，避免重复定义。
- 创建或替换 `🌐 静态IP出口` select 组，唯一成员为 `cliproxy-static`。
- 删除所有已有 `MATCH` / `MATCH-DIRECT` 规则，在末尾写入唯一 `MATCH,🌐 静态IP出口`。
- 验证所有代理组成员和 `dialer-proxy` 引用存在。
- 将候选写到 `--output`；不会修改目标文件。

`--apply` 模式会先在目标同目录创建 `目标文件.before-static-ip-时间戳.bak`，再以候选内容覆盖目标。应用 live profile 前必须取得用户明确确认。

## 静态验证

运行 `verify_static_ip_profile.rb --profile 候选文件`。最低门槛：

- `cliproxy-static` 恰好一个。
- `dialer-proxy` 指向 `🚀 Auto-Best`。
- `🌐 静态IP出口` 恰好一个，且唯一成员为 `cliproxy-static`。
- `MATCH` 类规则恰好一个，且为最后一条规则。
- 代理组成员与 dialer 引用完整。
- 若提供 `--mihomo-bin`，Mihomo `-t` 配置检查成功。

## Local profile 持久化登记

候选 YAML 通过静态验证后，仍不能把“文件存在”或“外部写入
`profiles.yaml`”视为 Clash Verge 已登记该 profile。应用运行时由其内存模型
持有 profile 索引；外部改写索引后再退出，可能被应用保存的旧状态覆盖，并使
未登记候选被清理。

1. 保持当前 Clash Verge 运行，不为登记候选而主动退出或重启。
2. 在 GUI 使用 `New → Local` 选择候选文件；点击 Save 前取得行动时确认。
3. Save 后只读核验目标 UID 在 `profiles.yaml` 中恰好出现一次、类型为
   `local`、名称符合预期，且正式 UID YAML 存在。
4. 默认只报告 current；只有用户明确要求保持或切换到某个 profile 时，才把
   current 与该显式期望比较。不得永久硬编码某个国家为 current。
5. 完成 UID/index/current 与 source/live 检查后，才清理未引用候选。

如果项目已有发布真源和同步检查器，按该项目提供的只读校验流程验证登记与部署一致。
当前 profile 必须从现场读取，不能把某个国家或作者机器的 manifest ID 当作默认值。
该检查不应重载或切换 Clash Verge。没有项目专用工具时，使用上述 GUI 与只读元数据核验。

## 运行态验收

静态结构验证后，仍需在实际运行环境检查：

1. Clash Verge 重新加载目标 profile。只有用户明确把重启持久性纳入本轮验收范围时才重启应用；Local 登记本身不得以退出/重启作为保存手段。
2. Mihomo API 运行态中存在 `cliproxy-static` 与 `🌐 静态IP出口`，引用关系一致。
3. 最终只保留一个预期 Mihomo 进程，避免旧进程继续占用端口或提供旧配置。
4. 通过 Mihomo 代理访问目标站，例如 `https://ippure.com/`，要求 HTTP 成功。
5. 核对出口 IP、国家/城市和 ISP 是否符合静态代理供应商资料。
6. 若重启持久性已获明确授权，重启 Clash Verge 后重复第 2 至第 5 步；否则把该项标为未验证边界，不得为补证据擅自退出。

已知成功样例的验收表现是目标站 HTTP 200，出口位于 Philippines / Manila，ISP 为 Arisk Communications。该样例只用于说明验收维度，不应硬编码为所有供应商的预期值。

## 常见失败

- **参考 YAML 无效**：先修复来源文件格式；禁止脚本猜测并吞掉解析错误。
- **健康检查错误**：`Auto-Best` 应使用真实 HTTP/HTTPS 探测地址，不要把 SOCKS 服务地址当 HTTP 健康检查 URL。
- **GUI 不显示 local profile**：当前版本可能不展示 `type: local`，应以实际加载配置和运行态 API 为准。
- **订阅刷新覆盖修改**：保留备份，并在每次订阅更新后重新生成、验证候选。
- **出口国家正确但链路错误**：必须同时检查运行态代理引用、目标站可达和 ISP/出口身份。
- **覆盖范围表述过度**：系统代理开启但 TUN 关闭时，只能证明进入 Mihomo 的流量走静态出口。

## 错误尝试与正确第一步

| 错误尝试或症状 | 为什么错误 | 正确第一步 | 自动门禁 |
| --- | --- | --- | --- |
| 参考文件在 YAML 第 18 行附近解析失败后，继续猜测并合并 | 局部语法损坏可能改变后续结构，猜测修复可能把错误配置写入 live profile | 停止写入，只报告文件与解析行号；先让来源生成合法 YAML 或制作人工审阅的修复副本 | 回归测试要求候选文件和备份均不存在 |
| 使用 `filter_map` 等新 Ruby API | macOS 系统 Ruby 2.6 不支持，脚本会在用户机器上直接失败 | 先运行 `ruby -v` 和脚本语法测试，使用 Ruby 2.6 可用 API | 测试脚本自身以当前 Ruby 执行全部场景 |
| 用 `ruby` 执行 `quick_validate.py` | 解释器与文件类型不匹配，会得到 `no Ruby script found` | 使用 `python3 .../quick_validate.py` | 验证命令在 Skill 中固定写明解释器 |
| 在一次性诊断表达式中把 `puts` 与 `map` 串错 | Ruby 调用优先级可能先执行 `puts`，随后对其 `nil` 返回值调用 `map` | 先把数据转换结果赋给变量，再单独 `puts result.inspect` | 正式回归不依赖临时一行式数据遍历 |
| 为找 YAML 错误打印整段真实 profile | 普通文本替换容易漏掉嵌套字段或数组形式，可能暴露 server、username、password、UUID 或 token | 使用解析器错误行号；需要结构检查时只输出键名、计数和布尔状态 | 测试扫描 stdout/stderr，禁止出现样例敏感值 |
| 用普通菲律宾节点代替静态 SOCKS5 | 国家相同只证明地理位置相似，不证明出口身份、ISP 或固定性相同 | 检查 `MATCH -> 静态组 -> cliproxy-static -> dialer-proxy` 的运行态引用 | verifier 检查唯一代理、组、MATCH 与引用完整性 |
| 静态校验通过后直接宣称配置已生效且 IP 长期固定 | 静态校验不覆盖进程、运行态选择、重启持久性和供应商长期承诺 | 继续执行 Mihomo API、目标站、出口身份和重启复验 | verifier 固定输出不能证明的边界 |
| Clash Verge 运行时外改 `profiles.yaml`，再退出验证新增 Local profile | 应用退出会保存内存索引，可能覆盖外改内容；候选文件存在不等于应用已登记 | 保持应用运行，通过 GUI `New → Local → Save`，再核验 UID 唯一、正式文件和 current | 脱敏登记测试覆盖 UID 缺失、重复、名称/类型错误及显式 current 不匹配 |

这些条目是可复用反模式，不保存本机真实代理地址、用户名、密码或订阅 URL。若新的错误只属于一次性命令笔误，优先补测试或修正命令，不扩大为全局规则。

## 回滚

1. 停止当前 Clash Verge/Mihomo 的配置重载操作。
2. 用最近的 `.before-static-ip-*.bak` 恢复目标 profile。
3. 重新加载或重启 Clash Verge。
4. 检查进程、端口、目标站访问和原订阅节点选择是否恢复。
