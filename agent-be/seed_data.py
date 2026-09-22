"""
30 realistic sample certificates for demo/hackathon seeding.
Covers a range of: expiry windows, customers, statuses, revocations.
"""
from datetime import datetime, timedelta, timezone

now = datetime.now(timezone.utc)


def _cert(
    cert_id, subject, issuer, serial, customer, domain, san,
    days_from_now, status="active", is_revoked=False,
    revocation_reason=None, env="production", tags=None
):
    issued = now - timedelta(days=365)
    expires = now + timedelta(days=days_from_now)
    revocation_date = (now - timedelta(days=10)) if is_revoked else None
    return {
        "cert_id": cert_id,
        "subject": subject,
        "issuer": issuer,
        "serial_number": serial,
        "customer_name": customer,
        "domain": domain,
        "san": san,
        "issued_at": issued,
        "expires_at": expires,
        "status": status,
        "is_revoked": is_revoked,
        "revocation_reason": revocation_reason,
        "revocation_date": revocation_date,
        "key_algorithm": "RSA",
        "key_size": 2048,
        "signature_algorithm": "SHA256withRSA",
        "environment": env,
        "tags": tags or ["tls"],
        "created_at": now,
        "updated_at": now,
    }


SEED_CERTIFICATES = [
    # ── Expiring within 7 days ──────────────────────────────────────────────
    _cert("ABC123", "CN=api.acme.com", "DigiCert Global CA", "3A:B1:00:01",
          "Customer A", "api.acme.com", ["api.acme.com", "api2.acme.com"], 5,
          tags=["api", "tls"]),
    _cert("ABC124", "CN=login.acme.com", "DigiCert Global CA", "3A:B1:00:02",
          "Customer A", "login.acme.com", ["login.acme.com"], 3,
          tags=["auth", "tls"]),
    _cert("DEF456", "CN=checkout.shopify-demo.com", "Let's Encrypt", "4C:D2:00:01",
          "Customer B", "checkout.shopify-demo.com", ["checkout.shopify-demo.com"], 6,
          tags=["ecommerce", "tls"]),

    # ── Expiring within 8–30 days ────────────────────────────────────────────
    _cert("ABC125", "CN=cdn.acme.com", "Sectigo CA", "3A:B1:00:03",
          "Customer A", "cdn.acme.com", ["cdn.acme.com", "static.acme.com"], 12,
          tags=["cdn", "tls"]),
    _cert("GHI789", "CN=payments.fintech-corp.com", "GlobalSign", "5E:F3:00:01",
          "Customer C", "payments.fintech-corp.com", ["payments.fintech-corp.com"], 18,
          tags=["payments", "tls"]),
    _cert("GHI790", "CN=api.fintech-corp.com", "GlobalSign", "5E:F3:00:02",
          "Customer C", "api.fintech-corp.com", ["api.fintech-corp.com"], 21,
          tags=["api", "tls"]),
    _cert("JKL001", "CN=portal.healthsys.io", "Entrust CA", "6F:A4:00:01",
          "Customer D", "portal.healthsys.io", ["portal.healthsys.io", "www.healthsys.io"], 25,
          tags=["portal", "tls"]),
    _cert("DEF457", "CN=admin.shopify-demo.com", "Let's Encrypt", "4C:D2:00:02",
          "Customer B", "admin.shopify-demo.com", ["admin.shopify-demo.com"], 29,
          tags=["admin", "tls"]),

    # ── Expiring within 31–90 days ────────────────────────────────────────────
    _cert("MNO111", "CN=mail.acme.com", "DigiCert Global CA", "3A:B1:00:04",
          "Customer A", "mail.acme.com", ["mail.acme.com"], 45,
          tags=["mail", "tls"]),
    _cert("MNO112", "CN=vpn.acme.com", "DigiCert Global CA", "3A:B1:00:05",
          "Customer A", "vpn.acme.com", ["vpn.acme.com"], 60,
          tags=["vpn", "tls"]),
    _cert("PQR222", "CN=store.shopify-demo.com", "Let's Encrypt", "4C:D2:00:03",
          "Customer B", "store.shopify-demo.com", ["store.shopify-demo.com"], 55,
          tags=["store", "tls"]),
    _cert("STU333", "CN=ehr.healthsys.io", "Entrust CA", "6F:A4:00:02",
          "Customer D", "ehr.healthsys.io", ["ehr.healthsys.io"], 72,
          tags=["ehr", "hipaa"]),
    _cert("VWX444", "CN=api.logistiqs.net", "Sectigo CA", "7G:B5:00:01",
          "Customer E", "api.logistiqs.net", ["api.logistiqs.net", "track.logistiqs.net"], 80,
          tags=["api", "tls"]),

    # ── Valid long-term (>90 days) ────────────────────────────────────────────
    _cert("YZA555", "CN=www.fintech-corp.com", "GlobalSign", "5E:F3:00:03",
          "Customer C", "www.fintech-corp.com", ["www.fintech-corp.com"], 180,
          tags=["web", "tls"]),
    _cert("BCD666", "CN=dashboard.logistiqs.net", "Sectigo CA", "7G:B5:00:02",
          "Customer E", "dashboard.logistiqs.net", ["dashboard.logistiqs.net"], 200,
          tags=["dashboard", "tls"]),
    _cert("EFG777", "CN=iot.acme.com", "DigiCert Global CA", "3A:B1:00:06",
          "Customer A", "iot.acme.com", ["iot.acme.com", "devices.acme.com"], 270,
          tags=["iot", "tls"]),
    _cert("HIJ888", "CN=internal.healthsys.io", "Entrust CA", "6F:A4:00:03",
          "Customer D", "internal.healthsys.io", ["internal.healthsys.io"], 300,
          tags=["internal", "hipaa"], env="staging"),
    _cert("KLM999", "CN=dev.acme.com", "DigiCert Global CA", "3A:B1:00:07",
          "Customer A", "dev.acme.com", ["dev.acme.com"], 365,
          tags=["dev"], env="dev"),

    # ── Revoked certificates ────────────────────────────────────────────────
    _cert("XYZ789", "CN=old-api.fintech-corp.com", "GlobalSign", "5E:F3:00:04",
          "Customer C", "old-api.fintech-corp.com", ["old-api.fintech-corp.com"], 120,
          status="revoked", is_revoked=True, revocation_reason="keyCompromise",
          tags=["api", "tls"]),
    _cert("REV001", "CN=legacy.shopify-demo.com", "Let's Encrypt", "4C:D2:00:04",
          "Customer B", "legacy.shopify-demo.com", ["legacy.shopify-demo.com"], 90,
          status="revoked", is_revoked=True, revocation_reason="superseded",
          tags=["legacy", "tls"]),
    _cert("REV002", "CN=compromised.logistiqs.net", "Sectigo CA", "7G:B5:00:03",
          "Customer E", "compromised.logistiqs.net", ["compromised.logistiqs.net"], 200,
          status="revoked", is_revoked=True, revocation_reason="cACompromise",
          tags=["tls"]),

    # ── Expired certificates ────────────────────────────────────────────────
    _cert("EXP001", "CN=old.acme.com", "DigiCert Global CA", "3A:B1:00:08",
          "Customer A", "old.acme.com", ["old.acme.com"], -10,
          status="expired", tags=["legacy"]),
    _cert("EXP002", "CN=beta.healthsys.io", "Entrust CA", "6F:A4:00:04",
          "Customer D", "beta.healthsys.io", ["beta.healthsys.io"], -30,
          status="expired", tags=["beta"], env="staging"),

    # ── Pending renewal ─────────────────────────────────────────────────────
    _cert("RNW001", "CN=reports.fintech-corp.com", "GlobalSign", "5E:F3:00:05",
          "Customer C", "reports.fintech-corp.com", ["reports.fintech-corp.com"], 8,
          status="pending_renewal", tags=["reports", "tls"]),

    # ── Customer F (new customer, fewer certs) ──────────────────────────────
    _cert("CUS001", "CN=app.retailvision.com", "DigiCert Global CA", "8H:C6:00:01",
          "Customer F", "app.retailvision.com", ["app.retailvision.com", "www.retailvision.com"], 40,
          tags=["app", "tls"]),
    _cert("CUS002", "CN=api.retailvision.com", "DigiCert Global CA", "8H:C6:00:02",
          "Customer F", "api.retailvision.com", ["api.retailvision.com"], 15,
          tags=["api", "tls"]),

    # ── Wildcard certificates ───────────────────────────────────────────────
    _cert("WLD001", "CN=*.acme.com", "DigiCert Global CA", "3A:B1:00:09",
          "Customer A", "*.acme.com", ["*.acme.com", "acme.com"], 90,
          tags=["wildcard", "tls"]),
    _cert("WLD002", "CN=*.fintech-corp.com", "GlobalSign", "5E:F3:00:06",
          "Customer C", "*.fintech-corp.com", ["*.fintech-corp.com", "fintech-corp.com"], 150,
          tags=["wildcard", "tls"]),

    # ── EV certificate ──────────────────────────────────────────────────────
    _cert("EV001", "CN=www.healthsys.io O=HealthSys Inc", "DigiCert EV CA", "6F:A4:00:05",
          "Customer D", "www.healthsys.io",
          ["www.healthsys.io", "healthsys.io", "secure.healthsys.io"], 365,
          tags=["ev", "tls", "hipaa"]),
]
