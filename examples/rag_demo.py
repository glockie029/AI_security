"""原最小 RAG 问答；需要可选依赖、模型权重及 API 配置。"""

from ai_security.rag.retrieval import rag_answer


def main():
    print(rag_answer("Java 日志组件中有哪些远程代码执行漏洞？"))


if __name__ == "__main__":
    main()
