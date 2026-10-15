"""仅检查引用编号是否属于检索结果，不判断证据是否支持结论。"""

import re


def validate_citations(answer: str, results: list) -> dict:
    cited_ids = set(re.findall(r"\[(DOC-\d+)\]", answer))
    valid_ids = {result["source"] for result in results}
    return {
        "cited_ids": sorted(cited_ids),
        "invalid_ids": sorted(cited_ids - valid_ids),
        "valid": bool(cited_ids) and cited_ids <= valid_ids,
    }
