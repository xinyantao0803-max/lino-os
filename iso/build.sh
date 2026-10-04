#!/usr/bin/env bash
# =============================================================================
# Lino OS — 可安装 ISO 构建脚本
# 基于 Debian live-build + Calamares（Windows 式引导安装）
#
# 用法（需 Linux + root）：
#   sudo bash iso/build.sh
# 产出：
#   dist/lino-os-0.1.0-amd64.iso
#
# 本脚本同时被 GitHub Actions（ubuntu runner）调用，推送 tag 即自动出 ISO。
# =============================================================================
set -euo pipefail

VERSION="0.1.3"
CODENAME="bookworm"
ARCH="amd64"

TOP="$(cd "$(dirname "$0")/.." && pwd)"
ISO_DIR="$TOP/iso"
OUT_DIR="$TOP/dist"

if [ "$(id -u)" -ne 0 ]; then
  echo "错误：请以 root 运行（sudo ./iso/build.sh）" >&2
  exit 1
fi

export DEBIAN_FRONTEND=noninteractive

echo "==> [1/5] 安装构建依赖 live-build"
apt-get update -qq
apt-get install -y -qq live-build debootstrap ca-certificates

cd "$ISO_DIR"

echo "==> [2/5] 清理旧构建"
lb clean --purge 2>/dev/null || true

echo "==> [3/5] 注入 Lino 自有组件到 live 根文件系统"
rm -rf config/includes.chroot/usr/share/lino
mkdir -p config/includes.chroot/usr/share/lino
cp -r "$TOP/shell"     config/includes.chroot/usr/share/lino/shell
cp -r "$TOP/apps"      config/includes.chroot/usr/share/lino/apps
cp -r "$TOP/security"  config/includes.chroot/usr/share/lino/security
find config/includes.chroot -name __pycache__ -type d -exec rm -rf {} + 2>/dev/null || true

# Windows 上 checkout 出来的 hook 没有执行位，这里统一补齐
chmod +x config/hooks/normal/*.hook.chroot 2>/dev/null || true

echo "==> [4/5] 配置 live-build"
lb config \
  --distribution "$CODENAME" \
  --architectures "$ARCH" \
  --binary-images iso-hybrid \
  --archive-areas "main contrib non-free non-free-firmware" \
  --bootloaders "syslinux grub-efi" \
  --linux-flavours amd64 \
  --memtest none \
  --debian-installer none \
  --bootappend-live "boot=live components locales=zh_CN.UTF-8 username=lino user-fullname=Lino hostname=lino-os quiet splash" \
  --iso-application "Lino OS" \
  --iso-publisher "Lino OS Project" \
  --iso-volume "Lino_OS_${VERSION}"

echo "==> [5/5] 构建 ISO（首次需下载大量软件包，耗时较长）"
lb build

mkdir -p "$OUT_DIR"
cp -f "live-image-${ARCH}.hybrid.iso" "$OUT_DIR/lino-os-${VERSION}-${ARCH}.iso"

echo "==> 完成：$OUT_DIR/lino-os-${VERSION}-${ARCH}.iso"