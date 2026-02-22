#!/usr/bin/env python3
"""
SVS v0.1 - receipt verifier (placeholder)
TODO:
- canonicalize JSON (remove signature, stable key order)
- verify Ed25519 signature (kid -> public key)
- enforce nonce + issued_at time window
"""
import json
import sys

def main():
  if len(sys.argv) != 2:
    print("Usage: verify_receipt.py <receipt.json>", file=sys.stderr)
    sys.exit(2)
  path = sys.argv[1]
  with open(path, "r", encoding="utf-8") as f:
    r = json.load(f)
  # Placeholder: always fail if signature looks placeholder
  sig = r.get("signature", {}).get("sig", "")
  if "PLACEHOLDER" in sig or sig in ("", "AAAA"):
    print("FAIL: INVALID_SIGNATURE")
    sys.exit(1)
  print("PASS")
  sys.exit(0)

if __name__ == "__main__":
  main()
