"""原课程中的固定长度切分与标题切分算法。"""

import re


def chunk_text(text: str, size=100, overlap=20):
    if size <= 0 or not 0 <= overlap < size:
        raise ValueError("无效的切分参数")

    chunks = []
    step = size - overlap
    for start in range(0, len(text), step):
        chunk = text[start : start + size]
        if chunk.strip():
            chunks.append(
                {
                    "start": start,
                    "end": start + len(chunk),
                    "content": chunk,
                }
            )
        if start + size >= len(text):
            break
    return chunks


def split_by_headings(text: str, cve_id: str):
    sections = re.split(r"(?=^## )", text, flags=re.MULTILINE)
    chunks = []
    for section in sections:
        section = section.strip()
        if not section:
            continue
        if not section.startswith("## "):
            continue

        lines = section.splitlines()
        heading = lines[0].removeprefix("## ").strip()
        content = "\n".join(lines[1:]).strip()
        chunks.append(
            {"cve_id": cve_id, "section": heading, "content": content}
        )
    return chunks
