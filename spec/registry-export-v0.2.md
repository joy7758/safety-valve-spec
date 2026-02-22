# Registry Export v0.2

## Goal
Define a minimal, deterministic export format that registry systems can ingest
without changing SVS v0.1 semantics.

## Versioning And Naming
- `spec_id`: `svs`
- `version`: `0.2`
- Type ID format: `svs:<TypeName>:v0.2`
- Reason code format: `SVS_<DOMAIN>_<NAME>` (same semantic namespace as v0.1)

## Export Files
- `registry/svs-types-v0.2.json`
- `registry/svs-reason-codes-v0.2.json`
- `registry/svs-profiles-v0.2.json`

Each export includes metadata:
- `spec_id`
- `export_version` (v0.2)
- `source_version` (v0.1)
- `generated_at` (deterministic value for reproducible output)
- `source_digest_sha256`

## Type Registry Payload (Minimal)
Each type entry MUST contain:
- `type_name`
- `type_id` (`svs:<TypeName>:v0.2`)
- `source_type_id` (`svs:<TypeName>:v0.1`)
- `purpose`
- `required_fields` (name + field spec)
- `optional_fields` (name + field spec)

## Reason Code Payload (Minimal)
Each reason code entry MUST contain:
- `code`
- `domain`

The export MAY also include grouped domain views for convenience.

## Profiles
A profile is a registry bundle for one integration use-case:
- Profile = set of `type_id`s + operational constraints + reason-code scope.
- v0.2 baseline profiles:
  - `ActionBoundaryGate`
  - `ReceiptVerifier`
  - `CompatIssuer`

Profiles are machine-readable in `registry/svs-profiles-v0.2.json`.

## Backward Compatibility
- v0.1 specs, schemas, semantics, and conformance expectations remain unchanged.
- v0.2 registry export is additive metadata for interoperability and registry
  submission.
- Implementations that only target v0.1 continue to be valid.
