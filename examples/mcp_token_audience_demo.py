
from datetime import datetime, timedelta, timezone
import jwt

# 仅用于本地实验，生产环境禁止硬编码密钥
SECRET = "LOCAL-DEMO-ONLY-not-for-production"
ISSUER = "https://auth.example.test"
MCP_AUD = "https://mcp.example.test/mcp"
BILLING_AUD = "https://billing.example.test"


def issue(audience, scope, expires_in=300):
    now = datetime.now(timezone.utc)
    return jwt.encode({
        "iss": ISSUER,
        "sub": "FIN01",
        "aud": audience,
        "scope": scope,
        "iat": now,
        "exp": now + timedelta(seconds=expires_in),
    }, SECRET, algorithm="HS256")


def check_mcp_token(token):
    try:
        claims = jwt.decode(
            token,
            SECRET,
            algorithms=["HS256"],
            issuer=ISSUER,
            audience=MCP_AUD,
            options={"require": ["iss", "sub", "aud", "exp"]},
        )
    except jwt.InvalidTokenError as exc:
        return f"401 invalid_token ({type(exc).__name__})"

    if "orders:approve" not in claims.get(
        "scope", ""
    ).split():
        return "403 insufficient_scope"

    # Token 合格不代表目标订单已授权
    return "TOKEN_OK (still requires resource authorization)"


cases = {
    "wrong_audience": issue(BILLING_AUD, "orders:approve"),
    "missing_scope": issue(MCP_AUD, "orders:read"),
    "valid_token": issue(MCP_AUD, "orders:approve"),
    "expired_token": issue(MCP_AUD, "orders:approve", -60),
}

for name, token in cases.items():
    print(name, "->", check_mcp_token(token))
