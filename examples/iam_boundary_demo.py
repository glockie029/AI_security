
ORDERS = {
    "PO-A": {"tenant": "A", "status": "pending"},
    "PO-B": {"tenant": "B", "status": "pending"},
}

def server_approve(order_id, principal):
    order = ORDERS[order_id]

    if (
        principal["tenant"] != order["tenant"]
        or "approve" not in principal["scopes"]
    ):
        return "DENIED"

    order["status"] = "approved"
    return "APPROVED"


def host_call(model_args, trusted_session):
    # 模型不能决定调用者身份
    return server_approve(
        model_args["order_id"], trusted_session
    )


staff = {"user": "E001", "tenant": "A", "scopes": ["read"]}
finance = {"user": "FIN01", "tenant": "A", "scopes": ["approve"]}

print("forged:", host_call({
    "order_id": "PO-A",
    "user": "FIN01",
    "scopes": ["approve"]
}, staff))

print("allowed:", host_call(
    {"order_id": "PO-A"}, finance
))

print("cross:", host_call(
    {"order_id": "PO-B"}, finance
))

print("PO-B status:", ORDERS["PO-B"]["status"])
