# Audit Receipt Spec v0.1

## Goal
At the **action boundary**, enforce:
- No receipt -> no action
- Receipts are **verifiable** (signature)
- ALLOW / DENY / DEGRADE all produce receipts

## Receipt Fields (minimal)

### Signature CA Mode (additive)
In CA mode, the receipt includes an embedded SVS-CERT:
- signature.cert: SVS Certificate JSON
- signature.sig: base64 signature by subject private key over canonical receipt payload


- receipt_version: "0.1"
- receipt_id: UUID
- issued_at: RFC3339 UTC timestamp
- nonce: random string to prevent replay
- actor: { type, id }
- agent: { name, version, model? }
- intent: { intent_id, scope? }
- policy: { policy_id, policy_version }
- tool: { name, action_type }
- action: { action_id, params_digest }
- context_digest: hash of relevant input context
- output_digest: hash of output (required for ALLOW/DEGRADE)
- decision:
  - effect: ALLOW | DENY | DEGRADE
  - reason_code: enum string
  - constraints: optional, e.g. { requires_human_confirm, max_amount, read_only }
- evidence_refs: optional array of { evidence_type, digest, uri? }
- signature:
  - alg: "Ed25519"
  - kid: key id
  - sig: base64 signature over canonical payload

## MUST Rules
1) DENY/DEGRADE MUST also generate receipts.
2) Action endpoints MUST require a receipt token (or embedded receipt) to execute.
3) Signature MUST be verified before executing ALLOW/DEGRADE actions.
4) nonce + issued_at MUST be checked (replay + time window).
5) policy_version MUST be traceable and included.

## Canonicalization
- Canonical payload = receipt JSON without `signature`, with stable key order.

## Identifiers
- Spec ID: `svs`
- Receipt Type ID: `svs:AuditReceipt:v0.1`
- Decision Type ID: `svs:PolicyDecision:v0.1`
