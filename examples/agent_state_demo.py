"""原 Agent 状态循环演示，不调用模型或外部工具。"""

def run_agent(task: str, max_steps: int = 3):
    state = {
        "task": task,
        "step": 0,
        "completed": False,
        "tool_results": [],
    }
    while not state["completed"]:
        if state["step"] >= max_steps:
            print("达到最大执行步数")
            break

        state["step"] += 1

        if state["step"] == 1:
            result = {
                "tool": "get_vulnerability",
                "cve_id": "CVE-2021-44228"
            }
        elif state["step"] == 2:
            result = {
                "tool": "get_assets",
                "assets": ["server-01", "server-02"],
            }
        else:
            state["completed"] = True
            continue

        state["tool_results"].append(result)
        print(f"步骤 {state['step']}: {result}")
    return state


def main():
    final_state = run_agent("检查Log4Shell 影响资产")
    print(final_state)


if __name__ == "__main__":
    main()
