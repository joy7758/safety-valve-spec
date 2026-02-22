#!/usr/bin/env python3
import json
try:
  from tools.svs_crypto import b64d, canonical_json, verify_ed25519
except ModuleNotFoundError:
  from svs_crypto import b64d, canonical_json, verify_ed25519

def main():
  import argparse
  ap = argparse.ArgumentParser()
  ap.add_argument("attestation", help="path to attestation json")
  args = ap.parse_args()

  att = json.load(open(args.attestation, "r", encoding="utf-8"))
  payload = dict(att)
  sig_b64 = payload.pop("sig_b64", None)
  if not sig_b64:
    print("FAIL: MISSING_SIG")
    raise SystemExit(1)

  # basic checks
  if payload.get("spec_id") != "svs" or payload.get("spec_version") != "0.1":
    print("FAIL: WRONG_SPEC")
    raise SystemExit(1)
  if payload.get("conformance", {}).get("overall") != "PASS":
    print("FAIL: NOT_PASS")
    raise SystemExit(1)

  root_pk = b64d(open("keys/root_ca.pk.b64", "r", encoding="utf-8").read().strip())
  ok = verify_ed25519(root_pk, canonical_json(payload), b64d(sig_b64))
  if not ok:
    print("FAIL: INVALID_SIGNATURE")
    raise SystemExit(1)

  print("PASS")
  raise SystemExit(0)

if __name__ == "__main__":
  main()
