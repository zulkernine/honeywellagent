import asyncio
from agent.tools import (
    fetch_certificate,
    list_expiring_certificates,
    verify_revocation,
    generate_renewal_request,
    list_certificates_by_customer,
    list_customers,
)
from database import get_db, close_db

async def run_tests():
    print("--- 1. Testing Empty / Missing ID ---")
    r1 = await fetch_certificate.ainvoke({"cert_id": ""})
    print("fetch_certificate(''):", r1)
    assert "error" in r1, "Should fail on empty cert_id"

    r2 = await verify_revocation.ainvoke({"cert_id": "   "})
    print("verify_revocation('   '):", r2)
    assert "error" in r2, "Should fail on whitespace cert_id"

    r3 = await generate_renewal_request.ainvoke({"cert_id": ""})
    print("generate_renewal_request(''):", r3)
    assert "error" in r3, "Should fail on empty renewal cert_id"

    print("\n--- 2. Testing Non-existent Cert ID ---")
    r4 = await fetch_certificate.ainvoke({"cert_id": "DOES_NOT_EXIST_XYZ"})
    print("fetch_certificate('DOES_NOT_EXIST_XYZ'):", r4)
    assert "error" in r4 and "not found" in r4["error"], "Should return not found error"

    r5 = await generate_renewal_request.ainvoke({"cert_id": "DOES_NOT_EXIST_XYZ"})
    print("generate_renewal_request('DOES_NOT_EXIST_XYZ'):", r5)
    assert "error" in r5 and "not found" in r5["error"], "Should return not found error"

    print("\n--- 3. Testing Special Regex Chars in Customer Name ---")
    r6 = await list_certificates_by_customer.ainvoke({"customer_name": "Acme (US) *["})
    print("list_certificates_by_customer('Acme (US) *['):", r6)
    assert isinstance(r6, list), "Should return clean list without regex crash"

    r7 = await list_certificates_by_customer.ainvoke({"customer_name": ""})
    print("list_certificates_by_customer(''):", r7)
    assert "error" in r7[0], "Should return error for empty customer name"

    print("\n--- 4. Testing Date Boundaries & Overflows ---")
    r8 = await list_expiring_certificates.ainvoke({"days": -10})
    print("list_expiring_certificates(days=-10):", r8)
    assert "error" in r8[0], "Should reject negative days"

    r9 = await list_expiring_certificates.ainvoke({"days": 999999})
    print(f"list_expiring_certificates(days=999999): returned {len(r9)} certificates (no crash)")
    assert isinstance(r9, list), "Should handle clamped days cleanly"

    print("\n--- 5. Testing Renewal on Revoked Cert ---")
    db = get_db()
    revoked_cert = await db.certificates.find_one({"is_revoked": True})
    if revoked_cert:
        r10 = await generate_renewal_request.ainvoke({"cert_id": revoked_cert["cert_id"]})
        print(f"generate_renewal_request for revoked cert {revoked_cert['cert_id']}:", r10)
        assert "error" in r10 and "revoked" in r10["error"].lower(), "Should reject renewal of revoked cert"
    else:
        print("No revoked cert found in DB to test.")

    print("\n--- ALL TESTS PASSED! ---")
    await close_db()

if __name__ == "__main__":
    asyncio.run(run_tests())
