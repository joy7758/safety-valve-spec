#!/usr/bin/env python3
import json
try:
  from tools.svs_crypto import b64d, canonical_json, verify_ed25519, parse_rfc3339, utcnow
except ModuleNotFoundError:
  from svs_crypto import b64d, canonical_json, verify_ed25519, parse_rfc3339, utcnow

def verify_crl(crl: dict) -> tuple[bool,str]:
  try:
    root_pk = b64d(open("keys/root_ca.pk.b64","r",encoding="utf-8").read().strip())
    root_kid = open("keys/root_ca.kid","r",encoding="utf-8").read().strip()
  except Exception:
    return False, "SVS_CERT_WRONG_ISSUER"

  if crl.get("issuer_kid") != root_kid:
    return False, "SVS_CERT_WRONG_ISSUER"

  payload = dict(crl)
  sig_b64 = payload.pop("sig_b64", None)
  if not sig_b64:
    return False, "SVS_CERT_INVALID_SIGNATURE"

  if not verify_ed25519(root_pk, canonical_json(payload), b64d(sig_b64)):
    return False, "SVS_CERT_INVALID_SIGNATURE"

  # issued_at parse sanity
  try:
    _ = parse_rfc3339(crl.get("issued_at"))
  except Exception:
    return False, "SVS_TIME_RECEIPT_TIME_PARSE_ERROR"

  return True, "PASS"

def main():
  import sys
  if len(sys.argv)!=2:
    print("Usage: crl_verify.py <crl.json>")
    raise SystemExit(2)
  crl=json.load(open(sys.argv[1],"r",encoding="utf-8"))
  ok, code = verify_crl(crl)
  if ok:
    print("PASS")
    raise SystemExit(0)
  print(f"FAIL: {code}")
  raise SystemExit(1)

if __name__ == "__main__":
  main()
