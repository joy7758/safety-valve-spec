# Integration Guide v0.1 (SVS)

Spec: `svs` v0.1  
Goal: enforce **No Receipt → No Action**, with verifiable receipts + optional CRL revocation.

---

## What you integrate (minimum)
You only need two things:

1) **Receipt Verifier** (MUST)  
- Verify SVS-CERT chain (Root → Leaf)
- Verify receipt signature (Leaf)
- Enforce `reason_code` enum (schema lock)
- Enforce replay + time window
- (Optional) Enforce CRL revocation

2) **Action Boundary Gate** (MUST)  
- Any irreversible action endpoint requires a receipt token (recommended: `X-SVS-Receipt-B64`)
- Reject missing/invalid receipts with SVS reason codes

---

## Recommended transport
**HTTP header**:
- `X-SVS-Receipt-B64: <base64(utf8-json)>`

Why:
- stable across shells/CI
- avoids quoting issues

---

## Integration Patterns (choose one)

### Pattern A — Gateway / Proxy (RECOMMENDED)
Place SVS gate between caller and the system that performs side effects.

**Pros**
- hardest to bypass (central enforcement)
- easiest to audit (single choke point)
- best for B2B compliance / monetization

**Cons**
- requires routing changes / infra integration

**Minimum contract**
- gateway rejects missing receipt
- gateway verifies receipt before calling downstream action

---

### Pattern B — Sidecar (K8s / service mesh)
Attach SVS gate as a sidecar to the service that performs actions.

**Pros**
- strong enforcement with local proximity
- incremental rollout per service

**Cons**
- ops complexity (deployments, config)

---

### Pattern C — SDK / Library (fastest, but weakest)
Embed verifier into the application code path.

**Pros**
- easiest adoption for developers
- low infra friction

**Cons**
- easiest to bypass via alternate code paths
- requires stricter conformance tests for bypass detection

---

## Required behaviors (SVS-Compatible v0.1)
An implementation must pass SVS conformance suite and satisfy:

- **ALLOW/DENY/DEGRADE receipts** exist and are verifiable
- **DENY/DEGRADE still emit receipts**
- **Replay protection**: nonce+receipt_id re-use fails
- **Time window** enforced
- **Bypass blocked**: alternate endpoints cannot skip receipt
- **DEGRADE constraints** enforced at action boundary
- **Completeness accounting**: protected requests reconciled with verified receipts
- **Reason codes** MUST be SVS reason codes

---

## CRL Revocation (v0.1)
CRL is an **explicit verifier switch**:
- CLI: `python tools/verify_receipt.py <r.json> --crl <crl.json>`
- Gateway: configure verifier with an active CRL path (implementation choice)

Reason:
- avoids breaking baseline flows unintentionally

---

## What to publish (for adopters)
To claim compatibility in your repo:
1) run SVS conformance workflow
2) produce `svs-compat.attestation.json`
3) publish badge or attach artifacts to your release/CI

---

## Next steps
Use the Reference Pack (coming next) to get a working gateway + client demo in minutes.
