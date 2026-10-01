# Clash Verge 可移植 Sidecar Workflow

## 适用目标

用于需要持续更新的远程订阅。订阅 YAML 是可替换数据；profile 绑定的 JavaScript
sidecar 是自定义逻辑真源。每次 Clash Verge 合成配置时，sidecar 都根据最新订阅
节点幂等重建：

```text
Global 或 Rule 流量入口
-> 静态出口组
-> 静态 SOCKS5 代理
-> dialer-proxy: Auto-Best
-> 当前订阅的可用普通节点
```

## 把 Skill 复制到另一台电脑

复制整个 `clash-verge-static-ip` 目录，而不是只复制 `SKILL.md`。目标位置通常为
`~/.agents/skills/clash-verge-static-ip/`，并应同时包含 `assets/`、`references/`、
`scripts/` 和 `agents/`。不要把任何生成后的真实 sidecar、订阅文件或供应商凭证
放进 skill 目录。

在新电脑执行基础自检：

```bash
ruby ~/.agents/skills/clash-verge-static-ip/scripts/test_static_ip_workflow.rb
ruby ~/.agents/skills/clash-verge-static-ip/scripts/test_sidecar_workflow.rb
```

第二项回归需要 Node.js，仅用于执行生成后的 JavaScript 行为测试；Clash Verge
实际加载 sidecar 时使用自身的 enhancement 运行环境。如果新电脑没有 Ruby，
应由当地 agent 依据模板生成候选文件并做同等结构验证，不能跳过验证后直接绑定
在线 profile。

## 禁止的迁移方式

- 不覆盖另一台电脑现有的 `profiles.yaml`。
- 不复制本机 `clash-verge.yaml`、缓存、运行态数据库或 profile UID。
- 不把静态代理凭证、订阅 URL 或生成后的 sidecar 提交到代码仓库。
- 不直接编辑远程订阅下载出的 YAML 并假设更新后仍会保留。

## 生成可移植 Sidecar

准备一份只在本机保存的 provider/reference YAML，其中包含静态代理对象。凭证
不能通过命令行参数传递。

```bash
ruby scripts/build_static_ip_sidecar.rb \
  --reference /secure/provider-reference.yaml \
  --proxy-name cliproxy-static \
  --auto-group-name auto-best \
  --static-group-name '🌐 静态IP出口' \
  --entry-group-name Proxy \
  --exclude-regex '香港|澳门|台湾|HK|MO|TW' \
  --output /tmp/static-ip-sidecar.js
```

生成器默认不覆盖已有输出。需要重新生成时，先审阅目标，再显式传 `--force`。
输出日志只给出对象名称和路径，不打印 server、username、password 或 token。

## 在新电脑安装

1. 安装兼容版本的 Clash Verge Rev/Mihomo，先用订阅 URL 在 GUI 新建远程
   profile。不要复制旧电脑的 profile UID。
2. 通过 Clash Verge 的“打开配置目录”定位这台电脑的真实配置目录；不要根据
   macOS、Windows 或 Linux 的经验路径硬猜。
3. 在 GUI 新建或导入 JavaScript 类型的 profile enhancement，把候选 sidecar
   内容放入该文件。
4. 在远程订阅的 profile chain/增强配置中绑定这个 sidecar。只修改目标 profile
   的绑定，不替换整个 profile 索引。
5. 执行一次普通“更新”，再切换到该 profile，让 Clash Verge 生成最终配置。
6. 如果网络环境要求代理更新，再执行一次“更新（代理）”。两种更新都必须
   成功，且更新后 sidecar 文件内容不应被订阅下载覆盖。

不同版本 GUI 的按钮名称可能略有变化。若 GUI 没有展示绑定入口，先确认当前
版本支持 JavaScript enhancement/profile chain；不要通过猜测修改内部索引。

## 静态与合成验证

对 Clash Verge 的最终合成 YAML 运行：

```bash
ruby scripts/verify_sidecar_profile.rb \
  --profile /path/final-composed.yaml \
  --static-proxy-name cliproxy-static \
  --auto-group-name auto-best \
  --static-group-name '🌐 静态IP出口' \
  --entry-group-name Proxy
```

最低门槛：

- 静态代理、Auto-Best 和静态出口组各恰好一个。
- 静态代理的 `dialer-proxy` 指向 Auto-Best。
- Auto-Best 至少有一个真实订阅节点，且所有引用存在。
- 静态出口组只包含静态代理。
- `Proxy` 同时能选择静态出口组和 Auto-Best。
- Mihomo `-t`（若可用）通过。

## 运行态选择

“最终配置里存在静态代理”不等于“当前正在使用静态 IP”。

- Global 模式：在 `GLOBAL` 中选择静态出口组。
- Rule 模式：在规则实际进入的 `Proxy`（或现场确认的入口组）中选择静态出口组。
- 系统代理只能覆盖进入 Mihomo 的应用流量；声称全设备覆盖前必须确认 TUN。

随后通过 Mihomo 代理访问两个独立 IP 检测来源，核对 IP、国家/地区和 ISP。
检测站点失败不能单独证明代理失败：同时检查 HTTP 状态、DNS、浏览器扩展拦截和
另一检测源。

## 更新、重启与回归

每种更新路径和重启后重复检查：

1. 订阅节点确实更新，远程 YAML 可变化。
2. sidecar 文件未被更新覆盖。
3. 最终合成中静态代理、两类组和引用仍唯一且完整。
4. 当前运行态仍选择静态出口；若 Clash Verge 清空组选择，需要人工重新选择。
5. 公网 IP/ISP 符合供应商资料。

只有第 2、3 项通过，可以说“自定义逻辑保留”；只有第 4、5 项也通过，才能说
“静态出口当前生效”。一次 IP 命中不能证明供应商长期固定 IP 承诺。

## 回滚

1. 在目标订阅的 profile chain 中解除 sidecar 绑定。
2. 重新更新并加载原始订阅。
3. 确认最终合成配置不再包含本次静态代理和自定义组。
4. 删除生成 sidecar 前先确认没有其它 profile 引用；不删除远程订阅或整个
   `profiles.yaml`。

## 错误尝试与正确第一步

| 症状 | 正确第一步 | 不能据此推断 |
| --- | --- | --- |
| 更新后对象仍存在，但 IP 不是静态 IP | 检查 `GLOBAL` 或 `Proxy` 当前选项 | 不能说 sidecar 失效 |
| 普通更新成功、代理更新失败 | 检查更新链路使用的运行态代理和 DNS | 不能覆盖或重建整个 profile 索引 |
| 新电脑 GUI 看不到旧 UID | 通过 GUI 新建订阅并重新绑定 sidecar | UID 不应跨电脑复用 |
| IP 检测页显示“无法获取本机 IP” | 换第二检测源并检查 WebRTC/脚本拦截 | 不等于代理或静态出口失败 |
| Auto-Best 没有候选 | 检查排除正则和最新订阅代理列表 | 不允许静默回退到 DIRECT |
