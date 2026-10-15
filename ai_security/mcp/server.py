"""最小 MCP 服务；保留原模拟数据和校验行为。"""

import re

CVE_DATA = {
    "CVE-2021-44228": {
        "cve_id": "CVE-2021-44228",
        "severity": "Critical",
        "description": "Apache Log4j 2 远程代码执行漏洞",
    }
}


def get_vulnerability(cve_id: str) -> dict:
    """根据CVE编号查询漏洞信息"""
    # 沿用原 findall 行为；完整匹配校验列入 README 待修项。
    if not re.findall(r"CVE-\d{4}-\d{4,}", cve_id):
        return {"error": "Invalid CVE ID"}
    return CVE_DATA.get(cve_id, {"error": "CVE not found"})


def create_server():
    from mcp.server import MCPServer

    server = MCPServer("Vulnerability Knowledge Server")
    server.tool()(get_vulnerability)
    return server


if __name__ == "__main__":
    create_server().run()
