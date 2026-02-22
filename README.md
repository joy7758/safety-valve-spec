# Safety Valve Spec (SVS)

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
