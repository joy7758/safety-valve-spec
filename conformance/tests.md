# Conformance Tests v0.1

An implementation is SVS-Compatible v0.1 if it passes ALL tests below.

## T01 No receipt, no action
- Attempt a protected action without receipt.
- Expected: reject (HTTP 401/403), reason_code=MISSING_RECEIPT.

## T02 Signature verification required
- Provide ALLOW receipt with valid signature.
- Expected: action proceeds.

## T03 Forged receipt rejected
- Provide fake JSON receipt with placeholder signature.
- Expected: reject, reason_code=INVALID_SIGNATURE.

## T04 Tamper detection
- Modify any field (effect/tool/amount/etc) after signing.
- Expected: reject, reason_code=SIGNATURE_MISMATCH.

## T05 Replay protection
- Reuse same receipt_id/nonce within replay window.
- Expected: reject, reason_code=REPLAY_DETECTED.

## T06 Time window enforcement
- Use issued_at outside allowed window.
- Expected: reject, reason_code=EXPIRED_RECEIPT.

## T07 Bypass path blocked
- Call action endpoint through any alternate path without receipt token.
- Expected: reject.

## T08 DENY receipts mandatory
- Trigger a policy denial.
- Expected: deny receipt emitted.

## T09 DEGRADE constraints enforced
- DEGRADE receipt should only allow limited behavior.
- Expected: no irreversible action; require human confirm or read-only.

## T10 Completeness accounting
- Request count must match receipt count for protected actions.
- Expected: missing receipts raise alert.

## Implementation Notes (v0.1 runner)
- Offline-verifiable now: T02, T03, T04, T05, T06, T08 (+ cert-chain extras X01..X03)
- Action-boundary (gateway demo) now implemented for: T01, T07, T09, T10

## Reason Code Requirement
All failures MUST emit SVS reason codes defined in `spec/reason-codes-v0.1.md`.
