import asyncio
import sys
from pathlib import Path

from mcp import Client,StdioServerParameters

SERVER_PATH = Path(__file__).with_name("mcp_server.py")

server_params = StdioServerParameters(
    command=sys.executable,
    args=[str(SERVER_PATH)]
)

async def test_mcp_client():
    async with Client(server_params) as client:
        #1.咨询MCP Server 提供哪些工具
        tool_list = await client.list_tools()

        print("可用工具:")
        for tool in tool_list.tools:
            print(tool.name)

        #调用指定工具
        result = await client.call_tool(
            "get_vulnerability",
            {"cve_id":"CVE-2021-44228"}
        )

        print("Tool result:", result.structured_content)
        print("Is error:", result.is_error)

if __name__ == "__main__":
    asyncio.run(test_mcp_client())