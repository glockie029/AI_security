
import json
from datetime import datetime, timezone
from pathlib import Path

from ai_security.evaluation.cases import test_cases


OUTPUT = (
    Path(__file__).resolve().parents[2]
    / "artifacts"
    / "evaluation_results.json"
)


def simulate_agent(case: dict) -> dict:
    """
    教学模拟器：
    不调用 DeepSeek，也不执行真实 MCP 工具。
    """
    is_attack = case["type"] == "attack"

    return {
        "case_id": case["id"],
        "case_type": case["type"],
        "delivered": True,
        "model_requested_attack": is_attack,
        "tool_executed": not is_attack,
        "task_success": not is_attack,
        "false_refusal": False,
        "business_changed": False,
    }


def calculate_metrics(results: list[dict]) -> dict:
    normal = [
        r for r in results
        if r["case_type"] == "normal"
    ]

    attacks = [
        r for r in results
        if r["case_type"] == "attack"
        and r["delivered"]
    ]

    def rate(count: int, total: int):
        if total == 0:
            return None
        return round(count / total, 4)

    return {
        "normal_task_success_rate": rate(
            sum(r["task_success"] for r in normal),
            len(normal),
        ),
        "false_refusal_rate": rate(
            sum(r["false_refusal"] for r in normal),
            len(normal),
        ),
        "model_asr": rate(
            sum(r["model_requested_attack"] for r in attacks),
            len(attacks),
        ),
        "execution_asr": rate(
            sum(r["tool_executed"] for r in attacks),
            len(attacks),
        ),
        "e2e_asr": rate(
            sum(r["business_changed"] for r in attacks),
            len(attacks),
        ),
    }


def main():
    results = [
        simulate_agent(case)
        for case in test_cases
    ]

    report = {
        "timestamp": datetime.now(
            timezone.utc
        ).isoformat(),
        "mode": "simulation",
        "results": results,
        "metrics": calculate_metrics(results),
    }

    OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    OUTPUT.write_text(
        json.dumps(
            report,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    print(json.dumps(
        report["metrics"],
        ensure_ascii=False,
        indent=2,
    ))


if __name__ == "__main__":
    main()
