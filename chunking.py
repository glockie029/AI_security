import re
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

def chunk_text(text: str, size=100, overlap=20):
    if size <= 0 or not 0 <= overlap < size:
        raise ValueError("无效的切分参数")

    chunks = []
    step = size - overlap

    for start in range(0, len(text),step):
        chunk = text[start:start + size]

        if chunk.strip():
            chunks.append({
                "start": start,
                "end": start + len(chunk),
                "content": chunk
            })

        if start + size >= len(text):
            break
    return chunks

chunks = chunk_text(document)
for i, chunk in enumerate(chunks,1):
    print(f"\nChunk {i}")
    print(chunk["content"])


import re


def split_by_headings(text: str, cve_id: str):
    sections = re.split(
        r"(?=^## )",
        text,
        flags=re.MULTILINE
    )

    chunks = []

    for section in sections:
        section = section.strip()

        if not section:
            continue

        # 跳过文档一级标题
        if not section.startswith("## "):
            continue

        lines = section.splitlines()
        heading = lines[0].removeprefix("## ").strip()
        content = "\n".join(lines[1:]).strip()

        chunks.append({
            "cve_id": cve_id,
            "section": heading,
            "content": content
        })

    return chunks


result = split_by_headings(
    document,
    "CVE-2021-44228"
)

for chunk in result:
    print(chunk)



chunk_text(document, size=100, overlap=0)