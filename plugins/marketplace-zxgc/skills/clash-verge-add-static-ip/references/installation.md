# Clash Verge 安装检测、安装与复检

## 先检测，不先要求用户找配置

Python 3.9+ 即可运行，无第三方包依赖。用当前 skill 的实际绝对路径执行：

```bash
python3 "$skill_dir/scripts/check_clash_verge_installation.py"
```

自定义安装位置由用户提供；macOS 传 `.app`，Windows/Linux 传应用可执行文件：

```bash
python3 "$skill_dir/scripts/check_clash_verge_installation.py" --app-path "$application_path"
```

结果为 JSON，必须读取 `status`，不能仅凭命令退出 0 判定已安装：

|状态|含义|下一步|
|---|---|---|
|installed|找到应用候选原生文件；macOS 同时核对 bundle 元数据|核验身份、版本与打开情况，确认后继续收集配置路径|
|not_found|只检查过常见安装位置和 PATH，没有找到有效文件|问是否自定义安装；用户确认未安装后走官方安装|
|unknown|不支持的平台/架构、自定义路径无效、权限不足或元数据异常|说明原因、询问位置/系统或请用户完成必要 OS 授权；不可假称未安装或已安装|

脚本不读取订阅/凭据、不枚举进程、不执行发现的二进制、不联网、不安装、不启动或退出应用。
`launch_check=not_performed` 一直表示启动未验证。macOS 版本取自 plist；Windows/Linux 版本可能为空，应从应用“关于”或可信包管理器元数据核对，不执行来历不明的程序获取版本。
Windows/Linux 的原生文件证据不是发行者签名证明，`identity_verified=false`；即使 `installed` 也需要用户/包管理器确认它确为 Clash Verge Rev。macOS bundle ID 也不是签名验证。只有 mihomo 内核、旧配置目录、PATH 包装脚本不能证明已安装 GUI。

常见安装路径不是穷尽清单：便携包、AppImage、用户自定义目录可能需 `--app-path`。没有桌面/远程终端不能据此断定应用未安装，也不能报告 GUI 已打开。未知架构应查当前官方支持范围，不猜一个安装包。

`dependencies` 独立提示 Ruby（构建器）和 Node.js（sidecar 执行/回归）是否在 PATH；这与 GUI 安装状态无关。缺依赖按当前平台正规安装方式补齐，不能报告静态配置已生成。

## 用户确认未安装后的官方安装流程

官方入口：[安装说明](https://www.clashverge.dev/install.html)、[GitHub Releases](https://github.com/clash-verge-rev/clash-verge-rev/releases)。每次实际安装时查当时支持的系统版本、CPU 架构与稳定版文件，避免硬编码“最新版”。

- **macOS**：识别 Intel/x64 与 Apple Silicon/arm64，下载官方对应 DMG，校验来源并按安装器操作拷入 Applications。若 Gatekeeper/管理员授权阻塞，由用户处理正常系统授权；不关闭安全机制、不自动移除 quarantine。
- **Windows**：官方文档支持 `winget install --exact --id ClashVergeRev.ClashVergeRev`。先检查 winget 可用及包身份；不加入静默同意许可参数。否则使用 Releases 的对应 x64/arm64 安装器，UAC/许可交互交由用户。
- **Linux**：先识别发行版与架构，按官方支持选择 deb/rpm 等包。Ubuntu/Debian 使用包管理器安装已下载的正确 deb，RPM 系使用相应包管理器。Arch/AUR 路线涉及社区构建，先说明来源，不默认安装构建工具或执行未知脚本。无受支持包或桌面时询问用户，不把仅安装内核当成完成。

在用户授权的安装范围内可下载并安装；安装器、OS 或账户强制授权不能由 agent 绕过。不要使用 `curl | sh`、第三方镜像脚本或自动购买代理。

## 安装之后必须重新检查

1. 重跑探测器；自定义目录用同一 `--app-path`，不沿用安装前结果。
2. 仍为 not_found/unknown：报告本次安装没有获得成功证据，保留安装器的脱敏错误与下一步；不能继续假设 GUI 可用。
3. 找到应用：从可信元数据/关于页核对名称与版本；按用户授权打开应用确认【订阅】页面可访问，记录 GUI 结果。已有正在运行的应用不重启、不切代理。
4. 然后提示：“在 Clash Verge →【订阅】→ 右键原订阅 →【打开文件】，提供配置文件绝对路径。”新安装还没有订阅时，请用户导入自己的基础 VPN 配置或订阅，再继续静态 IP 构建。

本 skill 的自动测试只模拟安装证据和失败状态，不宣称已验证三种系统的真实安装过程。
