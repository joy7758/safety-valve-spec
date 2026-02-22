# SVS Registry Export (v0.2)

This directory contains deterministic, machine-readable registry artifacts
derived from SVS v0.1 source docs.

## Files
- `svs-types-v0.2.json`: type dictionary export
- `svs-reason-codes-v0.2.json`: reason-code export
- `svs-profiles-v0.2.json`: profile bundles for common integrations

## Source Of Truth
- `spec/objects-v0.1.md`
- `spec/reason-codes-v0.1.md`

## Generation
Run:

```bash
python tools/registry_export.py
```

The generator is deterministic and writes only inside `registry/`.

## Registry Submission
For registry-like systems (including type registries), submit:
1. `registry/svs-types-v0.2.json`
2. `registry/svs-reason-codes-v0.2.json`
3. `registry/svs-profiles-v0.2.json`
4. `spec/registry-export-v0.2.md` (human-readable contract)

## Compatibility Note
This export is additive for v0.2 registry integration. It does not alter SVS
v0.1 runtime semantics or conformance behavior.
