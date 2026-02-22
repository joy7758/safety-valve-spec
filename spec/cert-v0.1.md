# SVS Certificate v0.1 (Lightweight)

## Motivation
We need a scalable trust model:
- Implementations sign receipts with their own keys
- A root CA issues a signed certificate binding `kid -> public_key`

## Cert Object (JSON)
- cert_version: "0.1"
- cert_id: string
- subject_kid: string
- subject_public_key_b64: base64(raw_ed25519_public_key_32bytes)
- issuer_kid: string
- issued_at: RFC3339 UTC
- expires_at: RFC3339 UTC
- sig_b64: base64(Ed25519 signature by issuer over canonical cert payload excluding sig_b64)

## Verification
1) Verify cert signature with issuer public key
2) Check time validity
3) Use subject public key to verify receipt signatures
