# Changelog

本项目遵循语义化版本（SemVer）。当前第一版聚焦 **PC 系统**；Server 为第二方向，暂不进入本版本范围。

## [0.1.1] — 修复安装器提权 + 中文本地化 + 系统身份 Lino 化

> 依据真机（VMware）首测反馈，修复「安装器未以管理员权限运行」与满屏 Debian 身份的问题。

### 变更

- **修复安装器无法安装**：桌面「安装 Lino OS」入口由 `Exec=calamares` 改为 `Exec=pkexec calamares`，
  并新增 `xfce-polkit`（图形授权代理），安装器得以提权运行。
- **中文本地化**：新增 `locales` + `fonts-noto-cjk`（中文显示）+ `fcitx5` 拼音输入法，
  默认语言设为 `zh_CN.UTF-8`。
- **系统身份**：`/etc/os-release` 覆盖为 `PRETTY_NAME="Lino OS 0.1.1"`、`ID=lino`、`ID_LIKE=debian`，
  系统信息不再显示为 Debian。

### 已知边界

- Calamares 安装器的界面品牌（标题/欢迎语/图标）仍沿用 `calamares-settings-debian`；
  本期只解决「能否安装」与系统身份，完整 Lino 品牌换皮 + 原生 Lino Shell 为下一主线。

## [0.1.0] — 第一版（可安装 PC 操作系统）

> 定位：交付一个**能刻盘/写 U 盘、像 Windows 一样安装到 PC** 的 Lino OS，
> 最终产物为 `lino-os-0.1.0-amd64.iso`。

### 交付物

- **可安装镜像构建管线（`iso/`）**：`iso/build.sh`（Debian live-build）+ Calamares 引导式安装器，
  GitHub Actions 推 `v*` tag 自动出 `.iso` 并附到 Release。
- **Lino Shell（用户显示层）**：`shell/index.html`，浏览器直接打开即可体验——
  开机动画、桌面壁纸/极光、顶栏（时钟·托盘·关机）、Dock（放大动效）、
  窗口管理（拖动/最小化/最大化/关闭/层级）、App Installer、Lino VLC、
  文件/设置/终端/开发者工具、Android/Windows 虚拟机入口，以及**安全中心**。
- **Lino App Installer（统一安装器）**：`apps/installer/`，Python CLI 可用
  （search / list / info / install / remove / update），Flatpak 后端，
  统一 `repo/index.json` 仓库，安装前权限确认，零终端理念。
- **ThreatScan（安全层·审查闸门）**：`security/threatscan/`，哈希签名匹配 + EICAR 自检，
  已接入安装器安装前扫描钩子（fail-closed：命中即拦截）。

### 本版关注

- 主攻 **PC**；不涉及 Server、Phone、IoT。
- 战略方向：软件好开发 + 生态完善，向 Android 的生态方式靠拢。
- 硬件适配：CPU（x86_64 / arm64）、GPU（Intel / AMD / NVIDIA）、整机外设
  （存储、USB/雷电、网络、蓝牙、音频、输入设备、串口/并口、打印、摄像头、电源、虚拟化）。

### 已知边界

- Shell 为高保真交互原型（HTML/CSS/JS），在真机上经浏览器 kiosk 呈现，尚未落地到
  原生合成器（compositor）技术栈。
- App Installer 的 GUI 商店为原型版；CLI 已可运行，真实安装依赖本机 Flatpak。
- 可安装 ISO 由 GitHub Actions 在 Linux 云机构建（本项目尚未在裸 Windows 上本地出过镜像）；
  首次构建需按 CI 日志迭代核对。