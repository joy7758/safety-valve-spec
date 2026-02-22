import argparse
import json

from . import reason_codes as R
from .crypto import b64d
from .verify import verify_attestation, verify_receipt


def load_root_pk(args):
  if args.root_pk_b64:
    return b64d(args.root_pk_b64)
  if args.root_pk_file:
    return b64d(open(args.root_pk_file, "r", encoding="utf-8").read().strip())
  raise SystemExit("Provide --root-pk-b64 or --root-pk-file (base64 raw Ed25519 pubkey)")


def main():
  ap = argparse.ArgumentParser(prog="svs-verify")
  sub = ap.add_subparsers(dest="cmd", required=True)

  r = sub.add_parser("receipt", help="verify an SVS receipt")
  r.add_argument("path")
  r.add_argument("--root-kid", required=True)
  r.add_argument("--root-pk-b64", default=None)
  r.add_argument("--root-pk-file", default=None)
  r.add_argument("--crl", default=None)
  r.add_argument("--time-window", type=int, default=300)

  a = sub.add_parser("attestation", help="verify an SVS compat attestation")
  a.add_argument("path")
  a.add_argument("--root-pk-b64", default=None)
  a.add_argument("--root-pk-file", default=None)

  args = ap.parse_args()

  root_pk = load_root_pk(args)

  if args.cmd == "receipt":
    receipt = json.load(open(args.path, "r", encoding="utf-8"))
    crl = json.load(open(args.crl, "r", encoding="utf-8")) if args.crl else None
    ok, code = verify_receipt(
      receipt,
      root_pk_raw=root_pk,
      root_kid=args.root_kid,
      time_window_seconds=args.time_window,
      crl=crl,
      replay_db={},
    )
    if ok:
      print("PASS")
      return 0
    print(f"FAIL: {code}")
    return 1

  if args.cmd == "attestation":
    att = json.load(open(args.path, "r", encoding="utf-8"))
    ok, code = verify_attestation(att, root_pk_raw=root_pk)
    if ok:
      print("PASS")
      return 0
    print(f"FAIL: {code}")
    return 1

  print("FAIL: UNKNOWN_CMD")
  return 2


if __name__ == "__main__":
  raise SystemExit(main())
