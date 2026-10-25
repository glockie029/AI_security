"""本地模拟：将高风险 Agent 工具请求绑定到一次性人工审批。无真实模型/MCP/身份服务。"""
import hashlib
import json
import time

TICKETS = {
    "LAB-01": {"tenant": "A", "status": "open"},
    "LAB-02": {"tenant": "A", "status": "open"},
}
AUDIT = []
OPERATOR = {"user": "E001", "tenant": "A", "scopes": ["ticket:close"]}
REQUEST = {
    "tool": "update_vulnerability_status",
    "arguments": {"ticket_id": "LAB-01", "status": "closed"},
}


def request_digest(request, principal):
    payload = {
        "tool": request["tool"],
        "arguments": request["arguments"],
        "user": principal["user"],
        "tenant": principal["tenant"],
    }
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode()).hexdigest()


def execute(request, principal, approval=None):
    tool = request.get("tool")
    args = request.get("arguments")
    ticket_id = args.get("ticket_id") if isinstance(args, dict) else None

    def reject(reason):
        AUDIT.append({"user": principal["user"], "tool": tool,
                      "ticket_id": ticket_id, "decision": "DENIED", "reason": reason})
        return f"DENIED:{reason}"

    if tool != "update_vulnerability_status":
        return reject("tool_not_allowed")
    if not isinstance(args, dict) or set(args) != {"ticket_id", "status"}:
        return reject("parameter_not_allowed")
    if args["status"] != "closed" or not isinstance(ticket_id, str):
        return reject("parameter_not_allowed")
    ticket = TICKETS.get(ticket_id)
    if not ticket or ticket["tenant"] != principal["tenant"]:
        return reject("resource_not_allowed")
    if "ticket:close" not in principal["scopes"]:
        return reject("scope_not_allowed")
    if approval is None:
        return reject("approval_missing")
    if approval["used"]:
        return reject("approval_used")
    if time.time() > approval["expires_at"]:
        return reject("approval_expired")
    if approval["digest"] != request_digest(request, principal):
        return reject("approval_mismatch")
    if ticket["status"] != "open":
        return reject("state_conflict")

    # 此处模拟 MCP Server 再次授权后的业务写入；真实服务必须独立实施校验。
    approval["used"] = True
    previous = ticket["status"]
    ticket["status"] = "closed"
    AUDIT.append({"user": principal["user"], "approver": approval["approver"],
                  "tool": tool, "ticket_id": ticket_id, "decision": "APPROVED",
                  "before": previous, "after": ticket["status"]})
    return "APPROVED"


def main():
    print("no_approval:", execute(REQUEST, OPERATOR))
    print("approval_request:", json.dumps(REQUEST, ensure_ascii=False))
    answer = input("模拟审批员 M001：输入 APPROVE 授权此操作（其他输入拒绝）：").strip()
    if answer != "APPROVE":
        print("human_denied: no business change")
        return

    # 仅模拟人的键盘确认；真实系统必须验证审批者身份并在服务端保存审批。
    approval = {"approver": "M001", "digest": request_digest(REQUEST, OPERATOR),
                "expires_at": time.time() + 60, "used": False}
    changed = {"tool": REQUEST["tool"],
               "arguments": {"ticket_id": "LAB-02", "status": "closed"}}
    print("changed_parameters:", execute(changed, OPERATOR, approval))
    print("approved_exact_request:", execute(REQUEST, OPERATOR, approval))
    print("replay:", execute(REQUEST, OPERATOR, approval))
    print("final_states:", json.dumps(TICKETS, ensure_ascii=False))
    print("audit:", json.dumps(AUDIT, ensure_ascii=False, indent=2))
    print("rollback_note: before=open 已记录；真实回滚需另行授权并校验当前状态")


if __name__ == "__main__":
    main()
