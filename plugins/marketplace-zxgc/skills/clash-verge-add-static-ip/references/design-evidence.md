# 设计依据与通用化边界

本流程提炼自多轮真实 Clash Verge 配置任务，分发版只保留脱敏结论，不包含用户的配置路径、UID、订阅 URL、服务器地址或凭据。

|历史观察|采用的流程|不能推断|
|---|---|---|
|远程 YAML 内手工新增的静态对象会被订阅下载替换|Remote 使用订阅专属扩展脚本，在最新节点基础上重建|脚本 UID 存在不代表脚本有效|
|Ldy 远程订阅曾通过普通更新与代理更新|分别验证两种更新的下载、脚本与合成结果|不能保证另一供应商现在允许更新|
|Wget 远程订阅曾因 403 阻塞，Local 可用|区分 Local 快照和 Remote 刷新，报告授权阻塞|Local 成功不能当作 Remote 更新成功|
|auto-best 曾被当成入口，绕过静态服务|流量入口选择静态出口组，静态节点通过 dialer 使用 auto-best|中转所在地不等于静态出口地区|
|运行中外改订阅索引后退出，被应用内存覆盖|GUI 新建、保存、卡片可见、只读 UID 登记核验|生成 YAML 不等于已注册|
|已有业务 DIRECT 规则需要保留|通用入口不自动重写全局规则或 DNS|单条 MATCH 不能代表全部流量覆盖|
|历史配置在不同解析器上表现不一致|隔离候选、解析失败报行号、Mihomo 原生检查|Ruby/YAML 解析成功不等于内核接受|

## 官方核验入口

构建前遇到版本差异应重新核验官方文档，按安装版本的 GUI 实际能力执行：

- [Clash Verge Rev 订阅导入](https://www.clashverge.dev/guide/profile.html)：本地新建选择文件并保存，或支持的版本拖拽导入。
- [Clash Verge Rev 扩展配置与脚本](https://www.clashverge.dev/guide/extend.html)：区分全局与订阅作用域；注意数组替换与实际执行顺序。
- [Mihomo dialer-proxy](https://wiki.metacubex.one/config/proxies/dialer-proxy/)：由静态落地节点通过订阅节点拨号，方向不能颠倒。
- [Mihomo SOCKS](https://wiki.metacubex.one/config/proxies/socks/)：正式类型 socks5，认证/TLS/UDP 按供应商能力。

本轮文档核验日期：2026-10-02。官方文档不是安装版本的执行证据，真实兼容性仍需合成与内核验证。
