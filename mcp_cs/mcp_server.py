import re
from mcp.server import MCPServer

mcp = MCPServer("Vulnerability Knowledge Server")

# 教学数据，后续再接入原有 CVE_DATABASE
CVE_DATA = {
    "CVE-2021-44228": {
        "cve_id": "CVE-2021-44228",
        "severity": "Critical",
        "description": "Apache Log4j 2 远程代码执行漏洞"
    }
}

@mcp.tool()
def get_vulnerability(cve_id: str) ->dict:
    """根据CVE编号查询漏洞信息"""
    if not re.findall(r"CVE-\d{4}-\d{4,}",cve_id):
        return {"error":"Invalid CVE ID"}
    return CVE_DATA.get(
        cve_id,
        {"error":"CVE not found"}
    )

if __name__ == "__main__":
    mcp.run()