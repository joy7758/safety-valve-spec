# Namespace v0.1

## Goal
Prevent semantic drift and name collisions across ecosystems.

## Recommended Namespace
- spec_id: `svs`
- version: `0.1`
- type_id format: `svs:<type>:v0.1`
- reason_code format: `SVS_<DOMAIN>_<NAME>`

Examples:
- `svs:AuditReceipt:v0.1`
- `svs:PolicyDecision:v0.1`
- `SVS_SIG_INVALID_SIGNATURE`

## Rules
1) New fields MUST be additive in v0.x.
2) Field semantics MUST NOT change without a new major version.
3) Implementations claiming compatibility MUST use these identifiers verbatim.
