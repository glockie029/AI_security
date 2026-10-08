import os
import json

import typer
from dotenv import load_dotenv
from openai import OpenAI,OpenAIError
from tools import get_vulnerability
import tools

load_dotenv()
app = typer.Typer()
MODEL = os.getenv("MODEL","deepseek-flash")
client = OpenAI(api_key=os.getenv("DEEPSEEK_API_KEY"),base_url=os.getenv("base_url"))

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_vulnerability",
            "description": "查询指定 CVE 的漏洞信息",
            "parameters": {
                "type": "object",
                "properties": {
                    "cve_id": {
                        "type": "string",
                        "description": "CVE 编号"
                    }
                },
                "required": ["cve_id"]
            }
        }
    }
]

def get_client():
    if not os.getenv("DEEPSEEK_API_KEY"):
        raise ValueError("DEEPSEEK_API_KEY 为空.")
    return OpenAI(api_key=os.getenv("DEEPSEEK_API_KEY"),base_url=os.getenv("base_url"))

@app.command()
def ask():
    """单次提问"""
    try:
        response = get_client().responses.create(
            model=MODEL,
            instructions="你是网络安全学习助手,请使用中文回答.",
            input=question,
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
    except (OpenAIError,RuntimeError) as e:
        typer.echo(f"请求失败: {e}", err=True)
        raise typer.Exit(code=1)

@app.command()
def chat():
    """多轮对话"""
    client = get_client()
    
    messages = [{"role": "system", "content": "你是网络安全学习助手，请使用中文回答。"}]
    
    print("进入对话模式,输入exit退出.")
    
    while True:
        question = input("\nYou: ").strip()
        if question.lower() in ("exit", "quit"):
            print("退出对话模式.")
            break

        if not question:
            continue

        messages.append({"role": "user", "content": question})
        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=messages,
                tools=tools,
                tool_choice="auto"
            )
            answer = response.choices[0].message.content

            message = response.choices[0].message

            if message.tool_calls:
                for call in message.tool_calls:
                    print("工具名称",call.function.name)
                    print("工具参数",call.function.arguments)
            else:
                print("AI:",message.content)
            print(f"\nAI: {answer}")

            messages.append({
                "role": "assistant",
                "content": answer
            })

        except OpenAIError as e:
            messages.pop()
            typer.echo(f"请求失败: {e}", err=True)
            
if __name__ == "__main__":
    app()