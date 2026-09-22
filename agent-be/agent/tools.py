"""
Certificate operation tools for the LangGraph ReAct agent.

All tools are async — LangGraph's ainvoke awaits them directly,
so Motor (async MongoDB) works cleanly with no event loop conflicts.
"""
from datetime import datetime, timedelta, timezone
from typing import Optional

from langchain_core.tools import tool

from database import get_db


def _serialize(doc: dict) -> dict:
    """Convert MongoDB document to JSON-serialisable dict."""
    if doc is None:
        return {}
    doc.pop("_id", None)
    for k, v in list(doc.items()):
        if isinstance(v, datetime):
            doc[k] = v.isoformat()
    return doc


# ── Tool 1 ─────────────────────────────────────────────────────────────────────

@tool
async def fetch_certificate(cert_id: str) -> dict:
    """
    Fetch full details of a certificate by its certificate ID (e.g. ABC123).
    Returns all certificate fields including status, expiry, issuer, and revocation info.
    """
    db = get_db()
    doc = await db.certificates.find_one({"cert_id": cert_id.upper()})
    return _serialize(doc) if doc else {"error": f"Certificate '{cert_id}' not found."}


# ── Tool 2 ─────────────────────────────────────────────────────────────────────

@tool
async def list_expiring_certificates(days: int = 30) -> list[dict]:
    """
    List all certificates expiring within the next N days (default 30).
    Use this for questions like 'show certs expiring next month' or 'expiring in 7 days'.
    Returns a list of certificates sorted by expiry date ascending.
    """
    db = get_db()
    now = datetime.now(timezone.utc)
    cutoff = now + timedelta(days=days)
    cursor = db.certificates.find(
        {
            "expires_at": {"$gte": now, "$lte": cutoff},
            "is_revoked": False,
            "status": {"$ne": "revoked"},
        }
    ).sort("expires_at", 1).limit(200)
    docs = await cursor.to_list(length=200)
    return [_serialize(d) for d in docs]


# ── Tool 3 ─────────────────────────────────────────────────────────────────────

@tool
async def verify_revocation(cert_id: str) -> dict:
    """
    Check the revocation status of a certificate by its ID.
    Returns whether it is revoked, the revocation reason, and revocation date if applicable.
    """
    db = get_db()
    doc = await db.certificates.find_one(
        {"cert_id": cert_id.upper()},
        {"cert_id": 1, "is_revoked": 1, "revocation_reason": 1,
         "revocation_date": 1, "status": 1, "_id": 0},
    )
    return _serialize(doc) if doc else {"error": f"Certificate '{cert_id}' not found."}


# ── Tool 4 ─────────────────────────────────────────────────────────────────────

@tool
async def generate_renewal_request(cert_id: str, reason: Optional[str] = None) -> dict:
    """
    Generate a renewal request for a certificate.
    Use this when the user asks to renew or raise a renewal action for a certificate.
    Returns the created renewal request details including the request ID.
    """
    import uuid
    db = get_db()

    cert = await db.certificates.find_one({"cert_id": cert_id.upper()})
    if not cert:
        return {"error": f"Certificate '{cert_id}' not found."}

    renewal_reason = reason or "Renewal requested by operations team"
    request_id = str(uuid.uuid4())
    now = datetime.utcnow()

    renewal_doc = {
        "request_id": request_id,
        "cert_id": cert_id.upper(),
        "status": "pending",
        "reason": renewal_reason,
        "requested_by": "admin",
        "created_at": now,
        "updated_at": now,
    }
    await db.renewal_requests.insert_one(renewal_doc)

    await db.certificates.update_one(
        {"cert_id": cert_id.upper()},
        {"$set": {"status": "pending_renewal", "updated_at": now}},
    )

    return {
        "message": "Renewal request created successfully.",
        "request_id": request_id,
        "cert_id": cert_id.upper(),
        "reason": renewal_reason,
        "status": "pending",
    }


# ── Tool 5 ─────────────────────────────────────────────────────────────────────

@tool
async def list_certificates_by_customer(customer_name: str) -> list[dict]:
    """
    List all certificates belonging to a specific customer.
    Use this for questions like 'show certificates for Acme Corp'.
    The search is case-insensitive and partial-match friendly.
    Returns certificates sorted by expiry date ascending.
    """
    db = get_db()
    cursor = db.certificates.find(
        {"customer_name": {"$regex": customer_name, "$options": "i"}}
    ).sort("expires_at", 1).limit(200)
    docs = await cursor.to_list(length=200)
    return [_serialize(d) for d in docs]


# ── Tool 6 ─────────────────────────────────────────────────────────────────────

@tool
async def list_customers() -> list[dict]:
    """
    List all unique customers (companies) that have certificates in the system.
    Use this for questions like 'who are our customers?', 'list all companies',
    or 'which customers do we manage certificates for?'.
    Returns each customer with a summary: total certs, active, expiring in 30 days, revoked.
    """
    db = get_db()
    now = datetime.now(timezone.utc)
    cutoff_30d = now + timedelta(days=30)
    pipeline = [
        {
            "$group": {
                "_id": "$customer_name",
                "total": {"$sum": 1},
                "active": {"$sum": {"$cond": [{"$eq": ["$status", "active"]}, 1, 0]}},
                "expiring_30d": {
                    "$sum": {
                        "$cond": [
                            {
                                "$and": [
                                    {"$eq": ["$status", "active"]},
                                    {"$lte": ["$expires_at", cutoff_30d]},
                                ]
                            },
                            1, 0,
                        ]
                    }
                },
                "revoked": {"$sum": {"$cond": [{"$eq": ["$is_revoked", True]}, 1, 0]}},
            }
        },
        {"$sort": {"_id": 1}},
    ]
    results = await db.certificates.aggregate(pipeline).to_list(length=200)
    return [
        {
            "customer_name": r["_id"],
            "total_certificates": r["total"],
            "active": r["active"],
            "expiring_in_30_days": r["expiring_30d"],
            "revoked": r["revoked"],
        }
        for r in results
    ]


# ── Exported list ──────────────────────────────────────────────────────────────

all_tools = [
    fetch_certificate,
    list_expiring_certificates,
    verify_revocation,
    generate_renewal_request,
    list_certificates_by_customer,
    list_customers,
]
