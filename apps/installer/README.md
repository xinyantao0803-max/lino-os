# Lino App Installer（核心）

统一应用安装器 —— Lino OS 的「灵魂」。解决不同 Linux 发行版软件安装不通用的问题。

## 设计

- **统一格式 + 免终端**：用户只面对「搜索 → 一键安装」，无需关心 `.deb` / `.rpm` / AUR。
- **复用 Flatpak 后端**：Flatpak 提供跨发行版的运行时与沙箱（bubblewrap），正契合 Lino 所需的
  「统一安装 + 应用沙箱」；Lino 在其上自研体验与权限模型，而非重复造轮子。
- **安全协同**：安装前展示应用申请的权限并显式授权，呼应 Lino 安全层（第 3 层）。

## 目录

```
apps/installer/
├── lino-app               # 启动脚本
├── lino_app/
│   ├── __init__.py
│   ├── __main__.py        # python -m lino_app
│   ├── schema.py          # 应用清单数据模型 + 校验
│   ├── registry.py        # 仓库索引加载/查询
│   ├── backend.py         # Flatpak 适配层
│   └── cli.py             # 命令行入口
└── repo/
    └── index.json         # Lino 应用仓库索引
```

## 运行

```bash
# 在本目录（apps/installer）下
python -m lino_app search vlc
python -m lino_app info org.lino.vlc
python -m lino_app install org.lino.vlc      # 需本机装有 flatpak
python -m lino_app list
python -m lino_app remove org.lino.vlc
python -m lino_app update
```

## 状态

当前为 Python 参考实现，仅完成 `flatpak` 后端（`waydroid` / `qemu` 后端为规划中）。
后续按性能与安全需求可迁移到 Rust/Go，并接入图形化商店 UI（对接 `shell/index.html`
中的 App Installer 界面）。