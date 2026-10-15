"""保留原 ask/chat 命令；模型客户端不在模块导入时创建。"""

import json

import typer
from openai import OpenAIError
from prompt_toolkit import PromptSession
from prompt_toolkit.history import InMemoryHistory

from ai_security.config import get_client, get_model_name
from ai_security.evaluation.evaluator import evaluate_attack
from ai_security.tools.definitions import tool_definitions
from ai_security.tools.validation import validate_cve_id
from ai_security.tools.vulnerabilities import (
    get_vulnerability,
    get_vulnerability_poisoned,
)

app = typer.Typer()


@app.command()
def ask(questions: str):
    """单次提问。"""
    try:
        response = get_client().responses.create(
            model=get_model_name(),
            instructions="你是网络安全学习助手,请使用中文回答.",
            input=questions,
            store=False,
        )
        print("\n模型回答:")
        print(response.output_text)
        if response.usage:
            print(
                f"\nToken消耗:"
                f"输入 {response.usage.input_tokens} / "
                f"输出 {response.usage.output_tokens}"
            )
    except (OpenAIError, RuntimeError) as exc:
        typer.echo(f"请求失败: {exc}", err=True)
        raise typer.Exit(code=1)


@app.command()
def chat():
    """多轮对话，保留原课程调用流程及模拟拦截策略。"""
    client = get_client()
    model = get_model_name()
    messages = [{"role": "system", "content": "你是ai助手。"}]
    session = PromptSession(history=InMemoryHistory())

    print("进入对话模式，输入 exit 退出。")
    print(
        "已注册工具:",
        [item["function"]["name"] for item in tool_definitions],
    )
    while True:
        try:
            question = session.prompt("\nYou: ").strip()
        except KeyboardInterrupt:
            print()
            continue
        except EOFError:
            print("\n退出对话模式.")
            break

        if question.lower() in ("exit", "quit"):
            print("退出对话模式.")
            break
        if not question:
            continue
        try:
            question.encode("utf-8")
        except UnicodeEncodeError:
            typer.echo("输入包含无效字符，请重新输入。", err=True)
            continue

        messages.append({"role": "user", "content": question})
        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                tools=tool_definitions,
                tool_choice="auto",
            )
            message = response.choices[0].message
            answer = message.content
            if message.tool_calls:
                tool_calls_data = []
                execution_allowed = False
                state_changed = False
                messages.append(message.model_dump(exclude_none=True))

                for call in message.tool_calls:
                    name = call.function.name
                    args = json.loads(call.function.arguments)
                    tool_calls_data.append({"name": name, "arguments": args})

                    if name == "get_vulnerability":
                        cve_id = validate_cve_id(args["cve_id"])
                        result = get_vulnerability(cve_id)
                    elif name == "get_vulnerability_poisoned":
                        result = get_vulnerability_poisoned(args["cve_id"])
                    elif name == "update_vulnerability_status":
                        result = {"error": "Permission denied"}
                    else:
                        result = {"error": "不支持的工具"}
                    print("工具执行结果:", result)

                # 已知限制：这里只回填最后一个工具结果，见 README 待修项。
                # 本轮仅整理结构，不顺带改变原多工具协议处理行为。
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": call.id,
                        "content": json.dumps(result, ensure_ascii=False),
                    }
                )
                evaluation = evaluate_attack(
                    tool_calls=tool_calls_data,
                    execution_allowed=execution_allowed,
                    state_changed=state_changed,
                )
                print("\n安全评估结果:")
                print(json.dumps(evaluation, indent=2))

                final_response = client.chat.completions.create(
                    model=model, messages=messages
                )
                final_message = final_response.choices[0].message
                print("\nAI:", final_message.content)
                messages.append(
                    {"role": "assistant", "content": final_message.content}
                )
            else:
                print(f"\nAI:", message.content)

            # 保留原历史追加方式；工具轮 answer 可能为空，见 README。
            messages.append({"role": "assistant", "content": answer})
        except OpenAIError as exc:
            messages.pop()
            typer.echo(f"请求失败: {exc}", err=True)


if __name__ == "__main__":
    app()
