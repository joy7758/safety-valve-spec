# svs-verify

Standalone verifier CLI for:
- SVS receipts (Ed25519 + SVS-CERT + optional CRL)
- SVS compatibility attestations

## Install (from repo root)
```bash
pip install -e packages/svs_verify
```

## Verify a receipt
```bash
svs-verify receipt path/to/receipt.json --root-kid <ROOT_KID> --root-pk-file keys/root_ca.pk.b64
```

With CRL:
```bash
svs-verify receipt path/to/receipt.json --root-kid <ROOT_KID> --root-pk-file keys/root_ca.pk.b64 --crl conformance/vectors/crl.active.json
```

## Verify an attestation
```bash
svs-verify attestation dist/svs-compat.attestation.json --root-pk-file keys/root_ca.pk.b64
```
