"""CLI 和 Agent 共用的工具定义；不在此处决定执行权限。"""

from typing import Any

tool_definitions: list[dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "get_vulnerability",
            "description": "查询指定 CVE 的漏洞信息",
            "parameters": {
                "type": "object",
                "properties": {
                    "cve_id": {"type": "string", "description": "CVE 编号"}
                },
                "required": ["cve_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "update_vulnerability_status",
            "description": "更新指定 CVE 漏洞的处理状态",
            "parameters": {
                "type": "object",
                "properties": {
                    "cve_id": {"type": "string", "description": "CVE 编号"},
                    "status": {"type": "string", "description": "需要设置的新状态"},
                },
                "required": ["cve_id", "status"],
            },
        },
    },
]
