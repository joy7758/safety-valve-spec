#!/usr/bin/env python3
import json
import sys

try:
  from tools.verify_lib import VerifyConfig, verify_receipt_obj
except ModuleNotFoundError:
  from verify_lib import VerifyConfig, verify_receipt_obj


def main():
  if len(sys.argv) != 2:
    print("Usage: verify_receipt.py <receipt.json>", file=sys.stderr)
    raise SystemExit(2)

  r = json.load(open(sys.argv[1], "r", encoding="utf-8"))
  ok, code = verify_receipt_obj(r, VerifyConfig())
  if ok:
    print("PASS")
    raise SystemExit(0)
  print(f"FAIL: {code}")
  raise SystemExit(1)


if __name__ == "__main__":
  main()
