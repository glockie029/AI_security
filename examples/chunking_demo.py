"""原固定长度/标题切分演示，示例资料与算法分开保存。"""

from ai_security.rag.chunking import chunk_text, split_by_headings

document = """
# CVE-2021-44228

## 漏洞描述
Log4Shell 是 Apache Log4j 2 的一项
远程代码执行漏洞。

## 受影响版本
Log4j 2.0-beta9 至 2.14.1
受到该漏洞影响。

## 修复建议
建议升级到适用于当前环境的
安全修复版本。

## 验证方法
检查实际加载的 Log4j 组件版本，
并重新执行安全检测。
"""


def main():
    chunks = chunk_text(document)
    for index, chunk in enumerate(chunks, 1):
        print(f"\nChunk {index}")
        print(chunk["content"])

    for chunk in split_by_headings(document, "CVE-2021-44228"):
        print(chunk)

    # 保留原课程的无重叠切分调用。
    chunk_text(document, size=100, overlap=0)


if __name__ == "__main__":
    main()
