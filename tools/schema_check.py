import json
from pathlib import Path

def load_reason_enum():
  s=json.loads(Path("schemas/receipt.v0.1.json").read_text(encoding="utf-8"))
  enum = s["properties"]["decision"]["properties"]["reason_code"].get("enum")
  return set(enum or [])

def check_reason_code(receipt: dict):
  enum = load_reason_enum()
  rc = (receipt.get("decision") or {}).get("reason_code")
  if not rc:
    return False, "SVS_POLICY_VIOLATION"
  if rc not in enum:
    return False, "SVS_POLICY_VIOLATION"
  return True, "PASS"
