"""本地只读工具 Agent 演示；执行时会调用模型 API。"""

from ai_security.agent import run_agent


def main():
    print(run_agent("查询 CVE-2021-44228 的漏洞信息.", 3))


if __name__ == "__main__":
    main()
