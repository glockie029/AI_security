"""RAG retrieval ACL demo: standard-library sparse vectors, no LLM or vector DB."""
from collections import Counter
from math import sqrt
import re

DOCS = [
    {"id": "B-SECRET", "tenant": "B", "groups": {"security"},
     "text": "incident severity remediation confidential", "source": "kb://B/incidents", "version": 2},
    {"id": "A-FINANCE", "tenant": "A", "groups": {"finance"},
     "text": "incident severity remediation finance report", "source": "kb://A/finance", "version": 4},
    {"id": "A-PUBLIC", "tenant": "A", "groups": {"security"},
     "text": "incident remediation overview", "source": "kb://A/security", "version": 3},
]

# A trusted session set by the backend, not by user input or model output.
PRINCIPAL = {"user": "E001", "tenant": "A", "groups": {"security"}}
QUERY = "incident severity remediation"


def embed(text):
    """Sparse word-count vectors ONLY as a transparent cosine-search stand-in."""
    return Counter(re.findall(r"[a-z0-9]+", text.lower()))


def similarity(a, b):
    x, y = embed(a), embed(b)
    dot = sum(v * y.get(k, 0) for k, v in x.items())
    norm_x = sqrt(sum(v * v for v in x.values()))
    norm_y = sqrt(sum(v * v for v in y.values()))
    return dot / (norm_x * norm_y) if norm_x and norm_y else 0.0


def authorized(doc, principal):
    return (doc["tenant"] == principal["tenant"]
            and bool(doc["groups"] & principal["groups"]))


def top_k(query, docs, k=2):
    return sorted(docs, key=lambda d: similarity(query, d["text"]), reverse=True)[:k]


def ids(docs):
    return [d["id"] for d in docs]


# Wrong: rank the entire shared index before enforcing ACL.
global_top2 = top_k(QUERY, DOCS)
late_filter = [d for d in global_top2 if authorized(d, PRINCIPAL)]

# Right: derive ACL from trusted session and restrict candidates BEFORE top-k.
visible = [d for d in DOCS if authorized(d, PRINCIPAL)]
secure_top2 = top_k(QUERY, visible)

# A request-supplied tenant is ignored; it cannot become the security principal.
model_args = {"query": QUERY, "tenant": "B"}
forged_tenant_result = top_k(model_args["query"], visible)

print("global_top2 (unsafe if sent to LLM):", ids(global_top2))
print("late_filter (recall may suffer):", ids(late_filter))
print("secure_prefilter:", ids(secure_top2))
print("model_forged_tenant:", ids(forged_tenant_result))
print("retrieval_audit:", [
    {"user": PRINCIPAL["user"], "doc": d["id"],
     "source": d["source"], "version": d["version"]}
    for d in secure_top2
])

assert ids(global_top2) == ["B-SECRET", "A-FINANCE"]
assert ids(late_filter) == []
assert ids(secure_top2) == ["A-PUBLIC"]
assert ids(forged_tenant_result) == ["A-PUBLIC"]
print("CHECKS_PASSED")
