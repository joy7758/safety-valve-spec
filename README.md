# Safety Valve Spec (SVS)

<!-- SVS_BADGE_BEGIN -->
![SVS Compatible](dist/svs-compat.badge.svg)

```bash
python tools/compat_verify.py dist/svs-compat.attestation.json
```
<!-- SVS_BADGE_END -->


A minimal, verifiable **Audit Receipt** standard + **Conformance Tests** for AI/Agent actions.

## What this is
- A **receipt format** (JSON) that can be cryptographically verified.
- A **policy gate contract**: no receipt → no real-world action.
- A **conformance test suite**: pass the tests → claim compatibility.

## Compatibility
An implementation is **SVS-Compatible** if it:
1) produces verifiable receipts for ALLOW/DENY/DEGRADE,
2) enforces "no receipt, no action" at the action boundary,
3) passes the conformance tests in `conformance/tests.md`.

## Quick Start
- Spec: `spec/receipt-v0.1.md`
- JSON Schema: `schemas/receipt.v0.1.json`
- Test plan: `conformance/tests.md`
- Verify tool: `tools/verify_receipt.py`

> v0.1 focuses on **action-boundary enforcement** and **receipt verifiability**.

## CA Mode (recommended)
- Root CA issues an SVS certificate binding `kid -> public_key`.
- Implementations sign receipts with their own keys and embed the cert.
- Verifiers validate: cert signature (root) -> receipt signature (leaf) -> nonce/time-window.

### Commands
```bash
source .venv/bin/activate
python tools/ca_generate_root.py
python tools/ca_issue_cert.py
python tools/receipt_sign.py examples/allow.receipt.json examples/signed/allow.receipt.signed.json
python tools/verify_receipt.py examples/signed/allow.receipt.signed.json
```

## Conformance
Run all conformance tests locally:
```bash
source .venv/bin/activate
bash conformance/run.sh
cat conformance/report.json
```

Note:
- T01/T07/T09/T10 are now covered by the gateway action-boundary demo in `conformance/run.sh`.

## Gateway Demo (action-boundary)
Run the gateway:
```bash
source .venv/bin/activate
python -m uvicorn demo.gateway_server:app --host 127.0.0.1 --port 8089
```
Conformance runner will start/stop it automatically:
```bash
bash conformance/run.sh
```

### Recommended transport
Use `X-SVS-Receipt-B64` header (base64-encoded UTF-8 JSON) to avoid quoting issues across shells/CI.

## Revocation (CRL)
SVS supports CRL v0.1 (signed by Root CA). Verifiers may load an active CRL and reject revoked `kid`s.
- Spec: `spec/crl-v0.1.md`
- Tooling: `tools/crl_generate.py`, `tools/crl_verify.py`

## Compatibility Attestation
After conformance passes, SVS can emit a signed compatibility attestation:
- Spec: `spec/compat-attestation-v0.1.md`
- Emit: `python tools/compat_emit.py --report conformance/report.json --out dist/svs-compat.attestation.json`
- Verify: `python tools/compat_verify.py dist/svs-compat.attestation.json`

Conformance runner does this automatically and outputs `dist/svs-compat.attestation.json`.

<!-- SVS_REUSABLE_WORKFLOW_BEGIN -->
## Reusable Conformance Workflow (for other repos)

Other repositories can reuse this conformance workflow:

```yaml
name: svs-check
on:
  push:
  pull_request:

jobs:
  svs:
    uses: <OWNER>/<REPO>/.github/workflows/svs-conformance.yml@<REF>
```

It uploads artifacts:
- conformance/report.json
- dist/svs-compat.attestation.json
- dist/svs-compat.badge.svg
- dist/svs-compat.badge.md
<!-- SVS_REUSABLE_WORKFLOW_END -->
