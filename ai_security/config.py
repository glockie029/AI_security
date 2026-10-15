"""集中读取项目配置，客户端仅在实际调用时创建。"""

import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def load_environment() -> None:
    """沿用原环境变量名，不覆盖调用方已经设置的环境变量。"""
    from dotenv import load_dotenv

    load_dotenv(PROJECT_ROOT / ".env", override=False)


def get_model_name() -> str:
    load_environment()
    return os.getenv("MODEL", "deepseek-flash")


def get_client():
    """按需创建客户端；导入、纯函数测试和查看帮助均不需要密钥。"""
    load_environment()
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        raise ValueError("DEEPSEEK_API_KEY 为空.")

    from openai import OpenAI

    return OpenAI(api_key=api_key, base_url=os.getenv("base_url"))
