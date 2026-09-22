# AI Operations Agent for Enterprise Certificates

## 1. Business Problem

An enterprise manages thousands of digital certificates used by devices and applications. Operations teams spend significant time manually performing repetitive and critical lifecycle tasks:
- **Checking certificate validity** and health across environments.
- **Looking up certificate details** (subject, issuer, serial, key size, algorithm, domains).
- **Verifying revocation status** (CRL / OCSP status).
- **Identifying expiring certificates** to prevent costly service outages.
- **Raising renewal actions** and ticket workflows for soon-to-expire or compromised certificates.

The goal is to build an **AI Agent** that can answer certificate-related operations questions and execute operational actions autonomously using tools.

---

## 2. Objective

Create an AI Agent capable of understanding natural language requests and executing tools to resolve operations workflows:

### Example User Queries
1. **Expiry Monitoring**: *"Show all certificates expiring in next 30 days"* / *"Show certificates expiring next month"*
2. **Status Inspection**: *"Check certificate ABC123 status"*
3. **Revocation Verification**: *"Verify if certificate XYZ789 is revoked"*
4. **Action / Renewal Automation**: *"Generate renewal request for certificate ABC123"*
5. **Ownership & Inventory**: *"List certificates belonging to Customer A"*

---

## 3. Mandatory Requirements

### Part 1 – Agent Architecture
Build an Agent that:
1. **Understands User Intent**: Parses natural language instructions, detects intent, extracts parameters (certificate IDs, date windows, customer identifiers).
2. **Executes Tools**:
   - `fetch_certificate(cert_id)`
   - `check_expiry(days_window)`
   - `verify_revocation(cert_id)`
   - `generate_renewal_request(cert_id, reason)`
   - `list_certificates_by_customer(customer_name)`
3. **Summarizes Results**: Provides clear, actionable, and human-friendly executive responses with structured data breakdowns.

---

### Part 2 – React UI
Provide an interactive, modern user interface:

```text
+-------------------------------------------------------+
|  AI Operations Agent - Enterprise Certificates        |
+-------------------------------------------------------+
|  [ User Question Input Box                       ] [Send] |
+-------------------------------------------------------+
|  Answer Window                                        |
|  - Clear agent response summary                       |
|  - Rendered data / status badge / action details      |
+-------------------------------------------------------+
|  Tool Calls Made:                                     |
|  1. fetch_certificate(cert_id="ABC123") -> SUCCESS   |
|  2. check_expiry(...) -> SUCCESS                      |
+-------------------------------------------------------+
|  Execution Time: 342ms                                |
+-------------------------------------------------------+
```

---

## 4. Deliverables & Execution Plan

> **Note**: Start with the **Flow Diagram** (Agent reasoning loop, tool invocation lifecycle, and UI state flow), followed by the complete backend and frontend implementation.