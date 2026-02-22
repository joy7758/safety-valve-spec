#!/usr/bin/env python3
import copy
import json
import os
from svs_crypto import b64d, canonical_json, parse_rfc3339, utcnow, verify_ed25519

REPLAY_DB = "conformance/state/seen_nonces.json"
TIME_WINDOW_SECONDS = 300  # 5 min default


def load_seen():
  if not os.path.exists(REPLAY_DB):
    return {"nonces": {}}
  return json.load(open(REPLAY_DB, "r", encoding="utf-8"))


def save_seen(db):
  os.makedirs(os.path.dirname(REPLAY_DB), exist_ok=True)
  json.dump(db, open(REPLAY_DB, "w", encoding="utf-8"), indent=2, ensure_ascii=False)


def fail(code: str):
  print(f"FAIL: {code}")
  raise SystemExit(1)


def main():
  import sys

  if len(sys.argv) != 2:
    print("Usage: verify_receipt.py <receipt.json>")
    raise SystemExit(2)

  r = json.load(open(sys.argv[1], "r", encoding="utf-8"))
  sig = r.get("signature") or {}
  if sig.get("alg") != "Ed25519":
    fail("UNSUPPORTED_ALG")

  cert = sig.get("cert")
  if not cert:
    fail("MISSING_CERT")

  # Load Root PK
  root_pk = b64d(open("keys/root_ca.pk.b64", "r", encoding="utf-8").read().strip())
  root_kid = open("keys/root_ca.kid", "r", encoding="utf-8").read().strip()

  # Verify cert issuer
  if cert.get("issuer_kid") != root_kid:
    fail("CERT_WRONG_ISSUER")

  # Verify cert signature
  cert_payload = dict(cert)
  cert_sig_b64 = cert_payload.pop("sig_b64", None)
  if not cert_sig_b64:
    fail("CERT_MISSING_SIG")
  if not verify_ed25519(root_pk, canonical_json(cert_payload), b64d(cert_sig_b64)):
    fail("CERT_INVALID_SIGNATURE")

  # Cert time validity
  now = utcnow()
  ia = parse_rfc3339(cert.get("issued_at"))
  ea = parse_rfc3339(cert.get("expires_at"))
  if not (ia <= now <= ea):
    fail("CERT_EXPIRED")

  # Receipt time window check
  issued_at = parse_rfc3339(r.get("issued_at"))
  delta = abs((now - issued_at).total_seconds())
  if delta > TIME_WINDOW_SECONDS:
    fail("EXPIRED_RECEIPT")

  # Replay check (nonce+receipt_id)
  nonce = r.get("nonce", "")
  rid = r.get("receipt_id", "")
  key = f"{rid}:{nonce}"
  db = load_seen()
  if key in db["nonces"]:
    fail("REPLAY_DETECTED")
  db["nonces"][key] = r.get("issued_at")
  save_seen(db)

  # Verify receipt signature with subject pubkey from cert
  subject_pk = b64d(cert.get("subject_public_key_b64"))
  payload = copy.deepcopy(r)
  payload.pop("signature", None)
  receipt_sig = sig.get("sig")
  if not receipt_sig:
    fail("MISSING_RECEIPT_SIG")
  if not verify_ed25519(subject_pk, canonical_json(payload), b64d(receipt_sig)):
    fail("INVALID_SIGNATURE")

  print("PASS")
  raise SystemExit(0)


if __name__ == "__main__":
  main()
