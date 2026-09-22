"""
Standalone seed script — run directly to populate MongoDB with sample certificates.

Usage:
    python seed.py

Reads MONGODB_URI and MONGODB_DB_NAME from .env automatically.
Safe to run multiple times (upserts by cert_id).
"""
import asyncio
from datetime import datetime, timedelta, timezone
from pathlib import Path
from dotenv import load_dotenv
import os

# Load .env from same directory as this script
load_dotenv(Path(__file__).parent / ".env")

MONGODB_URI = os.getenv("MONGODB_URI")
MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME", "certagent")

from motor.motor_asyncio import AsyncIOMotorClient

now = datetime.now(timezone.utc)


# ── Helpers ────────────────────────────────────────────────────────────────────

def days(n: int) -> datetime:
    return now + timedelta(days=n)

def cert(
    cert_id, common_name, issuer, serial, customer, domain, san,
    expires_at, status="active", is_revoked=False,
    revocation_reason=None, revocation_date=None,
    env="production", key_size=2048, tags=None,
):
    return {
        "cert_id": cert_id,
        "subject": f"CN={common_name}",
        "issuer": issuer,
        "serial_number": serial,
        "customer_name": customer,
        "domain": domain,
        "san": san,
        "issued_at": now - timedelta(days=365),
        "expires_at": expires_at,
        "status": status,
        "is_revoked": is_revoked,
        "revocation_reason": revocation_reason,
        "revocation_date": revocation_date,
        "key_algorithm": "RSA",
        "key_size": key_size,
        "signature_algorithm": "SHA256withRSA",
        "environment": env,
        "tags": tags or ["tls"],
        "created_at": now,
        "updated_at": now,
    }


# ── Seed Data ──────────────────────────────────────────────────────────────────
#
#  Customers:
#   - Acme Corp          (Customer A) — large enterprise, mixed portfolio
#   - Shopify Demo Ltd   (Customer B) — e-commerce, Let's Encrypt heavy
#   - FinTech Corp       (Customer C) — payments, strict compliance
#   - HealthSys Inc      (Customer D) — HIPAA, EV certs
#   - LogistiQs Net      (Customer E) — IoT + API
#   - RetailVision       (Customer F) — newer customer, growing

CERTIFICATES = [

    # ════════════════════════════════════════════════════════════════════
    # EXPIRING THIS MONTH (within 30 days) — critical for demo queries
    # ════════════════════════════════════════════════════════════════════

    cert("ABC123", "api.acme.com", "DigiCert Global CA", "AA:01:00:01",
         "Acme Corp", "api.acme.com",
         ["api.acme.com", "api2.acme.com"],
         days(5), tags=["api", "tls"]),

    cert("ABC124", "login.acme.com", "DigiCert Global CA", "AA:01:00:02",
         "Acme Corp", "login.acme.com",
         ["login.acme.com"],
         days(3), tags=["auth", "tls"]),

    cert("ABC125", "cdn.acme.com", "Sectigo RSA CA", "AA:01:00:03",
         "Acme Corp", "cdn.acme.com",
         ["cdn.acme.com", "static.acme.com"],
         days(12), tags=["cdn", "tls"]),

    cert("DEF456", "checkout.shopifydemo.com", "Let's Encrypt Authority X3", "BB:02:00:01",
         "Shopify Demo Ltd", "checkout.shopifydemo.com",
         ["checkout.shopifydemo.com", "cart.shopifydemo.com"],
         days(6), tags=["ecommerce", "tls"]),

    cert("DEF457", "admin.shopifydemo.com", "Let's Encrypt Authority X3", "BB:02:00:02",
         "Shopify Demo Ltd", "admin.shopifydemo.com",
         ["admin.shopifydemo.com"],
         days(20), tags=["admin", "tls"]),

    cert("GHI789", "payments.fintechcorp.com", "GlobalSign Root CA", "CC:03:00:01",
         "FinTech Corp", "payments.fintechcorp.com",
         ["payments.fintechcorp.com", "pay.fintechcorp.com"],
         days(18), tags=["payments", "pci-dss", "tls"]),

    cert("JKL001", "portal.healthsys.io", "Entrust CA", "DD:04:00:01",
         "HealthSys Inc", "portal.healthsys.io",
         ["portal.healthsys.io", "www.healthsys.io"],
         days(25), tags=["portal", "tls", "hipaa"]),

    cert("CUS002", "api.retailvision.com", "DigiCert Global CA", "FF:06:00:02",
         "RetailVision", "api.retailvision.com",
         ["api.retailvision.com"],
         days(15), tags=["api", "tls"]),

    # Pending renewal (already flagged)
    cert("RNW001", "reports.fintechcorp.com", "GlobalSign Root CA", "CC:03:00:02",
         "FinTech Corp", "reports.fintechcorp.com",
         ["reports.fintechcorp.com"],
         days(8), status="pending_renewal", tags=["reports", "tls"]),

    # ════════════════════════════════════════════════════════════════════
    # VALID — EXPIRING IN 1–12 MONTHS (varied)
    # ════════════════════════════════════════════════════════════════════

    cert("ABC126", "mail.acme.com", "DigiCert Global CA", "AA:01:00:04",
         "Acme Corp", "mail.acme.com",
         ["mail.acme.com", "smtp.acme.com"],
         days(45), tags=["mail", "tls"]),

    cert("ABC127", "vpn.acme.com", "DigiCert Global CA", "AA:01:00:05",
         "Acme Corp", "vpn.acme.com",
         ["vpn.acme.com"],
         days(60), tags=["vpn", "tls"]),

    cert("WLD001", "*.acme.com", "DigiCert Global CA", "AA:01:00:06",
         "Acme Corp", "*.acme.com",
         ["*.acme.com", "acme.com"],
         days(90), tags=["wildcard", "tls"]),

    cert("ABC128", "iot.acme.com", "DigiCert Global CA", "AA:01:00:07",
         "Acme Corp", "iot.acme.com",
         ["iot.acme.com", "devices.acme.com"],
         days(270), tags=["iot", "tls"]),

    cert("ABC129", "dev.acme.com", "DigiCert Global CA", "AA:01:00:08",
         "Acme Corp", "dev.acme.com",
         ["dev.acme.com"],
         days(365), env="dev", tags=["dev"]),

    cert("DEF458", "store.shopifydemo.com", "Let's Encrypt Authority X3", "BB:02:00:03",
         "Shopify Demo Ltd", "store.shopifydemo.com",
         ["store.shopifydemo.com", "www.shopifydemo.com"],
         days(55), tags=["store", "tls"]),

    cert("DEF459", "api.shopifydemo.com", "Let's Encrypt Authority X3", "BB:02:00:04",
         "Shopify Demo Ltd", "api.shopifydemo.com",
         ["api.shopifydemo.com"],
         days(200), tags=["api", "tls"]),

    cert("GHI790", "api.fintechcorp.com", "GlobalSign Root CA", "CC:03:00:03",
         "FinTech Corp", "api.fintechcorp.com",
         ["api.fintechcorp.com", "v2.api.fintechcorp.com"],
         days(120), tags=["api", "tls"]),

    cert("WLD002", "*.fintechcorp.com", "GlobalSign Root CA", "CC:03:00:04",
         "FinTech Corp", "*.fintechcorp.com",
         ["*.fintechcorp.com", "fintechcorp.com"],
         days(150), tags=["wildcard", "tls"]),

    cert("GHI791", "www.fintechcorp.com", "GlobalSign Root CA", "CC:03:00:05",
         "FinTech Corp", "www.fintechcorp.com",
         ["www.fintechcorp.com", "fintechcorp.com"],
         days(300), tags=["web", "tls"]),

    cert("STU333", "ehr.healthsys.io", "Entrust CA", "DD:04:00:02",
         "HealthSys Inc", "ehr.healthsys.io",
         ["ehr.healthsys.io"],
         days(72), tags=["ehr", "tls", "hipaa"]),

    cert("EV001", "www.healthsys.io", "DigiCert EV CA G2", "DD:04:00:03",
         "HealthSys Inc", "www.healthsys.io",
         ["www.healthsys.io", "healthsys.io", "secure.healthsys.io"],
         days(365), key_size=4096, tags=["ev", "tls", "hipaa"]),

    cert("HIJ888", "internal.healthsys.io", "Entrust CA", "DD:04:00:04",
         "HealthSys Inc", "internal.healthsys.io",
         ["internal.healthsys.io"],
         days(300), env="staging", tags=["internal", "hipaa"]),

    cert("VWX444", "api.logistiqs.net", "Sectigo RSA CA", "EE:05:00:01",
         "LogistiQs Net", "api.logistiqs.net",
         ["api.logistiqs.net", "track.logistiqs.net"],
         days(80), tags=["api", "tls"]),

    cert("BCD666", "dashboard.logistiqs.net", "Sectigo RSA CA", "EE:05:00:02",
         "LogistiQs Net", "dashboard.logistiqs.net",
         ["dashboard.logistiqs.net"],
         days(200), tags=["dashboard", "tls"]),

    cert("EE5003", "iot.logistiqs.net", "Sectigo RSA CA", "EE:05:00:03",
         "LogistiQs Net", "iot.logistiqs.net",
         ["iot.logistiqs.net", "sensors.logistiqs.net"],
         days(365), tags=["iot", "tls"]),

    cert("CUS001", "app.retailvision.com", "DigiCert Global CA", "FF:06:00:01",
         "RetailVision", "app.retailvision.com",
         ["app.retailvision.com", "www.retailvision.com"],
         days(40), tags=["app", "tls"]),

    cert("CUS003", "admin.retailvision.com", "DigiCert Global CA", "FF:06:00:03",
         "RetailVision", "admin.retailvision.com",
         ["admin.retailvision.com"],
         days(180), tags=["admin", "tls"]),

    # ════════════════════════════════════════════════════════════════════
    # REVOKED
    # ════════════════════════════════════════════════════════════════════

    cert("XYZ789", "old-api.fintechcorp.com", "GlobalSign Root CA", "CC:03:00:09",
         "FinTech Corp", "old-api.fintechcorp.com",
         ["old-api.fintechcorp.com"],
         days(120), status="revoked", is_revoked=True,
         revocation_reason="keyCompromise",
         revocation_date=now - timedelta(days=10),
         tags=["api", "tls"]),

    cert("REV001", "legacy.shopifydemo.com", "Let's Encrypt Authority X3", "BB:02:00:09",
         "Shopify Demo Ltd", "legacy.shopifydemo.com",
         ["legacy.shopifydemo.com"],
         days(90), status="revoked", is_revoked=True,
         revocation_reason="superseded",
         revocation_date=now - timedelta(days=30),
         tags=["legacy", "tls"]),

    cert("REV002", "compromised.logistiqs.net", "Sectigo RSA CA", "EE:05:00:09",
         "LogistiQs Net", "compromised.logistiqs.net",
         ["compromised.logistiqs.net"],
         days(200), status="revoked", is_revoked=True,
         revocation_reason="cACompromise",
         revocation_date=now - timedelta(days=5),
         tags=["tls"]),

    cert("REV003", "old-portal.healthsys.io", "Entrust CA", "DD:04:00:09",
         "HealthSys Inc", "old-portal.healthsys.io",
         ["old-portal.healthsys.io"],
         days(60), status="revoked", is_revoked=True,
         revocation_reason="affiliationChanged",
         revocation_date=now - timedelta(days=15),
         tags=["portal", "hipaa"]),

    # ════════════════════════════════════════════════════════════════════
    # EXPIRED
    # ════════════════════════════════════════════════════════════════════

    cert("EXP001", "old.acme.com", "DigiCert Global CA", "AA:01:00:09",
         "Acme Corp", "old.acme.com",
         ["old.acme.com"],
         days(-10), status="expired", tags=["legacy"]),

    cert("EXP002", "beta.healthsys.io", "Entrust CA", "DD:04:00:08",
         "HealthSys Inc", "beta.healthsys.io",
         ["beta.healthsys.io"],
         days(-30), status="expired", env="staging", tags=["beta"]),

    cert("EXP003", "staging.logistiqs.net", "Sectigo RSA CA", "EE:05:00:08",
         "LogistiQs Net", "staging.logistiqs.net",
         ["staging.logistiqs.net"],
         days(-5), status="expired", env="staging", tags=["staging"]),
]


# ── Runner ─────────────────────────────────────────────────────────────────────

async def seed():
    print(f"🔗 Connecting to MongoDB: {MONGODB_DB_NAME}")
    client = AsyncIOMotorClient(MONGODB_URI)
    db = client[MONGODB_DB_NAME]

    # Create indexes
    print("📐 Creating indexes...")
    await db.certificates.create_index("cert_id", unique=True)
    await db.certificates.create_index("customer_name")
    await db.certificates.create_index("expires_at")
    await db.certificates.create_index("status")
    await db.sessions.create_index("session_id", unique=True)
    await db.messages.create_index("session_id")

    # Upsert certificates
    inserted = 0
    updated = 0
    for c in CERTIFICATES:
        result = await db.certificates.update_one(
            {"cert_id": c["cert_id"]},
            {"$setOnInsert": c},
            upsert=True,
        )
        if result.upserted_id:
            inserted += 1
        else:
            updated += 1

    client.close()

    total = len(CERTIFICATES)
    print(f"\n✅ Done! {total} certificates processed:")
    print(f"   ├── {inserted} inserted (new)")
    print(f"   └── {updated} skipped (already exist)")
    print()

    # Summary breakdown
    by_status = {}
    expiring_30 = 0
    for c in CERTIFICATES:
        s = c["status"]
        by_status[s] = by_status.get(s, 0) + 1
        if c["expires_at"] <= now + timedelta(days=30) and not c["is_revoked"] and s == "active":
            expiring_30 += 1

    customers = {}
    for c in CERTIFICATES:
        customers[c["customer_name"]] = customers.get(c["customer_name"], 0) + 1

    print("📊 Breakdown by status:")
    for s, count in sorted(by_status.items()):
        print(f"   ├── {s}: {count}")

    print(f"\n⚠️  Expiring within 30 days (active): {expiring_30}")

    print("\n🏢 Breakdown by customer:")
    for name, count in sorted(customers.items()):
        print(f"   ├── {name}: {count} certs")


if __name__ == "__main__":
    if not MONGODB_URI:
        print("❌ MONGODB_URI not set in .env — aborting.")
        exit(1)
    asyncio.run(seed())
