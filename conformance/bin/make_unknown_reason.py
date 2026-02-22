#!/usr/bin/env python3
import json
import sys
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
  sys.path.insert(0, str(ROOT))

from tools.svs_crypto import utcnow, to_rfc3339

if len(sys.argv)!=3:
  print("Usage: make_unknown_reason.py <in_base_receipt.json> <out_receipt.json>")
  raise SystemExit(2)

r=json.load(open(sys.argv[1],"r",encoding="utf-8"))
# Remove signature to re-sign later
r.pop("signature", None)
r["receipt_id"]=f"r-unknown-{uuid.uuid4()}"
r["issued_at"]=to_rfc3339(utcnow())
r["nonce"]="n-unknown-12345"
r["decision"]["reason_code"]="SVS_NOT_A_REAL_CODE"
json.dump(r, open(sys.argv[2],"w",encoding="utf-8"), indent=2, ensure_ascii=False)
print("OK", sys.argv[2])
