# Compatibility Attestation v0.1

## Goal
Provide a signed, machine-verifiable statement that an implementation is **SVS-Compatible** for a given spec version.

## Attestation Object (JSON)
- att_version: "0.1"
- att_id: string
- spec_id: "svs"
- spec_version: "0.1"
- issuer_kid: Root CA key id
- issued_at: RFC3339 UTC
- subject:
  - subject_kid: implementation kid
  - subject_cert_id: cert_id (from SVS-CERT)
- conformance:
  - report_path: string (optional)
  - overall: "PASS"
  - passed: [test_id...]
  - skipped: [test_id...]
- policy:
  - reason_codes_version: "0.1"
  - namespace_version: "0.1"
- sig_b64: base64(Ed25519 signature by issuer over canonical att payload excluding sig_b64)

## Verification Rules
1) Verify signature with Root CA public key.
2) spec_id/spec_version MUST match SVS spec.
3) conformance.overall MUST be PASS.
4) Subject must match the implementation certificate used to sign receipts (kid + cert_id).

## Notes
- This attestation is a **public artifact** and can be shared.
- Root private key MUST never be committed.
