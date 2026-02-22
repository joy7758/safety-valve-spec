#!/usr/bin/env python3
import datetime
import json
import os
import uuid
from svs_crypto import (
  b64d,
  b64e,
  canonical_json,
  gen_ed25519_keypair,
  sign_ed25519,
  to_rfc3339,
  utcnow,
)


def main():
  os.makedirs("keys", exist_ok=True)

  # Load Root
  root_kid = open("keys/root_ca.kid", "r", encoding="utf-8").read().strip()
  root_sk = b64d(open("keys/root_ca.sk.b64", "r", encoding="utf-8").read().strip())

  # Create impl keypair
  impl_sk, impl_pk = gen_ed25519_keypair()
  subject_kid = "impl-kid-001"  # you can change per implementer

  issued_at = utcnow()
  expires_at = issued_at + datetime.timedelta(days=365)

  cert_payload = {
    "cert_version": "0.1",
    "cert_id": f"c-{uuid.uuid4()}",
    "subject_kid": subject_kid,
    "subject_public_key_b64": b64e(impl_pk),
    "issuer_kid": root_kid,
    "issued_at": to_rfc3339(issued_at),
    "expires_at": to_rfc3339(expires_at),
  }

  sig = sign_ed25519(root_sk, canonical_json(cert_payload))
  cert = dict(cert_payload)
  cert["sig_b64"] = b64e(sig)

  # Save
  open("keys/impl.sk.b64", "w", encoding="utf-8").write(b64e(impl_sk) + "\n")
  open("keys/impl.pk.b64", "w", encoding="utf-8").write(b64e(impl_pk) + "\n")
  open("keys/impl.kid", "w", encoding="utf-8").write(subject_kid + "\n")
  open("keys/impl.cert.json", "w", encoding="utf-8").write(json.dumps(cert, indent=2, ensure_ascii=False) + "\n")

  print("OK: issued implementation cert")
  print("  subject_kid:", subject_kid)
  print("  keys/impl.cert.json")
  print("  keys/impl.sk.b64 (KEEP SECRET)")


if __name__ == "__main__":
  main()
