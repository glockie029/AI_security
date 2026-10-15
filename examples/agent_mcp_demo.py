"""原 MCP Agent 手动演示；需要匹配的 MCP SDK 和 API 配置。"""

import asyncio

from ai_security.agent import run_agent_mcp


def main():
    print(asyncio.run(run_agent_mcp("你现在可以调用哪些工具？总共有哪些工具")))


if __name__ == "__main__":
    main()
