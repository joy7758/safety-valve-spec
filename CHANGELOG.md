# Changelog


---

# SVS v0.1.x Release

One-command demo + proofs:

```bash
git clone https://github.com/joy7758/safety-valve-spec.git
cd safety-valve-spec/examples/reference-pack
DEMO_WITH_CONFORMANCE=1 make demo
```

Artifacts (proofs) are written to:
- `examples/reference-pack/artifacts/`

Verify attestation:

```bash
pip install svs-verify
svs-verify attestation examples/reference-pack/artifacts/svs-compat.attestation.json --root-pk-file /path/to/root_ca.pk.b64
```
