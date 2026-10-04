# Lino OS

> 一个以「普通用户友好」为第一原则的**自由、开源** Linux 发行版。
> 让 Linux 不再是极客专属：装上即用，任何软件双击即装，全程零终端。

## 战略定位

**第一版只做 PC 系统**；Server 是第二方向，先放一放，等 PC 站稳、第一版发出去再说。不碰 Phone、不碰 IoT。

- **核心问题 1 — Windows 太臃肿、老崩溃**：用轻量、稳定、可维护的 Linux 底子 + 自研精致界面替代。
- **核心问题 2 — Linux 装软件/适配太难，厂商不愿适配**：用统一安装器 + 完善生态反过来吸引厂商。
- **两个解法（互为因果）**：① 软件好开发（统一格式、跨发行版、跨架构，一次打包处处可装）；
  ② 生态完善（用户多 → 厂商愿适配 → 用户更多，形成正循环）。
- **方向参照**：Android 本就是一个 Linux 发行版，Lino 向它「生态规模 + 开发友好」靠拢，但 Lino 只做 PC。

## 挡在用户面前的两堵墙

Lino OS 不是又一个换皮的 Linux 发行版，它的使命是拆掉两堵把大多数用户挡在门外的墙：

1. **软件安装不通用** —— 不同发行版的 `.deb` / `.rpm` / AUR 互不兼容，装不上、依赖地狱。
   → Lino 提供 **Lino App Installer**：统一安装格式，跨发行版通用，GUI 一键安装。
2. **终端劝退** —— 大多数普通用户不会、也不应该被要求使用命令行。
   → 安装、配置、日常使用全部图形化；终端退居幕后，但为开发者完整保留。

## 五层架构（从高到低）

| 层 | 名称 | 职责 |
|---|------|------|
| 1 | 用户显示层 | 自研桌面 Shell，原则：可靠、安全、自由、免费、美观 |
| 2 | 用户应用层 | Lino VLC、Lino App Installer、Android/Windows 虚拟机 |
| 3 | 安全层 | 应用沙箱、权限模型、进程隔离 |
| 4 | Linux 内核层 | Linux 内核 |
| 5 | 硬件抽象·安全隔离层 | 类 Qubes 的硬件抽象 + Secure Boot + UEFI（**仅支持 UEFI 启动**） |

> 详细设计见 [`docs/architecture.md`](docs/architecture.md)。

## 硬件适配

Lino **不止适配 CPU/GPU，而是适配电脑里的一切硬件**：存储（SATA/NVMe）、USB/雷电、有线/无线网卡、
蓝牙、声卡麦克风、键鼠/触摸板/触摸屏、串口（COM）/并口（LPT）等传统 I/O、打印机、摄像头、
电源管理（ACPI）与虚拟化（VT-x/AMD-V、VT-d/IOMMU）。

- CPU 双架构：x86_64（P0）、arm64（P1）；GPU 三厂：Intel / AMD / NVIDIA。
- 策略：优先保证现有 Linux 驱动「**完美运行**」，不重复造轮子；待社区影响力足够，厂商自然来适配。

## 内置应用

- **Lino VLC** —— 自有音视频播放器（基于开源 VLC 内核）
- **Lino App Installer** —— 统一应用安装器，整个 OS 的灵魂
- **Android 虚拟机** —— 基于开源 [Waydroid](https://waydro.id/)
- **Windows 虚拟机（可选）** —— 基于开源的 QEMU/KVM

## 开源许可

- 本项目自身代码以 **GNU GPL-3.0-or-later** 发布，详见 [`LICENSE`](LICENSE)。
- 仅采用合法、可自由使用/商用、开源的内核与组件（Linux 内核为 GPL-2.0，Linux 内核与
  Lino 用户态程序各自独立、互不影响）。
- 项目成熟后将整体在 GitHub 公开。

## 项目结构

```
Lino OS/
├── README.md               # 本文件
├── CHANGELOG.md            # 发布日志（v0.1.0 第一版范围）
├── LICENSE                 # GPL-3.0
├── docs/
│   └── architecture.md     # 五层架构详细设计
├── apps/
│   └── installer/          # Lino App Installer 核心（统一安装器，Flatpak 后端）
├── security/
│   └── threatscan/         # ThreatScan 威胁扫描器（安全层·审查闸门）
├── shell/
│   └── index.html          # 用户显示层（Lino Shell）原型，浏览器直接打开
├── iso/
│   └── build.sh            # 一条命令出可安装 ISO（live-build + Calamares）
└── .github/workflows/      # 推 tag 自动构建 ISO 并发布到 Release
```

## 快速体验

用任意现代浏览器打开 [`shell/index.html`](shell/index.html)，即可看到 Lino Shell 的
显示层交互原型：开机动画、桌面、Dock、窗口管理、Lino App Installer、Lino VLC。

> 这是「第 1 层 · 用户显示层」的高保真交互原型，用于先敲定 UI/UX 与动效，再向
> 真实合成器（compositor）技术栈落地。

## 可安装镜像（ISO）

第一版目标是**像 Windows 一样安装**的 PC 操作系统，最终打成 `.iso`：

- 底座：Debian stable 内核 + 轻量桌面；
- 安装器：**Calamares** 引导式安装（选语言 → 分区 → 建用户 → 安装 → 重启），即 Windows 式向导；
- 安装后开机进桌面，桌面内置「安装 Lino OS」与「Lino Shell」两个入口。

**出 ISO 的两种方式**

1. **GitHub Actions（推荐，免本地环境）**：推一个 `v*` tag，CI 在 Linux 云机自动跑
   `iso/build.sh`，把 `lino-os-0.1.0-amd64.iso` 附到该版本的 Release 上。
2. **本地构建**（需 Linux，如 WSL2 或 Debian 机器）：

   ```bash
   sudo bash iso/build.sh    # → dist/lino-os-0.1.0-amd64.iso
   ```

> 本机为 Windows 且无 Linux 工具链，本地出 ISO 前请先装 WSL2（`wsl --install`）。

## 路线图

- **Phase 0（完成）**：架构定稿 + 显示层原型，锁定视觉与交互。
- **Phase 1（进行中）**：可启动/可安装 ISO（live-build + Calamares，仅 UEFI），桌面跑起 Lino Shell。
- **Phase 2（进行中）**：Lino App Installer 落地（统一格式 + 后端 + 商店 UI），接入沙箱（核心 CLI 已可用）；
  威胁扫描已接入——ThreatScan（哈希签名匹配 + EICAR 自检）挂到安装前钩子，命中即拦截。
- **Phase 3**：Android 虚拟机（Waydroid）/ Windows 虚拟机（QEMU/KVM）集成。
- **Phase 4**：第 5 层类 Qubes 硬件抽象 + Secure Boot 信任链强化。

## 协作理念

这是一个长期、诚实的开源工程。内核站在巨人的肩膀上（Linux），真正自研的是
显示层、统一安装器、安全层与整体体验——这部分我们会一步一个脚印写完、测过、公开。