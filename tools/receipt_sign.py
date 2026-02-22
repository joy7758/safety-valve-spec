#!/usr/bin/env python3
import copy
import json
from svs_crypto import b64d, b64e, canonical_json, sign_ed25519


def main():
  import sys

  if len(sys.argv) != 3:
    print("Usage: receipt_sign.py <in_receipt.json> <out_receipt.json>")
    raise SystemExit(2)

  in_path, out_path = sys.argv[1], sys.argv[2]
  r = json.load(open(in_path, "r", encoding="utf-8"))

  impl_sk = b64d(open("keys/impl.sk.b64", "r", encoding="utf-8").read().strip())
  impl_kid = open("keys/impl.kid", "r", encoding="utf-8").read().strip()
  cert = json.load(open("keys/impl.cert.json", "r", encoding="utf-8"))

  # prepare payload to sign: receipt without signature
  payload = copy.deepcopy(r)
  payload.pop("signature", None)

  sig = sign_ed25519(impl_sk, canonical_json(payload))

  r["signature"] = {
    "alg": "Ed25519",
    "kid": impl_kid,
    "sig": b64e(sig),
    "cert": cert,
  }

  json.dump(r, open(out_path, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
  print("OK: signed receipt ->", out_path)


if __name__ == "__main__":
  main()
