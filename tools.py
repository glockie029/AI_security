
# tools.py
CVE_DATABASE = {
    "CVE-2021-44228": {
        "name": "Log4Shell",
        "severity": "Critical",
        "cvss": 10.0
    },
    "CVE-2024-3094": {
        "name": "XZ Utils Backdoor",
        "severity": "Critical",
        "cvss": 10.0
    }
}


def get_vulnerability(cve_id: str) -> dict:
    return CVE_DATABASE.get(
        cve_id.upper(),
        {"error": "未找到该漏洞"}
    )
