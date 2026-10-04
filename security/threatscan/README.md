# ThreatScan — Lino 威胁扫描器（审查闸门）

安全层（第 3 层）的第一个落地模块：对本地文件/字节流做**哈希签名匹配**，命中已知威胁即告警，
供 App Installer 安装前校验与安全中心调用（对应架构文档「审查闸门」职责）。

## 定位

- **签名库 + 哈希匹配**的最小可信实现；签名库可由开源威胁情报（如 ClamAV 的 .hdb/.ldb）或
  自定义 JSON 供给。
- 内置 **EICAR 测试签名**用于验证扫描链路（EICAR 是杀毒行业标准的合法测试样本，无真实危害）。

## 运行

```bash
# 在 security/threatscan 目录下
python -m threatscan selftest                 # 自检：应能检出 EICAR
python -m threatscan scan <文件或目录>          # 退出码：0=干净，2=命中威胁
```

## 与 App Installer 的接口

App Installer 在 `install` 时可用 `--preflight-scan <本地包>` 在安装前调用本扫描器，
命中即拦截（**fail-closed**：扫描器异常/未知状态也拦截）。可通过环境变量
`LINO_THREATSCAN_CMD` 覆盖扫描命令（默认 `python -m threatscan`）。

## 签名库格式

`signatures/builtin.json`：

```json
{
  "version": 1,
  "signatures": [
    { "name": "示例", "md5": "...", "sha256": "..." }
  ]
}
```

## 后续扩展

- 读取 ClamAV `.hdb`（MD5）与 `.ldb`（逻辑签名）；
- 接入在线威胁情报 API；
- 面向「运行前行为监控」（eBPF）与「安全中心」告警联动。