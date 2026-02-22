#!/usr/bin/env python3
import base64, json, sys
if len(sys.argv)!=2:
  print("Usage: receipt_to_b64.py <receipt.json>", file=sys.stderr)
  raise SystemExit(2)
obj=json.load(open(sys.argv[1],"r",encoding="utf-8"))
raw=json.dumps(obj, ensure_ascii=False, separators=(",",":")).encode("utf-8")
print(base64.b64encode(raw).decode("ascii"))
