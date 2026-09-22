"""
Certificates router – CRUD + seed data.
GET    /api/certificates           – list all certs (with optional filters)
GET    /api/certificates/{cert_id} – single cert
POST   /api/certificates           – create cert
PATCH  /api/certificates/{cert_id} – update cert
POST   /api/certificates/seed      – seed demo data
"""
import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from database import get_db
from models.certificate import Certificate, CertificateCreate

router = APIRouter(prefix="/api/certificates", tags=["certificates"])
logger = logging.getLogger(__name__)


def _clean(doc: dict) -> dict:
    doc.pop("_id", None)
    for k, v in doc.items():
        if isinstance(v, datetime):
            doc[k] = v.isoformat()
    return doc


@router.get("", response_model=list[dict])
async def list_certificates(
    customer: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    limit: int = Query(100, le=500),
):
    db = get_db()
    query: dict = {}
    if customer:
        query["customer_name"] = {"$regex": customer, "$options": "i"}
    if status:
        query["status"] = status
    cursor = db.certificates.find(query).sort("expires_at", 1).limit(limit)
    docs = await cursor.to_list(length=limit)
    return [_clean(d) for d in docs]


@router.get("/{cert_id}", response_model=dict)
async def get_certificate(cert_id: str):
    db = get_db()
    doc = await db.certificates.find_one({"cert_id": cert_id.upper()})
    if not doc:
        raise HTTPException(status_code=404, detail=f"Certificate '{cert_id}' not found.")
    return _clean(doc)


@router.post("", response_model=dict, status_code=201)
async def create_certificate(cert: CertificateCreate):
    db = get_db()
    existing = await db.certificates.find_one({"cert_id": cert.cert_id.upper()})
    if existing:
        raise HTTPException(status_code=409, detail=f"Certificate '{cert.cert_id}' already exists.")
    now = datetime.utcnow()
    doc = cert.model_dump()
    doc["cert_id"] = doc["cert_id"].upper()
    doc["created_at"] = now
    doc["updated_at"] = now
    await db.certificates.insert_one(doc)
    return _clean(doc)


@router.patch("/{cert_id}", response_model=dict)
async def update_certificate(cert_id: str, updates: dict):
    db = get_db()
    updates["updated_at"] = datetime.utcnow()
    result = await db.certificates.find_one_and_update(
        {"cert_id": cert_id.upper()},
        {"$set": updates},
        return_document=True,
    )
    if not result:
        raise HTTPException(status_code=404, detail=f"Certificate '{cert_id}' not found.")
    return _clean(result)


@router.post("/seed", status_code=201)
async def seed_certificates():
    """Seed 30 sample certificates for demo purposes. Safe to call multiple times (upserts)."""
    from seed_data import SEED_CERTIFICATES
    db = get_db()
    inserted = 0
    for cert in SEED_CERTIFICATES:
        result = await db.certificates.update_one(
            {"cert_id": cert["cert_id"]},
            {"$setOnInsert": cert},
            upsert=True,
        )
        if result.upserted_id:
            inserted += 1
    # Create indexes
    await db.certificates.create_index("cert_id", unique=True)
    await db.certificates.create_index("customer_name")
    await db.certificates.create_index("expires_at")
    await db.certificates.create_index("status")
    await db.sessions.create_index("session_id", unique=True)
    await db.messages.create_index("session_id")
    return {"message": f"Seeded {inserted} new certificates (skipped existing)."}
