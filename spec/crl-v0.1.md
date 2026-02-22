# CRL (Certificate Revocation List) v0.1

## Goal
Allow verifiers to reject receipts signed by certificates that have been revoked.

## CRL Object (JSON)
- crl_version: "0.1"
- crl_id: string
- issuer_kid: Root CA key id
- issued_at: RFC3339 UTC
- entries: array of revocations
  - subject_kid: string
  - revoked_at: RFC3339 UTC
  - reason: string (free text; optional)
- sig_b64: base64(Ed25519 signature by Root CA over canonical CRL payload excluding sig_b64)

## Verification Rules
1) Verify CRL signature with Root CA public key
2) Check issuer_kid matches Root
3) If receipt.signature.kid matches any entry.subject_kid => reject with `SVS_CERT_REVOKED`

## Distribution
- v0.1 treats CRL as an out-of-band artifact accessible to verifiers (file/URL).
- Implementations MAY embed CRL references in policies, but revocation decision is always verifier-side.
