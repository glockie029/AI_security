"""沿用原 MCP 客户端接口；SDK 兼容性单独列为待验证项。"""

import asyncio
import sys
from pathlib import Path

SERVER_PATH = Path(__file__).with_name("server.py")


def get_server_params():
    from mcp import StdioServerParameters

    return StdioServerParameters(
        command=sys.executable,
        args=[str(SERVER_PATH)],
    )


async def test_mcp_client():
    """原手动联调演示，不是离线自动化测试。"""
    from mcp import Client

    async with Client(get_server_params()) as client:
        tool_list = await client.list_tools()
        print("可用工具:")
        for tool in tool_list.tools:
            print(tool.name)

        result = await client.call_tool(
            "get_vulnerability", {"cve_id": "CVE-2021-44228"}
        )
        print("Tool result:", result.structured_content)
        print("Is error:", result.is_error)


if __name__ == "__main__":
    asyncio.run(test_mcp_client())
