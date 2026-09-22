"""
Quick smoke test for the AI Certificate Operations Agent API.
No asserts — just prints results to verify the agent is working end-to-end.

Usage:
    python test_agent.py
"""
import uuid
import json
import urllib.request
import urllib.error

BASE_URL = "http://localhost:8000"
SESSION_ID = str(uuid.uuid4())


def post(path: str, body: dict) -> dict:
    data = json.dumps(body).encode()
    req = urllib.request.Request(
        f"{BASE_URL}{path}",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return {"error": e.read().decode()}


def get(path: str) -> dict:
    try:
        with urllib.request.urlopen(f"{BASE_URL}{path}", timeout=10) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return {"error": e.read().decode()}


def divider(title: str):
    print(f"\n{'═' * 60}")
    print(f"  {title}")
    print('═' * 60)


def print_response(resp: dict):
    if "error" in resp:
        print(f"  ❌ ERROR: {resp['error']}")
        return
    print(f"  ⏱  Execution time : {resp.get('execution_time_ms', '?')} ms")
    print(f"  🔧 Tool calls     : {len(resp.get('tool_calls', []))}")
    for i, tc in enumerate(resp.get("tool_calls", []), 1):
        print(f"     {i}. {tc['tool_name']}({tc['args']}) → {tc['result_summary'][:80]}...")
    print(f"\n  💬 Answer:\n")
    for line in resp.get("answer", "").splitlines():
        print(f"     {line}")


# ── Health check ───────────────────────────────────────────────────────────────
divider("0. Health Check")
health = get("/health")
print(f"  Status : {health.get('status')}")
print(f"  Model  : {health.get('model')}")

# ── Test queries ───────────────────────────────────────────────────────────────
QUERIES = [
    "List all current customer names and how many certificates each has.",
    "Show all certificates expiring in the next 30 days.",
    "Check certificate ABC123 status.",
    "Verify if certificate XYZ789 is revoked.",
    "List certificates belonging to FinTech Corp.",
    "Generate a renewal request for certificate ABC123.",
]

for i, question in enumerate(QUERIES, 1):
    divider(f"Query {i}: {question}")
    resp = post(f"/api/chat/{SESSION_ID}", {"message": question})
    print_response(resp)

# ── Session history ────────────────────────────────────────────────────────────
divider("Session history check")
session = get(f"/api/sessions/{SESSION_ID}")
if "error" not in session:
    msgs = session.get("messages", [])
    print(f"  Session title : {session['session']['title']}")
    print(f"  Messages saved: {len(msgs)} (user + assistant turns)")
else:
    print(f"  ❌ {session['error']}")

print(f"\n{'═' * 60}")
print("  ✅ Smoke test complete")
print(f"{'═' * 60}\n")
