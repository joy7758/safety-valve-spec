#!/usr/bin/env python3
import json, uuid
try:
  from tools.svs_crypto import utcnow, to_rfc3339, b64d, b64e, canonical_json, sign_ed25519
except ModuleNotFoundError:
  from svs_crypto import utcnow, to_rfc3339, b64d, b64e, canonical_json, sign_ed25519

def main():
  import sys
  if len(sys.argv) < 3:
    print("Usage: crl_generate.py <out_crl.json> <subject_kid> [subject_kid...]")
    raise SystemExit(2)

  out_path = sys.argv[1]
  subjects = sys.argv[2:]

  root_kid = open("keys/root_ca.kid","r",encoding="utf-8").read().strip()
  root_sk = b64d(open("keys/root_ca.sk.b64","r",encoding="utf-8").read().strip())

  now = utcnow()
  payload = {
    "crl_version": "0.1",
    "crl_id": f"crl-{uuid.uuid4()}",
    "issuer_kid": root_kid,
    "issued_at": to_rfc3339(now),
    "entries": [
      {"subject_kid": sk, "revoked_at": to_rfc3339(now), "reason": "revoked by issuer"} for sk in subjects
    ],
  }
  sig = sign_ed25519(root_sk, canonical_json(payload))
  crl = dict(payload)
  crl["sig_b64"] = b64e(sig)

  json.dump(crl, open(out_path,"w",encoding="utf-8"), indent=2, ensure_ascii=False)
  print("OK:", out_path)

if __name__ == "__main__":
  main()
