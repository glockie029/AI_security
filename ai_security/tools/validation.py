"""从原 CLI 提取的 CVE 参数校验，保持原校验规则。"""

import re


def validate_cve_id(cve_id: str) -> str:
    if not isinstance(cve_id, str):
        raise ValueError("CVE ID 必须是字符串.")
    cve_id = cve_id.upper()
    if not re.fullmatch(r"CVE-\d{4}-\d{4,}", cve_id):
        raise ValueError("非法 CVE 编号")
    return cve_id
