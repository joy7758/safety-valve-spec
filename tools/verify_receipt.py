#!/usr/bin/env python3
import json, sys
try:
  from tools.verify_lib import verify_receipt_obj, VerifyConfig
except ModuleNotFoundError:
  from verify_lib import verify_receipt_obj, VerifyConfig

def main():
  import argparse
  ap = argparse.ArgumentParser()
  ap.add_argument("receipt", help="path to receipt.json")
  ap.add_argument("--crl", default=None, help="path to active CRL json (optional)")
  ap.add_argument("--time-window", type=int, default=300, help="seconds")
  args = ap.parse_args()

  r = json.load(open(args.receipt, "r", encoding="utf-8"))
  cfg = VerifyConfig(time_window_seconds=args.time_window, replay_db_path="conformance/state/seen_nonces.json", crl_path=args.crl)

  ok, code = verify_receipt_obj(r, cfg)
  if ok:
    print("PASS")
    raise SystemExit(0)
  print(f"FAIL: {code}")
  raise SystemExit(1)

if __name__ == "__main__":
  main()
