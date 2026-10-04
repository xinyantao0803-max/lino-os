"""Lino ThreatScan —— 威胁扫描器（安全层·审查闸门）。

对文件/字节流做哈希签名匹配，命中已知威胁即告警；供 App Installer 安装前校验与
安全中心调用。签名库见 signatures/builtin.json。
"""

__version__ = "0.1.0"